import logging
from fastapi import (APIRouter, status, Depends, 
                     HTTPException, BackgroundTasks)
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from service import AuthService
from schema import (UserCreate, UserLogin, 
                    PasswordResetRequest, PasswordResetConfirm)
from db.main import get_session
from db.models import User
from config import Config
from dependencies import (RefreshTokenBearer, get_current_user, 
                          RoleChecker, AccessTokenBearer)
from db.mongo import add_jti_to_blocklist
from user.service import UserService
from mail import create_message, mail
from .utils import (create_url_safe_token, decode_url_safe_token, verify_password, 
                    create_access_tokens, generate_password_hash)
from datetime import timedelta, datetime

REFRESH_TOKEN_EXPIRY = 5
ACCESS_TOKEN_EXPIRY = 1

auth_router = APIRouter()
auth_service = AuthService()
user_service = UserService()

role_checker = RoleChecker(["admin", "user"])

async def send_email(message):
    await mail.send_message(message)

@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    try:
        email = user_data.email
        user_exists = await auth_service.user_exists(email, session)
        if user_exists:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User with email {email} already exists.",
            )
        new_user = await auth_service.create_user(user_data, session)
        return {
            "message": "Account Created! Check email to verify your account",
            "user": new_user,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await session.close()

@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    user_login_data: UserLogin, session: AsyncSession = Depends(get_session)
):
    try:
        email = user_login_data.email
        password = user_login_data.password

        user = await auth_service.get_user_by_email(email, session)
        if user is not None:
            password_valid = verify_password(password, user.password_hash)

            if password_valid:
                access_token = create_access_tokens(
                    user_data={
                        "email": user.email,
                        "user_uid": str(user.user_id),
                        "role": user.role,
                    },
                    expiry=timedelta(days=ACCESS_TOKEN_EXPIRY)
                )

                refresh_token = create_access_tokens(
                    user_data={
                        "email": user.email,
                        "user_uid": str(user.user_id),
                    },
                    refresh=True,
                    expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
                )
                return JSONResponse(
                    content={
                        "message": "Login Successful",
                        "access token": access_token,
                        "refresh token": refresh_token,
                        "user": {
                            "email": user.email,
                            "uid": str(user.user_id),
                            "username": user.name,
                        },
                    }
                )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Email or Password",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await session.close()

# @auth_router.post("/google", status_code=status.HTTP_200_OK)
# async def google(id_token: str, session: AsyncSession = Depends(get_session)):
#     try:
#         decoded_token = auth.verify_id_token(id_token)
#         uid = decoded_token['uid']
#         email = decoded_token['email']
#         name = decoded_token.get('name')
#         picture = decoded_token.get('picture')

#         user = await user_service.get_user_by_email(email, session)

#         if not user:
#             new_user_data = {
#                 "email": email,
#                 "username": name,
#                 "avatar_url": picture,
#                 "password_hash": "firebase_user",
#                 "is_verified": True,
#                 "firebase_uid": uid,
#             }
#             user = await user_service.create_user(User(**new_user_data), session)

#         access_token = create_access_tokens(
#             user_data={"email": user.email, "user_uid": str(user.id), "role": user.role}
#         )
#         refresh_token = create_access_tokens(
#             user_data={"email": user.email, "user_uid": str(user.id)},
#             refresh=True,
#             expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
#         )
#         return JSONResponse(
#             content={
#                 "message": "Login Successful",
#                 "access token": access_token,
#                 "refresh token": refresh_token,
#                 "user": {"email": user.email, "uid": str(user.id), "username": user.username},
#             }
#         )
#     except auth.InvalidIdTokenError:
#         raise HTTPException(status_code=401, detail="Invalid ID token")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Firebase login failed: {e}")
#     finally:
#         await session.close()

@auth_router.post("/reset-password/request")
async def password_reset_request(email_data: PasswordResetRequest, background_tasks: BackgroundTasks):
    email = email_data.email

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"

    html_message = f"""
    <h1>Reset Your Password</h1>
    <p>Please click this <a href="{link}">link</a> to Reset Your Password</p>
    """
    subject = "Reset Your Password"

    message = create_message(recipients=[email], subject=subject, body=html_message)

    background_tasks.add_task(send_email, message)

    return JSONResponse(
        content={
            "message": "Please check your email for instructions to reset your password",
        },
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/reset-password/confirm")
async def reset_account_password(
    token: str,
    passwords: PasswordResetConfirm,
    session: AsyncSession = Depends(get_session),
):
    try:
        new_password = passwords.new_password
        confirm_password = passwords.confirm_new_password

        if new_password != confirm_password:
            raise HTTPException(
                detail="Passwords do not match", status_code=status.HTTP_400_BAD_REQUEST
            )

        token_data = decode_url_safe_token(token)
        user_email = token_data.get("email")

        if user_email:
            user = await auth_service.get_user_by_email(user_email, session)
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            passwd_hash = generate_password_hash(new_password)
            await user_service.update_user(user, {"password_hash": passwd_hash}, session)

            return JSONResponse(
                content={"message": "Password reset Successfully"},
                status_code=status.HTTP_200_OK,
            )

        return JSONResponse(
            content={"message": "Error occurred during password reset."},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await session.close()

@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    try:
        expiry_timestamp = token_details['exp']
        if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
            new_access_token = create_access_tokens(user_data=token_details['user'])
            return JSONResponse(content={"access_token": new_access_token})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or Expired Token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details["jti"]
    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={"message": "Logged out Successfully"},
        status_code=status.HTTP_200_OK,
    )


@auth_router.get("/me")
async def get_current_user(
    user: User = Depends(get_current_user),
    _: bool = Depends(role_checker),
    session: AsyncSession = Depends(get_session),
):
    try:
        return user
    except Exception as e:
        logging.error(f"Error fetching current user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        await session.close()


import logging
import requests
from fastapi import (APIRouter, status, Depends, 
                     HTTPException, BackgroundTasks)
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from .service import AuthService
from .schema import (UserCreate, UserLogin, UserGoogleAuth,
                    PasswordResetRequest, PasswordResetConfirm)
from db.main import get_session
from db.models import User, UserPlan, EmailPreferences, UserStatus
from config import Config
from .dependencies import (RefreshTokenBearer, get_current_user, 
                          RoleChecker, AccessTokenBearer)
from db.mongo import add_jti_to_blocklist
from user.service import UserService
from mail import send_mailgun_email
from .utils import (create_url_safe_token, decode_url_safe_token, verify_password, 
                    create_access_tokens, generate_password_hash)
from datetime import timedelta, datetime
from google.oauth2 import id_token

REFRESH_TOKEN_EXPIRY = 7
ACCESS_TOKEN_EXPIRY = 1

GOOGLE_CLIENT_ID = Config.GOOGLE_CLIENT_ID

auth_router = APIRouter()
auth_service = AuthService()
user_service = UserService()

role_checker = RoleChecker(["admin", "user"])

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
        # Create default email preferences
        email_prefs = EmailPreferences(
            user_id=new_user.user_id,
            updates=True,
            tips=True,
            security=True,
            newsletter=False,
        )
        session.add(email_prefs)
        session.commit()
        return {
            "message": "Account Created!",
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
                if user.status == UserStatus.BANNED:
                    # Check if user is banned
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Your account has been suspended. Please contact support.",
                    )
                else:
                    # Update user's last login time
                    user.updated_at = datetime.utcnow()
                    session.commit()
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

# Google Sign-In endpoint
@auth_router.post("/api/auth/google")
async def google_signin(google_token: UserGoogleAuth, session: AsyncSession = Depends(get_session)):
    try:
        # Verify the Google token
        idinfo = id_token.verify_oauth2_token(
            google_token.token, requests.Request(), GOOGLE_CLIENT_ID
        )

        # Extract user information from the token
        email = idinfo.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not found in Google token",
            )

        # Check if the email is verified
        if not idinfo.get("email_verified", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not verified with Google",
            )

        # Get user information
        name = idinfo.get("name", "")
        picture = idinfo.get("picture", "")

        # Check if user exists in database
        user = session.query(User).filter(User.email == email).first()

        if not user:
            # Create new user if not exists
            user = User(
                email=email,
                name=name,
                avatar_url=picture,
                plan=UserPlan.FREE,
                status="active",
                role="user",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(user)
            session.commit()
            session.refresh(user)

            # Create default email preferences
            email_prefs = EmailPreferences(
                user_id=user.user_id,
                updates=True,
                tips=True,
                security=True,
                newsletter=False,
            )
            session.add(email_prefs)
            session.commit()
        elif user.status == "banned":
            # Check if user is banned
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account has been suspended. Please contact support.",
            )
        else:
            # Update user's last login time
            user.updated_at = datetime.utcnow()
            session.commit()

        # Create access token
        access_token_expires =timedelta(days=ACCESS_TOKEN_EXPIRY)
        access_token = create_access_tokens(
            data={"sub": str(user.user_id)}, expires_delta=access_token_expires
        )

        # Return user information and token
        return {
            "user_id": str(user.user_id),
            "name": user.name,
            "email": user.email,
            "token": access_token,
            "plan": user.plan,
        }

    except ValueError:
        # Invalid token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        )
    except Exception as e:
        # Other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing Google sign-in: {str(e)}",
        )

@auth_router.post("/reset-password/request")
async def password_reset_request(email_data: PasswordResetRequest, background_tasks: BackgroundTasks):
    email = email_data.email

    # Generate token and link
    token = create_url_safe_token({"email": email})
    link = f"https://{Config.DOMAIN}/auth/reset-password/confirm/{token}"

    # Create HTML content
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .button {{
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 20px 0;
                cursor: pointer;
                border-radius: 4px;
            }}
        </style>
    </head>
    <body>
        <h1>Password Reset Request</h1>
        <p>Hello from Engineering Support AI Chatbot!</p>
        <p>We received a request to reset your password. Click the button below to proceed:</p>
        <a href="{link}" class="button">Reset Password</a>
        <p>If you didn't request this, please ignore this email.</p>
        <p>The link will expire in 24 hours.</p>
    </body>
    </html>
    """

    # Queue email sending
    background_tasks.add_task(
        send_mailgun_email,
        recipients=[email],
        subject="Password Reset Instructions",
        html=html_message
    )

    return JSONResponse(
        content={
            "message": "Password reset instructions sent to your email",
            "status": "success"
        },
        status_code=status.HTTP_200_OK
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


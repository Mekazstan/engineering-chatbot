from fastapi import (APIRouter, Depends, UploadFile, 
    File, HTTPException, status, Query
)
from fastapi.responses import JSONResponse
from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from .service import DocumentService
from .schema import (DocumentResponse, DocumentListResponse,
    DocumentStatusResponse, DocumentContentResponse
)
from db.main import get_session
from db.models import User, DocumentStatus
from auth.dependencies import get_current_user
import logging

docs_router = APIRouter()
document_service = DocumentService()

@docs_router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Upload a document for processing"""
    try:
        file_data = await file.read()
        result = await document_service.upload_document(
            user_id=current_user.user_id,
            file_data=file_data,
            filename=file.filename,
            file_type=file.content_type,
            background_tasks=background_tasks,
            session=session
        )
        
        document = result["document"]
        task_id = result["task_id"]
        
        return {
            "document_id": document.document_id,
            "name": document.name,
            "size": document.size,
            "upload_date": document.upload_date,
            "status": document.status,
            "task_id": task_id
        }
        
    except Exception as e:
        logging.error(f"Document upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document"
        )
        
@docs_router.get("/tasks/{task_id}/status")
async def get_task_status(
    task_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Check processing status"""
    progress = await DocumentService().get_processing_progress(task_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task_id,
        "status": progress["status"],
        "progress": progress["progress"],
        "document_id": progress.get("document_id")
    }

@docs_router.get("/all", response_model=DocumentListResponse)
async def get_documents(
    status: Optional[DocumentStatus] = Query(None),
    limit: int = Query(50, gt=0),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get list of user's documents"""
    try:
        documents, total = await document_service.get_user_documents(
            user_id=current_user.user_id,
            session=session,
            status=status,
            limit=limit,
            offset=offset
        )
        
        return {
            "documents": [
                {
                    "document_id": doc.document_id,
                    "name": doc.name,
                    "size": doc.size,
                    "upload_date": doc.upload_date,
                    "status": doc.status.value,
                    "url": doc.s3_url
                }
                for doc in documents
            ],
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset
            }
        }
        
    except Exception as e:
        logging.error(f"Failed to get documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve documents"
        )

@docs_router.get("/{document_id}", response_model=DocumentContentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get details of a specific document"""
    try:
        document = await document_service.get_document(
            document_id=document_id,
            user_id=current_user.user_id,
            session=session
        )
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
            
        # Get content preview (implement your logic)
        content_preview = await _get_content_preview(document.s3_url)
        
        return {
            "document_id": document.document_id,
            "name": document.name,
            "size": document.size,
            "upload_date": document.upload_date,
            "status": document.status,
            "url": document.s3_url,
            "content_preview": content_preview,
            "pages": document.pages,
            "file_type": document.file_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to get document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document"
        )

@docs_router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Delete a document"""
    try:
        success = await document_service.delete_document(
            document_id=document_id,
            user_id=current_user.user_id,
            session=session
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
            
        return JSONResponse(
            content={"message": "Document deleted successfully"},
            status_code=status.HTTP_200_OK
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to delete document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )

@docs_router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Check processing status of a document"""
    try:
        status_info = await document_service.get_document_status(
            document_id=document_id,
            user_id=current_user.user_id,
            session=session
        )
        
        if not status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
            
        return {
            "document_id": document_id,
            "status": status_info["status"],
            "progress": status_info["progress"],
            "message": status_info["message"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to get document status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get document status"
        )

async def _get_content_preview(s3_url: str) -> str:
    """Helper to get first few paragraphs of document content"""
    # Implement your logic to extract preview from document
    return "Sample preview text..."

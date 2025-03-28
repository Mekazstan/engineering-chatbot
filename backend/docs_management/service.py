import asyncio
import os
import uuid
import logging
from datetime import datetime
from typing import Optional, List, Dict
from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, update
from db.models import Document, DocumentStatus
import boto3
from botocore.exceptions import ClientError
from config import Config

processing_tasks: Dict[str, Dict[str, int]] = {}

class DocumentService:
    def __init__(self):
        # Initialize B2 client
        self.b2 = boto3.client(
            's3',
            endpoint_url=Config.B2_ENDPOINT_URL,
            aws_access_key_id=Config.B2_APPLICATION_KEY_ID,
            aws_secret_access_key=Config.B2_APPLICATION_KEY
        )
        self.bucket_name = Config.B2_BUCKET_NAME
        self.processing_tasks = processing_tasks

    async def upload_document(
        self, 
        user_id: int, 
        file_data: bytes,
        filename: str,
        file_type: str,
        background_tasks: BackgroundTasks,
        session: AsyncSession
    ) -> Document:
        """Handle document upload to Backblaze B2 and processing initiation"""
        try:
            # Generate unique file path
            file_path = f"user_{user_id}/{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
            
            # Upload to Backblaze B2
            b2_url = await self._upload_to_b2(file_data, file_path, file_type)
            
            # Create document record
            document = Document(
                user_id=user_id,
                name=filename,
                size=len(file_data),
                file_type=file_type,
                s3_url=b2_url,
                status=DocumentStatus.UPLOADED,
                upload_date=datetime.utcnow()
            )
            
            session.add(document)
            await session.commit()
            await session.refresh(document)
            
            # Start processing task
            task_id = await self._start_processing_task(
                document.document_id,
                background_tasks,
                session
            )
            
            return {
                "document": document, 
                "task_id": task_id
            }
            
        except Exception as e:
            logging.error(f"Error uploading document: {str(e)}")
            await session.rollback()
            raise

    async def _upload_to_b2(self, file_data: bytes, file_path: str, content_type: str) -> str:
        """Upload file to Backblaze B2 and return public URL"""
        try:
            self.b2.put_object(
                Bucket=self.bucket_name,
                Key=file_path,
                Body=file_data,
                ContentType=content_type
            )
            
            # Return public URL (Backblaze B2 format)
            return f"{self.b2.meta.endpoint_url}/{self.bucket_name}/{file_path}"
            
        except ClientError as e:
            logging.error(f"B2 upload failed: {str(e)}")
            raise Exception("Failed to upload document to storage")

    async def _delete_from_b2(self, file_url: str) -> bool:
        """Delete file from Backblaze B2"""
        try:
            # Extract the key from the URL
            key = file_url.split(f"{self.bucket_name}/")[-1]
            
            self.b2.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
            
        except ClientError as e:
            logging.error(f"B2 deletion failed: {str(e)}")
            return False

    # Modified delete_document to use B2
    async def delete_document(
        self,
        document_id: int,
        user_id: int,
        session: AsyncSession
    ) -> bool:
        """Delete document from B2 and database"""
        try:
            document = await self.get_document(document_id, user_id, session)
            if not document:
                return False
                
            # Delete from Backblaze B2
            success = await self._delete_from_b2(document.s3_url)
            if not success:
                raise Exception("Failed to delete file from storage")
            
            # Delete from database
            await session.delete(document)
            await session.commit()
            
            return True
            
        except Exception as e:
            logging.error(f"Error deleting document: {str(e)}")
            await session.rollback()
            raise

    # The following methods remain unchanged as they don't interact with storage
    async def get_user_documents(
        self,
        user_id: int,
        session: AsyncSession,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[Document], int]:
        """Get paginated list of user's documents"""
        try:
            query = select(Document).where(Document.user_id == user_id)
            
            if status:
                query = query.where(Document.status == status)
                
            total_query = select(func.count()).select_from(query.subquery())
            total = (await session.execute(total_query)).scalar_one()
            
            query = query.offset(offset).limit(limit)
            result = await session.execute(query)
            documents = result.scalars().all()
            
            return documents, total
            
        except Exception as e:
            logging.error(f"Error getting documents: {str(e)}")
            raise

    async def get_document(
        self,
        document_id: int,
        user_id: int,
        session: AsyncSession
    ) -> Optional[Document]:
        """Get single document with access control"""
        try:
            result = await session.execute(
                select(Document)
                .where(Document.document_id == document_id)
                .where(Document.user_id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logging.error(f"Error getting document: {str(e)}")
            raise

    async def get_document_status(
        self,
        document_id: int,
        user_id: int,
        session: AsyncSession
    ) -> Optional[dict]:
        """Get processing status of a document"""
        try:
            document = await self.get_document(document_id, user_id, session)
            if not document:
                return None
                
            return {
                "status": document.status,
                "progress": self._get_processing_progress(document_id),
                "message": None
            }
        except Exception as e:
            logging.error(f"Error getting document status: {str(e)}")
            raise

    async def _start_processing_task(
        self, 
        document_id: int,
        background_tasks: BackgroundTasks,
        session: AsyncSession
    ) -> str:
        """Start document processing as a background task"""
        try:
            # Create a unique task ID
            task_id = str(uuid.uuid4())
            
            # Initialize progress tracking
            self.processing_tasks[task_id] = {
                "document_id": document_id,
                "progress": 0,
                "status": "queued"
            }
            
            # Add to background tasks
            background_tasks.add_task(
                self._process_document_task,
                document_id=document_id,
                task_id=task_id,
                session=session
            )
            
            return task_id
            
        except Exception as e:
            logging.error(f"Error starting processing task: {str(e)}")
            raise
        
    async def _process_document_task(
        self,
        document_id: int,
        task_id: str,
        session: AsyncSession
    ):
        """Background task for document processing"""
        try:
            # Update status to processing
            self._update_task_progress(task_id, 10, "processing")
            
            # Get document from database
            document = await self.get_document(document_id, session=session)
            if not document:
                self._update_task_progress(task_id, 0, "failed")
                return

            # Simulate processing steps (replace with actual logic)
            await self._simulate_processing_steps(document_id, task_id, session)
            
            # Mark as completed
            self._update_task_progress(task_id, 100, "completed")
            
            # Update database status
            await session.execute(
                update(Document)
                .where(Document.document_id == document_id)
                .values(
                    status=DocumentStatus.COMPLETED,
                    processed_date=datetime.utcnow()
                )
            )
            await session.commit()
            
        except Exception as e:
            logging.error(f"Document processing failed: {str(e)}")
            self._update_task_progress(task_id, 0, "failed")
            
            # Update database status
            await session.execute(
                update(Document)
                .where(Document.document_id == document_id)
                .values(status=DocumentStatus.FAILED)
            )
            await session.commit()
            
    async def _simulate_processing_steps(
        self,
        document_id: int,
        task_id: str,
        session: AsyncSession
    ):
        """Simulate processing steps with progress updates"""
        steps = [
            ("Downloading file", 20),
            ("Extracting text", 40),
            ("Generating embeddings", 60),
            ("Storing in vector DB", 80),
            ("Finalizing", 95)
        ]
        
        for step_name, progress in steps:
            logging.info(f"Processing document {document_id}: {step_name}")
            await asyncio.sleep(2)  # Simulate work
            self._update_task_progress(task_id, progress, "processing")

    def _update_task_progress(
        self,
        task_id: str,
        progress: int,
        status: str
    ):
        """Update task progress in shared state"""
        if task_id in self.processing_tasks:
            self.processing_tasks[task_id]["progress"] = progress
            self.processing_tasks[task_id]["status"] = status

    async def get_processing_progress(
        self,
        task_id: str
    ) -> Optional[Dict[str, int]]:
        """Get current processing progress"""
        return self.processing_tasks.get(task_id)
    
"""
Document Service — Handles document uploads for RAG ingestion.

NOTE: This is the API-layer placeholder. It returns mock responses so the API
works end-to-end. The real document processing (PDF extraction, chunking,
embedding, ChromaDB storage) will be implemented in a later phase.

Reference: architecture_final.md §8.2 (Upload Document Endpoint)
"""
import uuid
from typing import Optional


class DocumentService:
    """
    Business logic for document upload and processing.
    """

    async def upload(
        self,
        filename: str,
        content: bytes,
        size_bytes: int,
        mpn: Optional[str] = None,
    ) -> dict:
        """
        Upload and process a technical document.
        
        This is the placeholder implementation. It validates basic file
        constraints and returns a mock processing response.
        
        Args:
            filename: Name of the uploaded file.
            content: Raw file bytes (unused in mock).
            size_bytes: Size of the file in bytes.
            mpn: Optional MPN to associate with the document.
        
        Returns:
            dict: Mock upload response with document_id and status.
        
        Raises:
            ValueError: If the file is empty or unsupported.
        """
        if size_bytes == 0:
            raise ValueError("Uploaded file is empty.")
        if not filename.lower().endswith(".pdf"):
            # Allow PDFs and common text formats; reject everything else.
            allowed = (".pdf", ".txt", ".csv", ".json")
            if not any(filename.lower().endswith(ext) for ext in allowed):
                raise ValueError(
                    "Unsupported file type. Upload a PDF, TXT, CSV, or JSON file."
                )

        document_id = f"doc_{uuid.uuid4().hex[:12]}"

        # Mock chunk count derived from file size.
        chunks_created = max(1, size_bytes // 2048)

        return {
            "document_id": document_id,
            "filename": filename,
            "size_bytes": size_bytes,
            "chunks_created": chunks_created,
            "status": "processed",
            "mpn": mpn,
        }


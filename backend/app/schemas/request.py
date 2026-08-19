"""
Pydantic schemas for API request validation.

Reference: architecture_final.md §8.2 (Request/Response Schemas)
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any


class ProductRequest(BaseModel):
    """Request schema for POST /api/v1/analyze."""
    mpn: str = Field(..., min_length=1, max_length=100, description="Manufacturer Part Number")
    brand: str = Field(..., min_length=1, max_length=200, description="Brand name")
    description: str = Field(..., min_length=1, max_length=1000, description="Short product description")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Analysis options")

    @field_validator("mpn")
    @classmethod
    def normalize_mpn(cls, v: str) -> str:
        """Normalize MPN to uppercase and strip whitespace."""
        return v.strip().upper()

    @field_validator("brand")
    @classmethod
    def normalize_brand(cls, v: str) -> str:
        """Strip whitespace from brand name."""
        return v.strip()

    @field_validator("description")
    @classmethod
    def normalize_description(cls, v: str) -> str:
        """Strip whitespace from description."""
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "mpn": "SN74LS00N",
                "brand": "Texas Instruments",
                "description": "Quad 2-input NAND gate",
                "options": {
                    "include_web_search": True,
                    "confidence_threshold": 0.7
                }
            }
        }


class DocumentUploadRequest(BaseModel):
    """Request schema for POST /api/v1/upload-document."""
    mpn: Optional[str] = Field(default=None, max_length=100, description="Optional MPN to associate with document")

    class Config:
        json_schema_extra = {
            "example": {
                "mpn": "SN74LS00N"
            }
        }


class HistoryQueryParams(BaseModel):
    """Query parameters for GET /api/v1/history."""
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=10, ge=1, le=100, description="Items per page")
    sort: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")

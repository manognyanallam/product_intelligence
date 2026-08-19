"""
History Service — Provides paginated analysis history.

NOTE: This is the API-layer placeholder. It returns mock responses so the API
works end-to-end. The real history will be read from ChromaDB in a later phase.

Reference: architecture_final.md §8.2 (History Endpoint)
"""
from typing import List

from app.schemas.response import ProductHistory, HistoryResponse


class HistoryService:
    """
    Business logic for retrieving analysis history.
    """

    def __init__(self) -> None:
        """Initialize with mock history data."""
        # In a real implementation, this would query the ChromaDB product_cache.
        self._mock_history: List[ProductHistory] = [
            ProductHistory(
                product_id="prod_sample_001",
                mpn="SN74LS00N",
                brand="Texas Instruments",
                description="Quad 2-input NAND gate",
                overall_confidence=0.94,
                category="Semiconductors > Logic ICs > NAND Gates",
                timestamp="2025-01-15T10:30:00Z",
                status="completed",
            ),
            ProductHistory(
                product_id="prod_sample_002",
                mpn="LM358N",
                brand="Texas Instruments",
                description="Dual operational amplifier",
                overall_confidence=0.89,
                category="Semiconductors > Amplifiers > Op-Amps",
                timestamp="2025-01-15T09:15:00Z",
                status="completed",
            ),
            ProductHistory(
                product_id="prod_sample_003",
                mpn="ATMEGA328P-PU",
                brand="Microchip Technology",
                description="8-bit AVR microcontroller with 32KB flash",
                overall_confidence=0.91,
                category="Semiconductors > Microcontrollers > AVR",
                timestamp="2025-01-14T16:45:00Z",
                status="completed",
            ),
        ]

    async def get_history(
        self, page: int = 1, limit: int = 10, sort: str = "desc"
    ) -> HistoryResponse:
        """
        Retrieve paginated analysis history.
        
        Args:
            page: Page number (1-indexed).
            limit: Number of items per page (max 100).
            sort: Sort order by timestamp: "asc" or "desc".
        
        Returns:
            HistoryResponse: Paginated history entries.
        """
        history = list(self._mock_history)

        # Sort by timestamp.
        if sort == "asc":
            history.sort(key=lambda h: h.timestamp)
        else:
            history.sort(key=lambda h: h.timestamp, reverse=True)

        # Paginate.
        start = (page - 1) * limit
        end = start + limit
        page_items = history[start:end]

        return HistoryResponse(
            results=page_items,
            total=len(history),
            page=page,
            limit=limit,
        )


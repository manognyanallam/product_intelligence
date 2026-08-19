"""
Seed Data — Initial product catalog data for ChromaDB.

This module provides seed data to populate the product_cache collection
with initial product information. This enables meaningful RAG results
even before users upload their own documents.

Reference: architecture_final.md §7 (Database Design)
"""
from typing import List, Dict, Any


# Sample seed products for development and testing
SEED_PRODUCTS: List[Dict[str, Any]] = [
    {
        "mpn": "SN74LS00N",
        "brand": "Texas Instruments",
        "category": "Semiconductors > Logic ICs > NAND Gates",
        "description": "Quad 2-Input Positive-NAND Gate",
        "specifications": {
            "technology": "LS (Low-Power Schottky)",
            "supply_voltage_min": "4.75V",
            "supply_voltage_max": "5.25V",
            "operating_temp_min": "0°C",
            "operating_temp_max": "70°C",
            "propagation_delay": "15ns",
            "package_type": "PDIP-14",
            "logic_family": "74LS",
        },
    },
    {
        "mpn": "LM358N",
        "brand": "Texas Instruments",
        "category": "Semiconductors > Amplifiers > Operational Amplifiers",
        "description": "Dual Operational Amplifier",
        "specifications": {
            "supply_voltage_min": "3V",
            "supply_voltage_max": "32V",
            "bandwidth": "1.1MHz",
            "slew_rate": "0.6V/µs",
            "package_type": "PDIP-8",
            "channels": 2,
        },
    },
    {
        "mpn": "ATMEGA328P-PU",
        "brand": "Microchip Technology",
        "category": "Semiconductors > Microcontrollers > AVR",
        "description": "8-bit AVR Microcontroller with 32KB Flash",
        "specifications": {
            "core": "AVR",
            "flash_memory": "32KB",
            "ram": "2KB",
            "eeprom": "1KB",
            "clock_speed": "20MHz",
            "package_type": "PDIP-28",
            "io_pins": 23,
        },
    },
    {
        "mpn": "1N4148",
        "brand": "ON Semiconductor",
        "category": "Semiconductors > Diodes > Switching Diodes",
        "description": "Small Signal Fast Switching Diode",
        "specifications": {
            "type": "Switching Diode",
            "reverse_voltage": "100V",
            "forward_current": "300mA",
            "forward_voltage": "1V",
            "reverse_recovery_time": "4ns",
            "package_type": "DO-35",
        },
    },
    {
        "mpn": "IRFZ44N",
        "brand": "Infineon Technologies",
        "category": "Semiconductors > Transistors > MOSFETs",
        "description": "N-Channel Power MOSFET",
        "specifications": {
            "type": "N-Channel MOSFET",
            "drain_source_voltage": "55V",
            "continuous_drain_current": "49A",
            "rds_on": "0.0175Ω",
            "package_type": "TO-220",
            "gate_threshold_voltage": "2V",
        },
    },
]


async def seed_database():
    """
    Seed the ChromaDB product_cache with initial product data.
    
    This should be called during application startup.
    Each product is embedded and stored in the product_cache collection.
    """
    # TODO: Implement seeding logic
    # TODO: Check if seed data already exists
    # TODO: Generate embeddings for each product
    # TODO: Store in ChromaDB product_cache collection
    pass


async def get_seed_product(mpn: str) -> Dict[str, Any]:
    """
    Get a seed product by MPN.
    
    Args:
        mpn: Manufacturer Part Number
    
    Returns:
        Product data if found, None otherwise
    """
    mpn = mpn.upper().strip()
    for product in SEED_PRODUCTS:
        if product["mpn"] == mpn:
            return product
    return None

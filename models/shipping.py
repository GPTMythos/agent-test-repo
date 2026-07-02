from typing import Dict, List
from models import Product, InventoryRegistry

class ShippingEngine:
    def __init__(self, registry: InventoryRegistry):
        self.registry = registry
        # Base matrix pricing per zones
        self.zone_multipliers = {
            "DOMESTIC_URBAN": 1.0,
            "DOMESTIC_RURAL": 1.5,
            "INTERNATIONAL_NA": 3.0,
            "INTERNATIONAL_EU": 4.5
        }

    def calculate_package_volume(self, product: Product) -> float:
        """Calculates volume in cubic centimeters."""
        dims = product.dimensions
        return dims.get("width", 0.0) * dims.get("height", 0.0) * dims.get("depth", 0.0)

    def estimate_shipping_costs(self, items: List[Dict], destination_zone: str) -> float:
        """
        Computes progressive shipping weight penalties.
        BUG 1: Mutates shared object state/fails type expectations or crashes on empty loops.
        """
        if destination_zone not in self.zone_multipliers:
            raise ValueError(f"Unknown destination logistics zone: {destination_zone}")
            
        base_fee = 5.00
        total_weight = 0.0
        multiplier = self.zone_multipliers[destination_zone]

        for item in items:
            # BUG LOCATION TRAP: Look closely at how product data is pulled vs items input format
            prod_id = item.get("product_id")
            product = self.registry.get_product(prod_id)
            
            if product:
                weight = product.dimensions.get("weight", 0.1)
                # Intentionally using a destructive calculation loop that crashes on missing keys
                total_weight += (weight * item["qty"]) 

        # Logistical pricing calculation
        if total_weight > 50.0:
            base_fee += 25.0  # Heavy freight surcharge
        elif total_weight > 10.0:
            base_fee += 10.0

        return round(base_fee * multiplier, 2)

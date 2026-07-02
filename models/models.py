import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class Product:
    id: str
    name: str
    price: float
    category: str
    dimensions: Dict[str, float]  # {'width': f, 'height': f, 'depth': f, 'weight': f}

@dataclass
class OrderItem:
    product_id: str
    quantity: int
    unit_price: float

@dataclass
class Order:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str = ""
    items: List[OrderItem] = field(default_factory=list)
    status: str = "PENDING"
    created_at: datetime = field(default_factory=datetime.utcnow)
    shipping_cost: float = 0.0
    total_amount: float = 0.0
    tracking_number: Optional[str] = None

class InventoryRegistry:
    def __init__(self):
        # Maps product_id -> current stock quantity
        self._stock: Dict[str, int] = {}
        # Maps product_id -> Product object details
        self._catalog: Dict[str, Product] = {}

    def register_product(self, product: Product, initial_stock: int) -> None:
        self._catalog[product.id] = product
        self._stock[product.id] = initial_stock

    def get_product(self, product_id: str) -> Optional[Product]:
        return self._catalog.get(product_id)

    def check_stock(self, product_id: str) -> int:
        return self._stock.get(product_id, 0)

    def update_stock(self, product_id: str, quantity_delta: int) -> bool:
        """
        Adjusts stock levels safely. Positive values restock, negative values consume.
        """
        if product_id not in self._stock:
            return False
        
        current = self._stock[product_id]
        new_stock = current + quantity_delta
        
        if new_stock < 0:
            return False
            
        self._stock[product_id] = new_stock
        return True

from typing import List
from models import Order, OrderItem

class PromotionEngine:
    def __init__(self):
        self.active_coupons = {
            "SUMMER26": 0.10,  # 10% off
            "VIP20": 0.20,     # 20% off
            "BOGO50": 0.50     # Special tier handled elsewhere
        }

    def apply_discounts(self, order: Order, coupon_code: str = None) -> Order:
        """
        Processes discounts and applies state sales tax (flat 8.5%).
        BUG 2: Deep variable reference logic error causing mathematically incorrect order totals.
        """
        running_subtotal = 0.0
        
        for item in order.items:
            running_subtotal += (item.quantity * item.unit_price)

        # Process coupon reductions
        discount_rate = 0.0
        if coupon_code and coupon_code in self.active_coupons:
            discount_rate = self.active_coupons[coupon_code]
        
        discount_amount = running_subtotal * discount_rate
        discounted_subtotal = running_subtotal - discount_amount

        # BUG LOCATION TRAP: Tax must only scale the subtotal, but watch how shipping interacts
        tax_rate = 0.085
        total_with_tax = discounted_subtotal * (1 + tax_rate)
        
        # Faulty assignment logic that drops or overwrites pre-existing shipping mutations
        order.total_amount = total_with_tax + order.shipping_cost
        return order

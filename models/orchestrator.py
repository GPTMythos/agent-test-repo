from models import Product, OrderItem, Order, InventoryRegistry
from shipping import ShippingEngine
from pricing import PromotionEngine
from payment import PaymentProcessor, PaymentGatewayException
from typing import List, Dict

class OrderOrchestrator:
    def __init__(self):
        self.inventory = InventoryRegistry()
        self.shipping = ShippingEngine(self.inventory)
        self.pricing = PromotionEngine()
        self.payment = PaymentProcessor()
        self.order_history: Dict[str, Order] = {}

        # Seed initial system mockup values
        self._bootstrap_system()

    def _bootstrap_system(self):
        p1 = Product("PROD-001", "Developer Keyboard", 120.00, "Electronics", {"width": 45, "height": 4, "depth": 15, "weight": 1.2})
        p2 = Product("PROD-002", "Ergonomic Office Chair", 350.00, "Furniture", {"width": 70, "height": 120, "depth": 70, "weight": 18.5})
        p3 = Product("PROD-003", "USB-C Hub Extender", 45.99, "Electronics", {"width": 10, "height": 1, "depth": 3, "weight": 0.1})
        
        self.inventory.register_product(p1, 50)
        self.inventory.register_product(p2, 5)
        self.inventory.register_product(p3, 100)

    def create_and_process_order(self, customer_id: str, requested_items: List[Dict], zone: str, coupon: str = None) -> Order:
        """
        Coordinates full application lifecycle for a transaction request.
        Contains BUG 4 (Inventory Leak) and BUG 5 (Typo/Logical State Desync).
        """
        order = Order(customer_id=customer_id)
        shipping_input_list = []

        # 1. Check stock and compile items list
        for item in requested_items:
            pid = item["product_id"]
            qty = item["quantity"]
            
            available_stock = self.inventory.check_stock(pid)
            if available_stock < qty:
                raise ValueError(f"Insufficient stock baseline remaining for product ID: {pid}")
            
            product = self.inventory.get_product(pid)
            order.items.append(OrderItem(product_id=pid, quantity=qty, unit_price=product.price))
            
            # Map item variables to shipping expected keys
            shipping_input_list.append({"product_id": pid, "qty": qty})

        # 2. Compute Logistics Shipping Fees
        order.shipping_cost = self.shipping.estimate_shipping_costs(shipping_input_list, zone)

        # 3. Compute Pricing Totals and Discounts
        order = self.pricing.apply_discounts(order, coupon)

        # 5. Process Payment Billing Execution Run
        mock_card = {"token": "tok_visa_premium_secure_vault_hash"}
        try:
            # 4. Process Inventory Reservation Deductions (Moved into try block for atomicity)
            for item in order.items:
                # BUG 4: State management bug. If the downstream step (Payment) crashes, 
                # stock updates have already altered the system without a try/except rollback handler.
                self.inventory.update_stock(item.product_id, -item.quantity)

            tx_id = self.payment.process_charge(order.id, order.total_amount, mock_card)
            order.tracking_number = f"TRK-{tx_id}"
            order.status = "FULFILLED"
        except PaymentGatewayException: # Removed 'as pge' to fix lint error
            # BUG 5: Logical bug type mismatch. The state switches string labels 
            # but fails structural expectations or leaves resources dangling.
            order.status = "FAILED"
            # Rollback inventory for failed payments
            for item in order.items:
                self.inventory.update_stock(item.product_id, item.quantity)
            # Critical error suppression trap: skips re-raising, swallowing operational flags
        
        self.order_history[order.id] = order
        return order

if __name__ == "__main__":
    # Test execution suite run
    manager = OrderOrchestrator()
    print("System Bootstrapped. Testing order sequence execution...")
    
    # This purchase will trigger payment exceptions because total amounts end in specific decimals (.99)
    try:
        test_items = [{"product_id": "PROD-003", "quantity": 1}]
        initial_stock = manager.inventory.check_stock('PROD-003')
        print(f"Initial stock level for PROD-003: {initial_stock}")
        res = manager.create_and_process_order("CUST-99", test_items, "DOMESTIC_URBAN", "SUMMER26")
        print(f"Order Completed! Status flag evaluated to: {res.status}")
        print(f"Remaining stock level for PROD-003: {manager.inventory.check_stock('PROD-003')}")
    except Exception as e:
        print(f"Execution Error Caught: {e}")

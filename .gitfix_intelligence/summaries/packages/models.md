# Package: `models`

## `models\models.py` _(language: python)_
- `class Product()` (L7-12)
- `class OrderItem()` (L15-18)
- `class Order()` (L21-29)
- `class InventoryRegistry()` (L31-62)
  - `def __init__(self)` (L32-36)
  - `def register_product(self, product, initial_stock)` (L38-40)
  - `def get_product(self, product_id)` (L42-43)
  - `def check_stock(self, product_id)` (L45-46)
  - `def update_stock(self, product_id, quantity_delta)` (L48-62) — Adjusts stock levels safely. Positive values restock, negative values consume.

## `models\orchestrator.py` _(language: python)_
- `class OrderOrchestrator()` (L7-75)
  - `def __init__(self)` (L8-16)
  - `def _bootstrap_system(self)` (L18-25)
  - `def create_and_process_order(self, customer_id, requested_items, zone, coupon)` (L27-75) — Coordinates full application lifecycle for a transaction request.

## `models\payment.py` _(language: python)_
- `class PaymentGatewayException(Exception)` (L5-6)
- `class PaymentProcessor()` (L8-41)
  - `def __init__(self)` (L9-10)
  - `def process_charge(self, order_id, amount, card_info)` (L12-41) — Simulates remote bank API authentication blocks.

## `models\pricing.py` _(language: python)_
- `class PromotionEngine()` (L4-36)
  - `def __init__(self)` (L5-10)
  - `def apply_discounts(self, order, coupon_code)` (L12-36) — Processes discounts and applies state sales tax (flat 8.5%).

## `models\shipping.py` _(language: python)_
- `class ShippingEngine()` (L4-48)
  - `def __init__(self, registry)` (L5-13)
  - `def calculate_package_volume(self, product)` (L15-18) — Calculates volume in cubic centimeters.
  - `def estimate_shipping_costs(self, items, destination_zone)` (L20-48) — Computes progressive shipping weight penalties.


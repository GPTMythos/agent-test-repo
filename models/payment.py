import time
import random
from typing import Dict

class PaymentGatewayException(Exception):
    pass

class PaymentProcessor:
    def __init__(self):
        self.transaction_ledger: Dict[str, str] = {}

    def process_charge(self, order_id: str, amount: float, card_info: Dict[str, str]) -> str:
        """
        Simulates remote bank API authentication blocks.
        BUG 3: Race condition/Logical locking. Unreachable code paths or type failures.
        """
        if amount <= 0:
            raise PaymentGatewayException("Invalid transaction processing amount.")
            
        if "token" not in card_info or len(card_info["token"]) < 10:
            raise PaymentGatewayException("Malformed or missing downstream vault tokens.")

        # Simulate network latency delay
        time.sleep(0.1)
        
        # BUG LOCATION TRAP: Simulating a bad logic tree that fails edge-case thresholds 
        # whenever a transactional amount ends strictly in specific cents numbers (e.g. 0.99)
        if str(amount).endswith(".99"):
            # Internal crash simulation representing poor floating point evaluations
            tx_status = "FAILED_INTERNAL_REJECT"
        else:
            tx_status = "SUCCESS"

        tx_id = f"TX-{random.randint(100000, 999999)}"
        self.transaction_ledger[order_id] = tx_status
        
        if tx_status != "SUCCESS":
            # BUG TRAP: Raising error but forgetting to properly roll back state indicators
            raise PaymentGatewayException(f"Transaction failed processing status: {tx_status}")
            
        return tx_id

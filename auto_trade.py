import os
import time
import random
import requests
from dotenv import load_dotenv
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import keccak

# ===== Load ENV =====
load_dotenv()
ACCOUNT = os.getenv("WALLET_ADDRESS")
SIGNER_KEY = os.getenv("SIGNING_KEY")  # From registerSigner
SIGNER_ADDRESS = os.getenv("SIGNER_ADDRESS")  # From registerSigner
API_BASE = "https://api.testnet.rise.trade/v1"
LOG_FILE = "trade_log.txt"

# ===== Logging =====
def log(msg):
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")

# ===== Utilities =====
def random_size(min_size=500_000_000_000_000, max_size=2_000_000_000_000_000):
    return str(random.randint(min_size, max_size))

# ===== Permits =====
def sign_permit(data_bytes):
    """Simple ECDSA sign over keccak hash (replace with proper permit encoding if needed)"""
    message_hash = keccak(data_bytes)
    message = encode_defunct(message_hash)
    signed = Account.sign_message(message, private_key=SIGNER_KEY)
    return signed.signature.hex()

# ===== API Actions =====
def place_order(market_id, size, price, side, stp_mode=0, order_type=0, post_only=False, reduce_only=False, tif=0, expiry=0):
    try:
        # Encode order as bytes32 hash (simplified)
        data_bytes = (
            market_id.to_bytes(8, 'big') +
            int(size).to_bytes(32, 'big') +
            int(price).to_bytes(32, 'big') +
            side.to_bytes(1, 'big')
        )
        signature = sign_permit(data_bytes)
        permit = {
            "account": ACCOUNT,
            "signer": SIGNER_ADDRESS,
            "nonce": "0",  # ideally fetch from API
            "deadline": str(int(time.time()) + 3600),
            "signature": signature
        }
        payload = {
            "order_params": {
                "market_id": market_id,
                "size": size,
                "price": price,
                "side": side,
                "stp_mode": stp_mode,
                "order_type": order_type,
                "post_only": post_only,
                "reduce_only": reduce_only,
                "tif": tif,
                "expiry": expiry
            },
            "permit_params": permit
        }
        r = requests.post(f"{API_BASE}/orders/place", json=payload)
        if r.status_code == 200:
            data = r.json().get("data", {})
            log(f"✅ Order placed: {data.get('order_id')} tx={data.get('transaction_hash')}")
            return data
        else:
            log(f"❌ Failed to place order: {r.status_code} {r.text}")
            return None
    except Exception as e:
        log(f"❌ Exception place order: {e}")
        return None

# ===== Main Loop =====
if __name__ == "__main__":
    MARKET_ID = 1  # contoh BTC
    SIDE = 0  # 0=Long, 1=Short

    while True:
        size = random_size()
        price = "87467000000000000000000"  # contoh harga 87,467 USDC (18 decimals)
        place_order(MARKET_ID, size, price, SIDE)
        SIDE = 1 - SIDE
        time.sleep(random.randint(5, 15))

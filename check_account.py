import os
import time
import requests
from dotenv import load_dotenv
from web3 import Web3

# ===== Load ENV =====
load_dotenv()
WALLET = Web3.to_checksum_address(os.getenv("WALLET_ADDRESS"))
API_BASE = "https://api.testnet.rise.trade/v1"

# ===== Logging =====
def log(msg):
    print(msg)

# ===== Utilities =====
def get_account_equity(wallet):
    try:
        r = requests.get(f"{API_BASE}/accounts/{wallet.lower()}/perps")
        if r.status_code == 200:
            data = r.json()
            equity = int(data.get("equity", 0)) / 1e8
            free_margin = int(data.get("free_margin", 0)) / 1e8
            return equity, free_margin
        else:
            log(f"❌ Failed to fetch equity/free margin: {r.status_code} {r.text}")
    except Exception as e:
        log(f"❌ Exception fetching equity/free margin: {e}")
    return None, None

def get_open_positions(wallet):
    try:
        r = requests.get(f"{API_BASE}/positions", params={"account": wallet.lower()})
        if r.status_code == 200:
            positions = r.json().get("positions", [])
            return positions
        else:
            log(f"❌ Failed to fetch positions: {r.status_code} {r.text}")
    except Exception as e:
        log(f"❌ Exception fetching positions: {e}")
    return []

# ===== Main =====
if __name__ == "__main__":
    log(f"🔹 Checking account: {WALLET}")

    # Equity & Free Margin
    equity, free_margin = get_account_equity(WALLET)
    if equity is not None:
        log(f"💰 Equity: {equity} USD")
        log(f"💸 Free Margin: {free_margin} USD")
    else:
        log("⚠️ Could not fetch equity/free margin")

    # Positions
    positions = get_open_positions(WALLET)
    if positions:
        log(f"📈 Open Positions ({len(positions)}):")
        for pos in positions:
            market = pos.get("market_id")
            side = "Long" if pos.get("side") == 0 else "Short"
            size = int(pos.get("size", 0)) / 1e8
            entry_price = int(pos.get("entry_price", 0)) / 1e8
            unrealized_pnl = int(pos.get("unrealized_pnl", 0)) / 1e8
            log(f" - Market {market}: {side} | Size: {size} | Entry: {entry_price} | PnL: {unrealized_pnl}")
    else:
        log("⚠️ No open positions found")

# register_signer.py
import os
import time
import json
import requests
from dotenv import load_dotenv, set_key
from eth_account import Account
from eth_account.messages import encode_typed_data
from web3 import Web3

# ===== Load env =====
load_dotenv()
WALLET = os.getenv("WALLET_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")  # Wallet utama
API_BASE = "https://api.testnet.rise.trade/v1"

if not WALLET or not PRIVATE_KEY:
    print("❌ Masukkan WALLET_ADDRESS dan PRIVATE_KEY di .env dulu")
    exit(1)

# ===== 1. Ambil EIP712 Domain =====
def get_eip712_domain():
    r = requests.get(f"{API_BASE}/auth/eip712-domain")
    r.raise_for_status()
    data = r.json().get("data")
    if not data:
        return None
    # Transform to the correct EIP712 format
    return {
        "name": data.get("name"),
        "version": data.get("version"),
        "chainId": int(data.get("chain_id")),
        "verifyingContract": data.get("verifying_contract")
    }

domain = get_eip712_domain()
if not domain:
    print("❌ Failed to get EIP712 domain data.")
    exit(1)
print("✅ EIP712 Domain:", domain)

# ===== 2. Buat Signer Key baru =====
signer_acct = Account.create()
SIGNER_KEY = signer_acct.key.hex()
SIGNER_ADDRESS = signer_acct.address
print(f"✅ New Signer: {SIGNER_ADDRESS}")

# ===== 3. Ambil nonce akun utama =====
r = requests.get(f"{API_BASE}/accounts/{WALLET.lower()}/nonce")
r.raise_for_status()
nonce = int(r.json()["nonce"])
print(f"✅ Account nonce: {nonce}")

# ===== 4. Buat account signature (RegisterSigner) =====
expiration = int(time.time()) + 86400  # 1 hari dari sekarang
message = "Register signer"

# EIP712 structured data
register_signer_struct = {
    "types": {
        "EIP712Domain": [
            {"name": "name", "type": "string"},
            {"name": "version", "type": "string"},
            {"name": "chainId", "type": "uint256"},
            {"name": "verifyingContract", "type": "address"},
        ],
        "RegisterSigner": [
            {"name": "signer", "type": "address"},
            {"name": "message", "type": "string"},
            {"name": "expiration", "type": "uint40"},
            {"name": "nonce", "type": "uint256"},
        ],
    },
    "domain": domain,
    "primaryType": "RegisterSigner",
    "message": {
        "signer": SIGNER_ADDRESS,
        "message": message,
        "expiration": expiration,
        "nonce": nonce,
    },
}

account_signed = Account.sign_message(
    encode_typed_data(full_message=register_signer_struct),
    private_key=PRIVATE_KEY
)
account_signature = account_signed.signature.hex()
print("✅ Account signature done")

# ===== 5. Buat signer signature (VerifySigner) =====
verify_signer_struct = {
    "types": {
        "EIP712Domain": [
            {"name": "name", "type": "string"},
            {"name": "version", "type": "string"},
            {"name": "chainId", "type": "uint256"},
            {"name": "verifyingContract", "type": "address"},
        ],
        "VerifySigner": [
            {"name": "account", "type": "address"},
            {"name": "nonce", "type": "uint256"},
        ],
    },
    "domain": domain,
    "primaryType": "VerifySigner",
    "message": {
        "account": WALLET,
        "nonce": nonce,
    },
}

signer_signed = Account.sign_message(
    encode_typed_data(full_message=verify_signer_struct),
    private_key=SIGNER_KEY
)
signer_signature = signer_signed.signature.hex()
print("✅ Signer signature done")

# ===== 6. Register signer =====
body = {
    "account": WALLET,
    "signer": SIGNER_ADDRESS,
    "message": message,
    "expiration": expiration,
    "nonce": nonce,
    "account_signature": account_signature,
    "signer_signature": signer_signature,
}

r = requests.post(f"{API_BASE}/auth/register-signer", json=body)
r.raise_for_status()
resp = r.json()

if resp.get("success"):
    print("🎉 Signer registered successfully!")
    print("Transaction hash:", resp["transaction_hash"])
    print("Status:", resp["status"])
else:
    print("❌ Failed:", resp)

# ===== 7. Simpan ke .env =====
env_file = ".env"
set_key(env_file, "SIGNER_KEY", SIGNER_KEY)
set_key(env_file, "SIGNER_ADDRESS", SIGNER_ADDRESS)
print("✅ Saved SIGNER_KEY and SIGNER_ADDRESS to .env")

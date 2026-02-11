import os
import time
import random
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
WALLET = Web3.to_checksum_address(os.getenv("WALLET_ADDRESS"))
SENDWALLET = Web3.to_checksum_address(os.getenv("SENDWALLET"))

w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
        raise Exception(f" fail connect ke RPC: {RPC_URL}")

def human_delay(min_s=5, max_s=20):
    t = random.randint(min_s, max_s)
    print(f"⏳ Delay {t} Sec...")
    time.sleep(t)

def build_tx(tx):
    tx["nonce"] = w3.eth.get_transaction_count(WALLET)
    tx["gas"] = random.randint(180_000, 260_000)
    tx["gasPrice"] = w3.eth.gas_price
    return tx

def send_tx(tx):
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"✅ Tx Sent: {tx_hash.hex()}")
    return tx_hash

def watch_tx(tx_hash):
    print("👀 Watching transaction...")
    while True:
        try:
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            if receipt:
                status = "Success" if receipt.status == 1 else "Failed"
                gas_used = receipt.gasUsed
                print("Transaction Receipt:")
                print(f"Tx Hash      : {tx_hash.hex()}")
                print(f"Block Number : {receipt.blockNumber}")
                print(f"From         : {receipt['from']}")
                print(f"To           : {receipt['to']}")
                print(f"Status       : {status}")
                print(f"Gas Used     : {gas_used}")
                break
        except Exception:
            pass
        time.sleep(2)  

def dummy_tx():
    tx = {
        "from": WALLET,
        "to": SENDWALLET,
        "value": w3.to_wei(random.uniform(0.00001, 0.00005), "ether")
    }
    tx_hash = send_tx(build_tx(tx))
    watch_tx(tx_hash)

def main():
    actions = [dummy_tx] 
    for action in actions:
        human_delay()
        action()
    print("All actions done")

if __name__ == "__main__":
    main()

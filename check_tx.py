import os
from web3 import Web3
from dotenv import load_dotenv

# Load .env
load_dotenv()
RPC_URL = os.getenv("RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    raise Exception(f"❌ Gagal connect ke RPC: {RPC_URL}")
print("✅ RPC Connected")

def check_tx(tx_hash):
    try:
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        print("✅ Transaction Receipt:")
        print(f"Tx Hash      : {receipt['transactionHash'].hex()}")
        print(f"Block Number : {receipt['blockNumber']}")
        print(f"From         : {receipt['from']}")
        print(f"To           : {receipt['to']}")
        print(f"Status       : {'Success' if receipt['status'] == 1 else 'Failed'}")
        print(f"Gas Used     : {receipt['gasUsed']}")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Mungkin Tx belum dikonfirmasi atau salah hash")


if __name__ == "__main__":
    # Masukkan beberapa Tx hash di sini
    tx_hashes = [
        "28d0298d3d9127124d56af86a12c9bfe3293ec402a0e80e06b925da4cc39ae02",
        # Tambahkan hash lain jika perlu
    ]
    
    for tx in tx_hashes:
        check_tx(tx)
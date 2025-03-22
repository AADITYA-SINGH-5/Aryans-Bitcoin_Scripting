import logging
import json
import random
from decimal import Decimal
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

# Configure logging
logging.basicConfig(level=logging.INFO)

# Bitcoin RPC connection details
RPC_USER = "ruva"
RPC_PASS = "r1205"
RPC_HOST = "127.0.0.1"
RPC_PORT = 6000
WALLET = "my_unique_wallet"


# Function to establish connection
def connect_rpc():
    return AuthServiceProxy(f"http://{RPC_USER}:{RPC_PASS}@{RPC_HOST}:{RPC_PORT}")


# Connect to Bitcoin Core
rpc = connect_rpc()

# Ensure wallet is loaded or created
existing_wallets = rpc.listwallets()
if WALLET not in existing_wallets:
    try:
        rpc.loadwallet(WALLET)
        logging.info(f"Using existing wallet: {WALLET}")
    except JSONRPCException:
        rpc.createwallet(WALLET)
        logging.info(f"New wallet created: {WALLET}")

# Reconnect to the wallet instance
rpc = AuthServiceProxy(
    f"http://{RPC_USER}:{RPC_PASS}@{RPC_HOST}:{RPC_PORT}/wallet/{WALLET}"
)

# Set default fee
try:
    rpc.settxfee(0.0002)
except JSONRPCException:
    logging.warning("Transaction fee setup failed. Using fallback.")

# Mine initial blocks if no UTXOs are found
if not rpc.listunspent():
    mining_addr = rpc.getnewaddress()
    rpc.generatetoaddress(101, mining_addr)
    logging.info("Mined 101 blocks to generate test Bitcoin.")

# Generate random Bitcoin addresses
ADDR_A = rpc.getnewaddress("", "legacy")
ADDR_B = rpc.getnewaddress("", "legacy")
ADDR_C = rpc.getnewaddress("", "legacy")
logging.info(f"Generated addresses: {ADDR_A}, {ADDR_B}, {ADDR_C}")

# Fund first address
fund_tx = rpc.sendtoaddress(ADDR_A, 1)
logging.info(f"Sent 1 BTC to {ADDR_A}, txid={fund_tx}")

# Confirm the transaction
rpc.generatetoaddress(1, rpc.getnewaddress())

# Retrieve UTXOs for address A
utxos_A = [utxo for utxo in rpc.listunspent() if utxo["address"] == ADDR_A]
if not utxos_A:
    logging.error("No UTXOs found for Address A.")
    exit(1)

# Create transaction: A → B
input_A = [{"txid": utxos_A[0]["txid"], "vout": utxos_A[0]["vout"]}]
output_A = {ADDR_B: 0.5}

# Compute change and fee
fee = Decimal("0.00001")
change_A = Decimal(str(utxos_A[0]["amount"])) - Decimal("0.5") - fee
if change_A > 0:
    output_A[ADDR_A] = float(round(change_A, 8))

# Sign & Broadcast A → B
raw_tx_AB = rpc.createrawtransaction(input_A, output_A)
signed_tx_AB = rpc.signrawtransactionwithwallet(raw_tx_AB)
txid_AB = rpc.sendrawtransaction(signed_tx_AB["hex"])
logging.info(f"Transaction A → B broadcasted: {txid_AB}")

# Confirm transaction
rpc.generatetoaddress(1, rpc.getnewaddress())

# Retrieve UTXOs for address B
utxos_B = [utxo for utxo in rpc.listunspent() if utxo["address"] == ADDR_B]
if not utxos_B:
    logging.error("No UTXOs found for Address B.")
    exit(1)

# Create transaction: B → C
input_B = [{"txid": utxos_B[0]["txid"], "vout": utxos_B[0]["vout"]}]
output_B = {ADDR_C: 0.3}

# Compute change and fee
change_B = Decimal(str(utxos_B[0]["amount"])) - Decimal("0.3") - fee
if change_B > 0:
    output_B[ADDR_B] = float(round(change_B, 8))

# Sign & Broadcast B → C
raw_tx_BC = rpc.createrawtransaction(input_B, output_B)
signed_tx_BC = rpc.signrawtransactionwithwallet(raw_tx_BC)
txid_BC = rpc.sendrawtransaction(signed_tx_BC["hex"])
logging.info(f"Transaction B → C broadcasted: {txid_BC}")

# Confirm transaction
rpc.generatetoaddress(1, rpc.getnewaddress())

# Decode and analyze transaction B → C
decoded_BC = rpc.decoderawtransaction(signed_tx_BC["hex"])
logging.info(
    f"Decoded Transaction B → C:\n{json.dumps(decoded_BC, default=str, indent=2)}"
)

# Extract scriptSig or Witness
script_data = []
for vin in decoded_BC["vin"]:
    if "txinwitness" in vin:
        script_data.append(vin["txinwitness"])
    elif "scriptSig" in vin:
        script_data.append(vin["scriptSig"])

logging.info(f"Extracted ScriptSig/Witness from B → C: {script_data}")

import logging
import json
from decimal import Decimal
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

# Configure logging
logging.basicConfig(level=logging.INFO)

# Bitcoin Core RPC Connection Details
RPC_USER = "ruva"
RPC_PASS = "r1205"
RPC_HOST = "127.0.0.1"
RPC_PORT = 6000
WALLET_NAME = "segwit_wallet"


# Function to establish an RPC connection
def connect_to_rpc():
    return AuthServiceProxy(f"http://{RPC_USER}:{RPC_PASS}@{RPC_HOST}:{RPC_PORT}")


# Connect to Bitcoin Core
rpc = connect_to_rpc()

# Ensure the wallet is available
if WALLET_NAME not in rpc.listwallets():
    try:
        rpc.loadwallet(WALLET_NAME)
        logging.info(f"Loaded wallet: {WALLET_NAME}")
    except JSONRPCException:
        rpc.createwallet(WALLET_NAME)
        logging.info(f"Created new wallet: {WALLET_NAME}")

# Reconnect to the wallet instance
rpc = AuthServiceProxy(
    f"http://{RPC_USER}:{RPC_PASS}@{RPC_HOST}:{RPC_PORT}/wallet/{WALLET_NAME}"
)

# Generate three SegWit addresses: A, B, and C
A = rpc.getnewaddress("", "p2sh-segwit")
B = rpc.getnewaddress("", "p2sh-segwit")
C = rpc.getnewaddress("", "p2sh-segwit")
logging.info(f"Generated addresses:\n A = {A}\n B = {B}\n C = {C}")

# Fund Address A with 1 BTC
funding_txid = rpc.sendtoaddress(A, 1)
logging.info(f"Funded A with 1 BTC, txid={funding_txid}")
rpc.generatetoaddress(1, rpc.getnewaddress())

# Retrieve UTXOs for Address A
utxos_A = [utxo for utxo in rpc.listunspent() if utxo["address"] == A]
if not utxos_A:
    logging.error("No UTXOs found for Address A.")
    exit(1)

# Create Transaction: A → B
input_A = [{"txid": utxos_A[0]["txid"], "vout": utxos_A[0]["vout"]}]
output_A = {B: 0.5}

# Calculate change and fee
fee = Decimal("0.00001")
change_A = Decimal(str(utxos_A[0]["amount"])) - Decimal("0.5") - fee
if change_A > 0:
    output_A[A] = float(round(change_A, 8))

# Sign & Broadcast A → B Transaction
raw_tx_AB = rpc.createrawtransaction(input_A, output_A)
signed_tx_AB = rpc.signrawtransactionwithwallet(raw_tx_AB)
txid_AB = rpc.sendrawtransaction(signed_tx_AB["hex"])
logging.info(f"Transaction A → B broadcasted: {txid_AB}")

# Mine a block to confirm
rpc.generatetoaddress(1, rpc.getnewaddress())

# Retrieve UTXOs for Address B
utxos_B = [utxo for utxo in rpc.listunspent() if utxo["address"] == B]
if not utxos_B:
    logging.error("No UTXOs found for Address B.")
    exit(1)

# Create Transaction: B → C
input_B = [{"txid": utxos_B[0]["txid"], "vout": utxos_B[0]["vout"]}]
output_B = {C: 0.3}

# Calculate change and fee
change_B = Decimal(str(utxos_B[0]["amount"])) - Decimal("0.3") - fee
if change_B > 0:
    output_B[B] = float(round(change_B, 8))

# Sign & Broadcast B → C Transaction
raw_tx_BC = rpc.createrawtransaction(input_B, output_B)
signed_tx_BC = rpc.signrawtransactionwithwallet(raw_tx_BC)
txid_BC = rpc.sendrawtransaction(signed_tx_BC["hex"])
logging.info(f"Transaction B → C broadcasted: {txid_BC}")

# Mine a block to confirm
rpc.generatetoaddress(1, rpc.getnewaddress())

# Decode and Analyze Final Transaction
decoded_BC = rpc.decoderawtransaction(signed_tx_BC["hex"])
logging.info(
    f"Decoded B → C Transaction:\n{json.dumps(decoded_BC, default=str, indent=2)}"
)

# Extract and log scriptSig or Witness details
script_data = []
for vin in decoded_BC["vin"]:
    if "txinwitness" in vin:
        script_data.append(vin["txinwitness"])
    elif "scriptSig" in vin:
        script_data.append(vin["scriptSig"])

logging.info(f"Extracted Script Data: {script_data}")

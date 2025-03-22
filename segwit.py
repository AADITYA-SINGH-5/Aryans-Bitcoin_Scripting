import logging
import json
from decimal import Decimal
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

logging.basicConfig(level=logging.INFO)

RPC_USER = "ruva"
RPC_PASS = "r1205"
RPC_HOST = "127.0.0.1"
RPC_PORT = 6000
WALLET_NAME = "segwit_wallet"

def connect_to_rpc():
    return AuthServiceProxy(f"http://{RPC_USER}:{RPC_PASS}@{RPC_HOST}:{RPC_PORT}")

rpc = connect_to_rpc()

if WALLET_NAME not in rpc.listwallets():
    try:
        rpc.loadwallet(WALLET_NAME)
        logging.info(f"Loaded wallet: {WALLET_NAME}")
    except JSONRPCException:
        rpc.createwallet(WALLET_NAME)
        logging.info(f"Created new wallet: {WALLET_NAME}")

rpc = AuthServiceProxy(
    f"http://{RPC_USER}:{RPC_PASS}@{RPC_HOST}:{RPC_PORT}/wallet/{WALLET_NAME}"
)

A = rpc.getnewaddress("", "p2sh-segwit")
B = rpc.getnewaddress("", "p2sh-segwit")
C = rpc.getnewaddress("", "p2sh-segwit")
logging.info(f"Generated addresses:\n A = {A}\n B = {B}\n C = {C}")


funding_txid = rpc.sendtoaddress(A, 1)
logging.info(f"Funded A with 1 BTC, txid={funding_txid}")
rpc.generatetoaddress(1, rpc.getnewaddress())

utxos_A = [utxo for utxo in rpc.listunspent() if utxo["address"] == A]
if not utxos_A:
    logging.error("No UTXOs found for Address A.")
    exit(1)

input_A = [{"txid": utxos_A[0]["txid"], "vout": utxos_A[0]["vout"]}]
output_A = {B: 0.5}

fee = Decimal("0.00001")
change_A = Decimal(str(utxos_A[0]["amount"])) - Decimal("0.5") - fee
if change_A > 0:
    output_A[A] = float(round(change_A, 8))

raw_tx_AB = rpc.createrawtransaction(input_A, output_A)
signed_tx_AB = rpc.signrawtransactionwithwallet(raw_tx_AB)
txid_AB = rpc.sendrawtransaction(signed_tx_AB["hex"])
logging.info(f"Transaction A → B broadcasted: {txid_AB}")

rpc.generatetoaddress(1, rpc.getnewaddress())

utxos_B = [utxo for utxo in rpc.listunspent() if utxo["address"] == B]
if not utxos_B:
    logging.error("No UTXOs found for Address B.")
    exit(1)

input_B = [{"txid": utxos_B[0]["txid"], "vout": utxos_B[0]["vout"]}]
output_B = {C: 0.3}

change_B = Decimal(str(utxos_B[0]["amount"])) - Decimal("0.3") - fee
if change_B > 0:
    output_B[B] = float(round(change_B, 8))

raw_tx_BC = rpc.createrawtransaction(input_B, output_B)
signed_tx_BC = rpc.signrawtransactionwithwallet(raw_tx_BC)
txid_BC = rpc.sendrawtransaction(signed_tx_BC["hex"])
logging.info(f"Transaction B → C broadcasted: {txid_BC}")

rpc.generatetoaddress(1, rpc.getnewaddress())

decoded_BC = rpc.decoderawtransaction(signed_tx_BC["hex"])
logging.info(
    f"Decoded B → C Transaction:\n{json.dumps(decoded_BC, default=str, indent=2)}"
)

script_data = []
for vin in decoded_BC["vin"]:
    if "txinwitness" in vin:
        script_data.append(vin["txinwitness"])
    elif "scriptSig" in vin:
        script_data.append(vin["scriptSig"])

logging.info(f"Extracted Script Data: {script_data}")

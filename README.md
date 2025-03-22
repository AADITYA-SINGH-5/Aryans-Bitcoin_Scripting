# Bitcoin Scripting

## Introduction
 Bitcoin transactions using **Legacy (P2PKH) and SegWit (P2SH-P2WPKH) formats** in Bitcoin Core's **Regtest mode**. The provided Python scripts establish an RPC connection to Bitcoin Core, create wallets, generate addresses, send transactions, and analyze their outputs.

## Prerequisites
- **Bitcoin Core** (`bitcoind`, `bitcoin-cli`)
- **Python 3**
- **Required Python packages:** Install using:
  ```bash
  pip install python-bitcoinrpc
  ```

## Setting Up Bitcoin Core
1. **Start Bitcoin Core in Regtest mode:**
   ```bash
   bitcoind -regtest -daemon
   ```
2. **Verify the node is running:**
   ```bash
   bitcoin-cli -regtest getblockchaininfo
   ```

## Running the Scripts
### 1. Legacy Transactions (`legacy.py`)
This script performs transactions using **Legacy P2PKH addresses**.

#### Steps:
- Creates or loads a wallet (`my_unique_wallet`).
- Generates three legacy addresses (A, B, C).
- Mines 101 blocks to fund the wallet.
- Sends **0.5 BTC** from A → B.
- Sends **0.3 BTC** from B → C.
- Decodes and logs transaction details.

#### Run the script:
```bash
python legacy.py
```

### 2. SegWit Transactions (`segwit.py`)
This script performs transactions using **SegWit P2SH-P2WPKH addresses**.

#### Steps:
- Creates or loads a wallet (`segwit_wallet`).
- Generates three SegWit addresses (A', B', C').
- Mines 101 blocks to fund the wallet.
- Sends **0.5 BTC** from A' → B'.
- Sends **0.3 BTC** from B' → C'.
- Decodes and logs transaction details.

#### Run the script:
```bash
python segwit.py
```

## Debugging & Verification
To check transactions, use the following commands:


### Get transaction details:
```bash
bitcoin-cli -regtest gettransaction <txid>
```

### Decode a raw transaction:
```bash
bitcoin-cli -regtest decoderawtransaction $(bitcoin-cli -regtest getrawtransaction <txid> 1)
```

## Stopping Bitcoin Core
To safely stop `bitcoind`, run:
```bash
bitcoin-cli -regtest stop
```

## Team Member name and roll number

- Ruva Kachhia - 230003061
- Aaditya Singh - 230004001
- Anurag Singh - 230002011
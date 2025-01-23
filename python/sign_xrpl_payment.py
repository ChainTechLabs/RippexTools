"""XRP Client"""

import sys
import os
import json
import getpass

from datetime import datetime

import xrpl
from xrpl.wallet import Wallet
from xrpl.clients import JsonRpcClient
from xrpl.models import Payment
from xrpl.constants import CryptoAlgorithm

def load_wallet_from_secret(secret, algo):
    """load_wallet_from_secret"""

    if algo == 'SECP256K1':
        new_wallet = Wallet.from_secret(secret, algorithm = CryptoAlgorithm.SECP256K1)
    elif algo == 'Ed25519':
        new_wallet = Wallet.from_secret(secret, algorithm = CryptoAlgorithm.ED25519)
    else:
        print(f'Error: Unknown algorithm selected {algo}')
        sys.exit(1)

    print(f'Address:\t{new_wallet.address}')
    print(f'Public key:\t{new_wallet.public_key}')
    print(f'Seed:\t\t{new_wallet.seed[0:3]}{"*"*(len(new_wallet.seed) - 3)}')
    print(f'PrivKey:\t{new_wallet.private_key[0:10]}{"*"*(len(new_wallet.private_key) - 10)}')
    print(f'Block Exp:\thttps://xrpscan.com/account/{new_wallet.address}')
    print('')

    return new_wallet

def create_signed_tx(client, wallet, destination_address, tx_amount, current_leger_sequence, last_acount_sequence, destination_tag, tx_fee):
    """create a signed tx"""

    if client:

        new_payment = Payment(
            account=wallet.address,
            destination=destination_address,
            amount=str(int(tx_amount*1000000)),
            last_ledger_sequence=(current_leger_sequence + 100) # 5m (3 seconds per increment) minutes to submit the transaction
        )

        # Sign online (adds fee and sequence number)
        signed_tx = xrpl.transaction.autofill_and_sign(new_payment, client, wallet)

    else:

        # Manually (adds fee and sequence number)
        new_payment = Payment(
            account=wallet.address,
            destination=destination_address,
            amount=str(int(tx_amount*1000000)),
            last_ledger_sequence=(current_leger_sequence + 200), # 10m (~3 seconds per increment) minutes to submit the transaction
            fee=tx_fee,
            sequence=last_acount_sequence,
            destination_tag=destination_tag
        )

        # Sign offline
        signed_tx = xrpl.transaction.sign(new_payment, wallet)

    print(f'Signed NEW payment of {int(signed_tx.amount)/1000000:.2f} XRP: {signed_tx.account} -> {signed_tx.destination} OK')
    print('')

    return signed_tx

"""Main"""

print("\nXRPL Transaction Signatory\n--------------------------\n")

xrp_client = None
algorithm = "Ed25519"
current_leger_sequence = 0
last_acount_sequence = 0
current_fee = 0

# Validate arguments
if len(sys.argv) != 4 or sys.argv[2] != '-algorithm' or sys.argv[3] not in ['Ed25519', 'secp256k1']:
    print("Usage: python3 sign_xrpl_payment.py <relative_path_to_address_probe_file.json> -algorithm <Ed25519 | secp256k1>\n")
    sys.exit(1)

# Extract arguments
probe_filename_path = sys.argv[1]
algorithm_flag = sys.argv[2]
algorithm = sys.argv[3]

# Check if the JSON file exists
if not os.path.isfile(probe_filename_path):
    print(f"Error: The file '{probe_filename_path}' does not exist or is not accessible.\n")
    sys.exit(1)

wallet_master_secret = getpass.getpass("Please enter the wallet master secret: ")
print()

xrp_wallet = load_wallet_from_secret(wallet_master_secret, algorithm)

with open(probe_filename_path, "r", encoding="utf-8") as file_in:
    raw_json_data = file_in.read()
    probe_data = json.loads(raw_json_data)

# Check if the probe data source address matches the one we generated from the private key
if xrp_wallet.address != probe_data.get("src_address"):
    print("Private key load has resulted in a different account address than expected, try using the other algorithm..S")
    sys.exit(1)

current_leger_sequence = probe_data.get("current_leger_sequence")
last_acount_sequence = probe_data.get("last_acount_sequence")
current_fee = probe_data.get("current_fee")

tx_amount = probe_data.get("tx_amount")
recipient_address = probe_data.get("dst_address")
dst_tag = probe_data.get("destination_tag")

print(f"Master key:\t {wallet_master_secret[0:3]}{'*'*(len(wallet_master_secret) - 10)}{wallet_master_secret[-3:]}")
print(f"Recipient addr:\t {recipient_address}")
print(f"Amount to send:\t {tx_amount} XRP")
print(f"Dest tag:\t {dst_tag}")

print(f"LEGER Seq:\t {current_leger_sequence}")
print(f"ACCOUNT Seq:\t {last_acount_sequence}")
print(f"Transact fee:\t {current_fee}")

response = input("\nIs the information provided correct? (yes/no): ").strip().lower()

# Check the response
if response != 'yes':
    print("Abort!")
    quit()

print('')

xrp_client = JsonRpcClient('https://xrplcluster.com/')

# Check if the account exists on the mainnet
account_exists = xrpl.account.does_account_exist(xrp_wallet.address, xrp_client, 'current')
print(f"Account exists:\t{account_exists}")

# If no account then dont continue (have you funded it with 10 XRP yet?)
if not account_exists:
    print("Account not found, abort!\n")
    quit()

# Check the account ballance
account_ballance = xrpl.account.get_balance(xrp_wallet.address, xrp_client, 'current')

if(account_ballance/1000000 < tx_amount):
    print(f'Not enough in the account to send {tx_amount} XRP, abort!\n')
    quit()

print(f"Addr ballance:\t{account_ballance/1000000:.2f} XRP")

current_leger_sequence = xrpl.ledger.get_latest_validated_ledger_sequence(xrp_client)
print(f'Last leger seq:\t{current_leger_sequence}\n')

signed_payment = create_signed_tx(
    client=xrp_client,
    wallet=xrp_wallet,
    destination_address=recipient_address,
    tx_amount=tx_amount,
    current_leger_sequence=current_leger_sequence,
    last_acount_sequence=last_acount_sequence,
    destination_tag=dst_tag,
    tx_fee=current_fee
)

dict_transaction = signed_payment.to_dict()

print("Signed JSON payment:")
print(json.dumps(dict_transaction))
print('')

directory_path = 'signed_transactions'

if not os.path.isdir(directory_path):
    print(f"Directory '{directory_path}' does not exist. Creating it...")
    os.makedirs(directory_path)

file_name = f"{directory_path}/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_tx.json"

with open(file_name, "w", encoding="utf-8") as file_out:
    file_out.write(json.dumps(dict_transaction, indent=2))

print(f"Done - Wrote new signed transaction to: {file_name}\n")

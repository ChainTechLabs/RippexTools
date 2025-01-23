"""Address probe for offline tx signing"""

import json
import sys
from datetime import datetime

import xrpl
from xrpl.clients import JsonRpcClient

print("\nXRPL Transaction Probe\n----------------------\n")

probe_address = input("Please enter the SOURCE address to probe: ")
destination_address = input("Please enter the DESTINATION address to send to: ")
destination_tag = int(input("Please enter the DESTINATION TAG: "))
print()
amount = float(input("How much do you want to send from this address: "))
print()

xrp_client = JsonRpcClient('https://xrplcluster.com/')

probe_data = {
    'src_address': probe_address,
    'dst_address': destination_address,
    'destination_tag': destination_tag,
    'current_leger_sequence': 0,
    'last_acount_sequence': 0,
    'current_fee': 0,
    'tx_amount': 0
}

source_address_exists = xrpl.account.does_account_exist(probe_address, xrp_client, 'current')
print(f"Source address exists:\t\t{source_address_exists}")

if not source_address_exists:
    print("Error: Source address not found!\n")
    sys.exit(1)

dest_address_exists = xrpl.account.does_account_exist(destination_address, xrp_client, 'current')
print(f"Dest address exists:\t\t{dest_address_exists}")

if not dest_address_exists:
    print("Error: Destination address not found!\n")
    sys.exit(1)

account_ballance = xrpl.account.get_balance(probe_address, xrp_client, 'current')
print(f'Account contains:\t\t{account_ballance/1000000:.2f} XRP ({(account_ballance/1000000) - amount:.2f} remaining)')

if amount >= account_ballance/1000000:
    print('Insufficient funds!\n')
    quit()

# Set the tx amount
probe_data['tx_amount'] = amount

probe_data['current_leger_sequence'] = xrpl.ledger.get_latest_validated_ledger_sequence(xrp_client)
print(f'LEGER sequence number:\t\t{probe_data.get("current_leger_sequence")}')

probe_data['last_acount_sequence'] = xrpl.account.get_next_valid_seq_number(probe_address, xrp_client,'current')
print(f'ACCOUNT sequence number:\t{probe_data.get("last_acount_sequence")}')

probe_data['current_fee'] = xrpl.ledger.get_fee(xrp_client)
print(f'NETWORK current fee:\t\t{probe_data.get("current_fee")}')

print(f"\nProbe data: {json.dumps(probe_data, indent=2)}\n")

directory_path = 'address_probes'

if not os.path.isdir(directory_path):
    print(f"Directory '{directory_path}' does not exist. Creating it...")
    os.makedirs(directory_path)

file_name = f"{directory_path}/{probe_address[0:5]}_probe_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"

with open(file_name, "w", encoding="utf-8") as file_out:
    file_out.write(json.dumps(probe_data, indent=2))

print(f"Done - Wrote new address probe to: {file_name}\n")

"""Pre-signed payment submitter"""

import sys
import json
import xrpl

from xrpl.clients import JsonRpcClient
from xrpl.transaction import submit_and_wait

print("\nXRPL Transaction Submitter\n--------------------------\n")

# Check if a file name is provided as an argument
if len(sys.argv) != 2:
    print("Usage: python submit_signed_xrpl_payment.py <filename>")
    sys.exit(1)

# Get the file name from the command-line arguments
file_name = sys.argv[1]
json_input = None

try:
    # Read the file contents
    with open(file_name, 'r', encoding='utf-8') as file:
        json_input = file.read()

        print('Pre-signed JSON transaction:')
        print(json_input)
        print('')

except FileNotFoundError:
    print(f"Error: The file '{file_name}' was not found.")
    sys.exit(1)

except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)

if json_input is None:
    print("Error reading json input file")
    quit()

xrp_client = JsonRpcClient('https://xrplcluster.com/')

# Load the pre-signed payment
signed_payment = xrpl.models.transactions.payment.Payment.from_dict(json.loads(json_input))

print("Pre-signed payment:")
print(signed_payment)
print('')

# Get the last open leger sequence number
current_leger_sequence = xrpl.ledger.get_latest_validated_ledger_sequence(xrp_client)
sequence_remaining = signed_payment.last_ledger_sequence - current_leger_sequence

print(f"Leger sequence {signed_payment.last_ledger_sequence} v {current_leger_sequence} grace period remaining: {sequence_remaining}\n")

if sequence_remaining <= 3: # ~10 seconds
    print('Leger sequence grace period is too short, abort!\n')
    quit()

print(f'Payment of {int(signed_payment.amount)/1000000:.2f} XRP: {signed_payment.account} -> {signed_payment.destination}\n')

# Ask the user for confirmation
response = input("Are you SURE you want to proceed? (yes/no): ").strip().lower()

# Check the response
if response == 'yes':

    print('\nSubmitting...\n')

    try:
        tx_response = submit_and_wait(signed_payment, xrp_client)
        print("XRPL Transaction Successful!")
    except Exception as e:
        print("Transaction Failed", e)

elif response == 'no':
    print("\nCanceled.")

else:
    print("Invalid input. Please respond with 'yes' or 'no'.")

print('\nDone\n')

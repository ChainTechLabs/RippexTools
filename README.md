# RippexTools
A set of tools to interact with the now unmaintained Rippex Wallet

### Introduction

In the early days of Ripple Labs, the options for non-custodial desktop wallet software were quite limited. Many users, myself included, preferred not to transfer their XRP to custodial services like Gate.io. Instead, we turned to a JavaScript-based wallet called Rippex. This wallet provided a reliable way to hold XRP non-custodially, eliminating the need to trust third parties.

However, the Rippex wallet (linked below) was abandoned nearly nine years ago. Setting up and running the deprecated software today involves significant overhead, making it challenging to access any XRP stored in its wallet files, if you can even get it to connect to the network.

### Rippex Decrypt

After a lengthy and arduous litigation process, it seems XRP is finally on track to being recognized as a legitimate bridge currency. As a result, many of us have found ourselves dusting off our old Rippex wallets, only to discover they can no longer be opened or connected to the Ripple Network.

This project offers a simple web tool where you can paste the Base64-encoded contents of your Rippex wallet, enter your decryption password (you’ll still need that!), and let the software decrypt your wallet to retrieve your private key.

Note: *The JavaScript library (SJCL) used to create these wallets has some gross nuances in its implementation, so using the same library for decryption avoids a lot of issues. Additionally, the Rippex wallet did not use cryptographically secure random number generation, so it’s highly recommended to transfer your funds to a professionally maintained, open-source alternative like Trezor (link below) for long-term security.*

With your private key in hand, you can interact with the modern XRP Ledger using Python and the xrpl library (linked below). I’ll also share the code for this interaction soon.

### Rippex Wallet Decryptor usage

**The web tool works locally only, no data is sent or received and can / should be used offline**

1. Clone the repository to your local PC.
2. **Strongly recommended**: Copy the files to a clean, offline PC, Raspberry Pi, or similar device, as you will be exposing your private key during the process.
3. Locate and open your Rippex Wallet file in any good text editor.
4. Open the ```rippex_wallet_decryptor.html``` file in Chrome or Firefox (other browsers have not been tested).
5. Copy the Base64-encoded contents of your Rippex Wallet into the "Base64 Encoded Wallet" input box.
6. Enter your decryption password.
7. Click the Decrypt button.
8. **If** your password is correct, the page will decrypt your wallet file and reveal it's contents.
7. Securly record your decrypted master key (also referred to as a Secret Key).
8. Use this private key to access your XRP funds using the xrpl library.

### Python xrpl scrips usage

#### xrpl_probe.py [ONLINE]

This script gathers the essential details for the transaction you want to create. You will need to carefully provide the following information:

1. SOURCE Address: The wallet address from which you want to send the funds.

2. DESTINATION Address: The wallet address to which you want to send the funds.

3. DESTINATION TAG (Critical if sending to an exchange): This tag ensures that the exchange can correctly route your funds, especially when using a shared address for multiple customers.

4. Amount to Send: Specify the amount you want to transfer to the destination address.

The script will verify that the specified addresses exist and that sufficient funds are available. If everything checks out, the script will generate a .json file and save it to the ```address_probes``` directory. This file contains all the necessary information for the ```sign_xrpl_payment.py```  script to create and sign the transaction.

Take the new json file, put it on a USB key and transfer to your OFFLINE machine to actually sign the transaction.

Note: *You can do all of this on the same online machine but I don't recommend it*

#### sign_xrpl_payment.py [OFFLINE]

This script signes the XRPL transaction created by ```xrpl_probe.py```, it has been designed to be used OFFLINE as you have to enter your private key.

Copy your probe .json file to an offline machine (via USB for example) and run the following (example) command replacing your filename with the probe file example below:

```python3 sign_xrpl_payment.py address_probes/rsZ3b_probe_2025-01-22_17-16-55.json -algorithm Ed25519```

Note: *If you get an error complaining about the algorithm selected you might want to try using ```SECP256K1``` opposed to ```Ed25519``` dependant on when and in what patch state your system was in when you generated the original wallet file.*

You will be asked to enter your Master Key (found by using the Rippex Wallet Decryptor web tool) at which point a bunch of checks will be made and you will be asked to confirm the signing operation if everything looks good.

If everything is correct enter 'yes' and the script will create you a new file in the ```signed_transactions``` directory that can then be USB copied safely back to your ONLINE machine for transmission to XRPL network.

Note: *You have a 5 minute grace period in which to send the signed transaction to the network*

#### submit_signed_xrpl_payment.py [ONLINE]

This script submits the signed transaction to the XRPL network that you have just created OFFLINE using the sign_xrpl_payment.py script.

It requires the relative path to the signed transaction file, for example: 

```python3 submit_signed_xrpl_payment.py signed_transactions/2024-12-29_21-08-56_tx.json```

Once the script is run, it will load the file, display a summary of the actions it is about to perform, and if you have not run out of time (remember you have to get this done in 5 minutes!) prompt you for confirmation.

**Important**: Double-check **everything** before entering 'yes'— once the transaction is sent, it cannot be undone.

If everything is correct, enter 'yes' and the transaction will be sent and processed by the XRPL network, your funds will be transferred to the specified DESTINATION address.

*phew*

### Disclaimer

Use this tool at your own risk. You are solely responsible for the security of your private key and any associated funds. It is strongly recommended that you download and transfer this project to an offline device (e.g. a PC or Raspberry Pi) to minimize security risks, as private keys should never be handled on an internet-connected machine. The creator of this tool accepts NO liability for any loss or damage resulting from it's use.

### Buy me a coffee

If this project helps you unlock your XRP, please consider showing your appreciation by buying me a coffee, a pint, a car, or perhaps a *modest* mansion (i’m not greedy!).

XRP Address: ```rLC8yKbdfNHVHCKpV9BP7BduYpPK1gKkqL```

### Links

https://github.com/rippex/ripple-client-desktop---UNMAINTAINED

https://pypi.org/project/xrpl-py/

https://trezor.io/

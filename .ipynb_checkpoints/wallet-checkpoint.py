
# Import dependencies
import subprocess
import json
from dotenv import load_dotenv
import os
from web3 import Web3, Account, middleware
import bit
from bit import Key, PrivateKey, PrivateKeyTestnet
from bit.network import NetworkAPI
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3.middleware import geth_poa_middleware



# Load and set environment variables
load_dotenv()
mnemonic=os.getenv("Mnemonic_key")

# Import constants.py and necessary functions from bit and web3
from constants import *

#create web3 object
w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
w3.eth.setGasPriceStrategy(medium_gas_price_strategy)

# Create a function called `derive_wallets`
def derive_wallets(coin=BTC, mnemonic=mnemonic, depth=3):
    command = f'php ./derive -g --mnemonic="{mnemonic}" --cols=all --coin={coin} --numderive={depth} --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    keys = json.loads(output)
    return keys

# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = {BTC:derive_wallets(BTC), ETH:derive_wallets(ETH)}

# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, priv_key):
    if coin == BTCTEST:
        return bit.PrivateKeyTestnet(priv_key) 
    elif coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    else:
        print('Error: Invalid coin or key. Please use ETH or BTCTEST and verify wallet keys')
        
# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, to, amount):
    if coin == ETH:
        value = w3.toWei(amount, "ether") # convert 1.2 ETH to 120000000000 wei
        gasEstimate = w3.eth.estimateGas(
            {"from": account, "to": to, "amount": value}
    )
        return {
            "from": account,
            "to": to,
            "value": value,
            "gas": gasEstimate,
            "gasPrice": 20000000000,
            "nonce": w3.eth.getTransactionCount(account),
            "chainId": w3.eth.chain_id
    }
    elif coin == BTCTEST:
        return bit.PrivateKeyTestnet.prepare_transaction(account.address, [(to,amount,BTC)])
    else:
        print('Error: Invalid coin selection. Please use ETH or BTCTEST')
# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account, to, amount):
    if coin == ETH:
        raw_tx = create_tx(coin, account.address, to, amount)
        signed_tx = account.sign_transaction(raw_tx)
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return result.hex()
    elif coin == BTCTEST:
        raw_tx = create_tx(coin, account, to, amount)
        signed_tx = account.sign_transaction(raw_tx)
        return NetworkAPI.broadcast_tx_testnet(signed_tx)
    else:
        print('Error: Invalid coin selection. Please use ETH or BTCTEST')
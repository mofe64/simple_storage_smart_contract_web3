import os
from solcx import compile_standard, install_solc
import json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# compile solidity
install_solc("0.6.0")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# connect to ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
chainId = 1337
my_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
private_key = os.getenv("PRIVATE_KEY")


# create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
print(SimpleStorage)

# to deploy the contract we need to build transaction, sign the transaction then send the transaction

# Get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)

# build transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {"chainId": chainId, "from": my_address, "nonce": nonce}
)

# sign transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# send transaction
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

# get block confirmation
tx_reciept = w3.eth.wait_for_transaction_receipt(tx_hash)


# working with our deployed contract
# when working with a deployed contract we always need two things the contract address and the contract abi
simple_storage = w3.eth.contract(address=tx_reciept.contractAddress, abi=abi)

# we can now access functions on the contract
# there are two ways we can interact with our contract with a call and with a transact
# call -> simulates making the call and getting a return value doesnt make a state change to the blockchain
# Transact -> actually make the state change
print(simple_storage.functions.retrieve().call())

# to carry out a transaction
store_transaction = simple_storage.functions.store(100).buildTransaction(
    {
        "chainId": chainId,
        "from": my_address,
        "nonce": nonce
        + 1,  # nonce can only be used once for each transaction, we already used nonce when deploying the contract we do + 1 now
    }
)

signed_store_tx = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)

send_store_tx = w3.eth.send_raw_transaction(signed_store_tx.rawTransaction)

send_store_tx_reciept = w3.eth.wait_for_transaction_receipt(send_store_tx)


print(
    simple_storage.functions.retrieve().call()
)  # should print out our newly updated transaction value

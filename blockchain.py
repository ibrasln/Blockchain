import datetime
from hashlib import sha256
import json
import time
from flask import Flask, jsonify

class Blockchain:
    
    difficulty = 6 # Difficulty of mining
    
    def __init__(self):
        self.utxos = []
        self.chain = []
        self.create_block(nonce = 1, prev_hash = '0') # It's for genesis block
    
    def hash(self, block):
        '''
        It creates a hash.
        '''
        encoded_block = json.dumps(block).encode()
        return sha256(encoded_block).hexdigest()
    
    def create_block(self, nonce, prev_hash):
        '''
        It creates a block.
        '''
        block = {'Block Number' : len(self.chain) + 1,
                 'Timestamp' : int(time.time()),
                 'Nonce' : nonce,
                 'Transactions' : self.utxos,
                 'Previous Hash' : prev_hash}
        
        # We will see these properties in the chain.
        blockInChain = {'Block Number' : len(self.chain) + 1,
                        'Timestamp' : int(time.time()),
                        'Date' : str(datetime.datetime.now()),
                        'Nonce' : nonce,
                        'Transactions' : self.utxos,
                        'Previous Hash' : prev_hash,
                        'Hash' : self.hash(block)}
        
        self.utxos = [] # We send the transactions into the block. So UTXO list will be empty.
        self.chain.append(blockInChain)
        return block
    
    def get_prev_block(self):
        '''
        It gives us the last block of the chain.
        '''
        return self.chain[-1]
    
    def add_new_transaction(self, sender, receiver, amount):
        '''
        It adds a transaction to the UTXOs.
        '''
        transaction = {'Sender' : sender,
                       'Receiver' : receiver,
                       'Amount' : f"{amount} BTC"}
        
        self.utxos.append(transaction)
        return transaction
    
    def compute_hash(self, nonce1, nonce2):
        '''
        It creates a hash for the mathematical problem of proof-of-work.
        '''
        return sha256(str(nonce1 ** 2 - nonce2 ** 2).encode()).hexdigest()
    
    def proof_of_work(self, prev_nonce):
        '''
        It runs the Proof-Of-Work consensus mechanism.
        '''
        new_nonce = 1
        
        while True:
            computed_hash = self.compute_hash(new_nonce, prev_nonce) # We compute hash.
            
            if computed_hash.startswith('0' * self.difficulty): # If hash starts with 6 '0', stop the loop.
                break
            else:
                new_nonce += 1
        
        return new_nonce
    
    def is_chain_valid(self, chain):
        '''
        It checks the validity of the chain. 
        '''
        prev_block = chain[0]
        block_number = 1
        
        while block_number < len(chain):
            block = chain[block_number]
            
            if block['Previous Hash'] != self.hash(prev_block): # If previous hash of block is not equal to the hash of previous block
                return False
            
            prev_nonce = prev_block['Nonce']
            nonce = block['Nonce']
            
            computed_hash = self.compute_hash(nonce, prev_nonce)
            
            if not computed_hash.startswith('0' * self.difficulty): # If computed hash doesn't start with 6 '0'
                return False
            
            prev_block = block
            block_number += 1
        
        return True
    
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
 
blockchain = Blockchain()

def create_transaction():
    '''
    It creates a transaction.
    '''
    sender = input("Sender: ")
    receiver = input("Receiver: ")
    amount = float(input("Amount: "))
    blockchain.add_new_transaction(sender, receiver, amount)
    
while True:
    choose = input("Do you want to add a transaction?(Y/N)")

    if choose.upper() == 'Y':
        create_transaction()
    elif choose.upper() == 'N':
        break
    else:
        print("Invalid input.")

@app.route('/get_chain', methods = ['GET'])
def get_chain():
    '''
    It shows us the chain.
    '''
    response = {'Length' : len(blockchain.chain),
                'Chain' : blockchain.chain}
    
    return jsonify(response), 200

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    '''
    It mines a block.
    '''
    prev_block = blockchain.get_prev_block()
    prev_nonce = prev_block['Nonce']
    nonce = blockchain.proof_of_work(prev_nonce)
    prev_hash = blockchain.hash(prev_block)
    block = blockchain.create_block(nonce, prev_hash)
    block_hash = blockchain.hash(block)
    
    response = {'Message' : 'Congratulations, you earned 6.25 BTC!',
                'Block Number' : block['Block Number'],
                'Timestamp' : block['Timestamp'],
                'Nonce' : block['Nonce'],
                'Transactions' : block['Transactions'],
                'Previous Hash' : block['Previous Hash'],
                'Date' : str(datetime.datetime.now()),
                'Hash' : block_hash}
    
    return jsonify(response), 200

@app.route('/get_utxos', methods = ['GET'])
def get_utxos():
    '''
    It shows us to unspent transaction outputs.
    '''
    response = {'Length' : len(blockchain.utxos),
                'UTXOs' : blockchain.utxos}
    
    return jsonify(response), 200

@app.route('/is_valid', methods = ['GET'])
def is_valid():
    '''
    It says the validity of the chain.
    '''
    validation = blockchain.is_chain_valid(blockchain.chain)
    
    if validation:
        response = {'Message' : 'Blockchain is valid.'}
    else:
        response = {'Message' : 'Blockchain is not valid.'}
    
    return jsonify(response), 200

app.run(host = '0.0.0.0', port = 5000)

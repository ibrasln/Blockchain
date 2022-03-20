# -*- coding: utf-8 -*-
"""
Created on Sun Mar 20 15:32:06 2022

@author: ibraslnn
"""

import datetime
import hashlib
import json
from flask import Flask, jsonify

# Part 1 - Building a Blockchain ******

class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.create_block(proof = 1, prev_hash = '0')
        
    def create_block(self, proof, prev_hash):
        #We create a block dictionary
        block = {'index' : len(self.chain) + 1,
                 'timestamp' : str(datetime.datetime.now()),
                 'proof' : proof,
                 'previous_hash' : prev_hash} 
        #The proof is same as the nonce.
        
        #We add the block to the chain
        self.chain.append(block)

        return block
    
    def get_prev_block(self):
        #We return the last block in the chain
        return self.chain[-1]
    
    def proof_of_work(self, prev_proof):
        new_proof = 1
        check_proof = False
        
        #When we cannot find the true nonce
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof ** 2 - prev_proof ** 2).encode()).hexdigest()
            # **2 is adding a bit challenge to hash
            '''
            new_proof ** 2 - prev_proof ** 2 -> 5
            str(new_proof ** 2 - prev_proof ** 2) -> '5'
            str(new_proof ** 2 - prev_proof ** 2).encode() -> b'5'
            (str(new_proof ** 2 - prev_proof ** 2).encode()).hexdigest() -> hexadecimal format
            '''
            
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
            
        return new_proof
    
    def hash(self, block):
        #We transform the block dictionary into string
        encoded_block = json.dumps(block, sort_keys  = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        prev_block = chain[0]
        block_index = 1
        
        #When block index reached the end of the chain
        while block_index < len(chain):
            block = chain[block_index]
            
            #First check is the previous hash of the block is equal to the hash of the previous block
            if block['previous hash'] != self.hash(prev_block):
                return False
            
            prev_proof = prev_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof ** 2 - prev_proof ** 2).encode()).hexdigest()
            
            #Second check is the this hash operation starts with 4 leading zeros
            if hash_operation[:4] != '0000':
                return False
            
            prev_block = block
            block_index += 1
        
        return True


# Part 2 - Mining our Blockchain ******

# Creating a Web App
#https://flask.palletsprojects.com/en/1.1.x/quickstart/
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Creating a Blockchain
blockchain = Blockchain()

# Mining a new block

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    prev_block = blockchain.get_prev_block()
    prev_proof= prev_block['proof']
    
    proof = blockchain.proof_of_work(prev_proof)
    prev_hash = blockchain.hash(prev_block)
    
    block = blockchain.create_block(proof, prev_hash)
    
    response = {'message' : 'Congratulations, you mined a block!',
                'index' : block['index'],
                'timestamp' : block['timestamp'],
                'proof' : block['proof'],
                'previous_hash' : block['previous_hash']}
    
    return jsonify(response), 200
    #https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
    
# Getting the full Blockchain

@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain' : blockchain.chain,
                'length' : len(blockchain.chain)}
    
    return jsonify(response), 200

# Check if the blockchain is valid

@app.route('/is_valid', methods = ['GET'])
def is_valid():
    chain = blockchain.chain
    validation = blockchain.is_chain_valid(chain)
    
    if validation:
        response = {'message' : 'The blockchain is valid.'}
    else:
        response = {'message' : 'The blockchain is not valid.'}
        
    return jsonify(response), 200

# Running the app

app.run(host = '0.0.0.0', port = 5000)



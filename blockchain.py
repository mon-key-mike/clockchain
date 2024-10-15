import hashlib
import json
import time
from datetime import datetime

class SimpleBlockchain:
    def __init__(self, blockchain_file='blockchain.json'):
        self.chain = self.load_chain(blockchain_file)
        self.blockchain_file = blockchain_file

    def load_chain(self, blockchain_file):
        try:
            with open(blockchain_file, 'r') as file:
                return json.load(file)
            return []
        except FileNotFoundError:
            genesis_block = self.create_genesis_block()
            self.save_chain([genesis_block])
            return [genesis_block]

    def create_genesis_block(self):
        return {
            'index': 0,
            'timestamp': str(datetime.utcnow()),
            'data': 'Genesis Block',
            'previous_hash': '0',
            'hash': self.hash_block(0, str(datetime.utcnow()), 'Genesis Block', '0'),
            'nonce': 0
        }

    def save_chain(self, chain):
        with open(self.blockchain_file, 'w') as file:
            json.dump(chain, file, indent=4)

    def hash_block(self, index, timestamp, data, previous_hash, nonce=0):
        block_string = f"{index}{timestamp}{data}{previous_hash}{nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def add_block(self, data):
        last_block = self.chain[-1]
        index = len(self.chain)
        timestamp = str(datetime.utcnow())
        previous_hash = last_block['hash']
        new_block = {
            'index': index,
            'timestamp': timestamp,
            'data': data,
            'previous_hash': previous_hash,
            'hash': self.hash_block(index, timestamp, data, previous_hash),
            'nonce': 0
        }
        self.chain.append(new_block)
        self.save_chain(self.chain)
        return new_block

    def validate_block(self, block):
        last_block = self.chain[-1]
        if block['previous_hash'] != last_block['hash']:
            return False
        return True

class NistBlockchain(SimpleBlockchain):
    pass

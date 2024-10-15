import json
import hashlib
from datetime import datetime

class SimpleBlockchain:
    def __init__(self, genesis_file: str):
        self.genesis_file = genesis_file
        self.chain = []
        self.load_chain()

    def load_chain(self):
        """Load the blockchain from the genesis file."""
        try:
            with open(self.genesis_file, 'r') as f:   
                self.chain = json.load(f)
                print("Blockchain loaded successfully.") 
        except FileNotFoundError:
            print("Genesis file not found. Initializing a new blockchain.")
            self.chain = []  # Start with an empty chain 
            self.create_genesis_block()  # Create the genesis block
        except json.JSONDecodeError:
            print("Error decoding JSON from the genesis file.")
            self.chain = []  # Reset on error

    def create_genesis_block(self):
        """Create the genesis block and add it to the chain."""
        print("Creating genesis block...")
        genesis_block = {
            "index": 0,
            "timestamp": int(datetime.utcnow().timestamp()),  # Unix timestamp
            "data": "Genesis Block",
            "previous_hash": "0",
            "hash": "0"  # Placeholder hash
        }
        genesis_block['hash'] = self.hash(genesis_block)  # Compute hash
        self.chain.append(genesis_block)

    def hash(self, block: dict) -> str:
        """Compute the SHA-256 hash of a block."""
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def add_block(self, block: dict) -> bool:
        """Add a new block to the blockchain."""
        if not self.chain or block['index'] == len(self.chain):
            self.chain.append(block)
            self.save_chain()  # Save the updated chain  
            print(f"Block added: {block}")
            return True
        else:
            print("Error: Invalid block index.")
            return False

    def save_chain(self):
        """Save the current blockchain to the genesis file."""
        with open(self.genesis_file, 'w') as f:       
            json.dump(self.chain, f)
            print("Blockchain state saved successfully.")

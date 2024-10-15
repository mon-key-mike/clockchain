import json
import hashlib
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

class SimpleBlockchain:
    def __init__(self, genesis_file: str):
        self.genesis_file = genesis_file
        self.chain = []
        self.peers = set()  # Use a set to store unique peer addresses
        self.initialize_peers()  # Initialize peers list
        self.load_chain()

    def initialize_peers(self):
        """Initialize the peers directly in the code."""
        self.peers = {
            "https://ubiquitous-disco-jv44r5757wwc5g46-5000.app.github.dev/chain",
            "https://legendary-cod-97x4jq9645p3pqrq-5000.app.github.dev/chain",
            "https://laughing-space-giggle-5g4xv6w69xrp37qvj-5000.app.github.dev/chain",
            "https://psychic-fortnight-564rwxj46g43vv5q-5000.app.github.dev/chain"
        }

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

    def add_peer(self, peer: str):
        """Add a new peer to the network."""
        self.peers.add(peer)
        print(f"Peer {peer} added.")

@app.route('/add_peer', methods=['POST'])
def add_peer():
    data = request.get_json()
    peer = data.get('peer')
    if peer:
        blockchain.add_peer(peer)
        return jsonify({"message": f"Peer {peer} added."}), 200
    return jsonify({"error": "Peer not provided."}), 400

@app.route('/peers', methods=['GET'])
def get_peers():
    """Get the list of peers."""
    return jsonify(list(blockchain.peers)), 200

if __name__ == '__main__':
    blockchain = SimpleBlockchain('genesis_block.json')  # Adjust this to your genesis file
    app.run(host='0.0.0.0', port=5000)  # Change port as needed

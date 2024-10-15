import time
import hashlib
import json
import logging
import threading
import requests
import argparse
from flask import Flask, request, jsonify

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

class SimpleBlock:
    def __init__(self, index: int, timestamp: int, previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()  # Calculate hash upon creation

    def calculate_hash(self):
        """Calculate the hash of the block based on its timestamp and previous hash."""
        block_string = f"{self.timestamp}{self.previous_hash}".encode()
        return hashlib.sha256(block_string).hexdigest()  

    def to_dict(self):
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'hash': self.hash
        }

class SimpleBlockchain:
    def __init__(self, genesis_file: str, blockchain_file: str):
        self.chain = []
        self.genesis_file = genesis_file
        self.blockchain_file = blockchain_file
        self.load_genesis_block()
        self.load_chain()

    def load_genesis_block(self):
        """Load the genesis block from the genesis file."""
        try:
            with open(self.genesis_file, 'r') as f:
                data = json.load(f)
                self.chain.append(SimpleBlock(data['index'], data['timestamp'], data['previous_hash']))  # Create block without 'hash'
                logger.info("Genesis block loaded successfully.")
        except FileNotFoundError:
            logger.warning("Genesis block file not found. Creating a new genesis block.")
            self.create_genesis_block()
        except json.JSONDecodeError:
            logger.error("Error decoding JSON from the genesis file.")
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading the genesis block: {e}")

    def create_genesis_block(self):
        """Create the genesis block and save it to the genesis file."""
        logger.info("Creating genesis block...")
        genesis_block = SimpleBlock(0, int(time.time()), "0")
        self.chain.append(genesis_block)
        self.save_genesis_block()  # Save the genesis block to the file
        logger.info("Genesis block created and saved.")  

    def save_genesis_block(self):
        """Save the genesis block to the genesis file."""
        try:
            with open(self.genesis_file, 'w') as f:
                json.dump(self.chain[0].to_dict(), f)  # Save only the genesis block
            logger.info("Genesis block saved successfully.")
        except Exception as e:
            logger.error(f"Error saving genesis block: {e}")

    def load_chain(self):
        """Load the blockchain from the blockchain file."""
        try:
            with open(self.blockchain_file, 'r') as f:
                data = json.load(f)
                for block in data['chain']:
                    self.chain.append(SimpleBlock(block['index'], block['timestamp'], block['previous_hash']))  # Create block without 'hash'
                logger.info("Blockchain loaded successfully.")
        except FileNotFoundError:
            logger.warning("Blockchain file not found. Initializing a new blockchain.")
            self.save_chain()  # Save the initial state with the genesis block
        except json.JSONDecodeError:
            logger.error("Error decoding JSON from the blockchain file.")
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading the chain: {e}")

    def save_chain(self):
        """Save the current chain to the blockchain file."""
        try:
            logger.info("Saving blockchain state...")    
            with open(self.blockchain_file, 'w') as f:
                json.dump({'chain': [block.to_dict() for block in self.chain]}, f)
            logger.info("Blockchain state saved successfully.")
        except Exception as e:
            logger.error(f"Error saving blockchain state: {e}")

    def create_block(self):
        """Create a new block with the current timestamp."""
        if self.chain:
            last_block = self.chain[-1]
            current_time = int(time.time())
            new_block = SimpleBlock(
                index=len(self.chain),
                timestamp=current_time,
                previous_hash=last_block.hash
            )
            self.chain.append(new_block)  # Append the new block to the chain
            self.save_chain()  # Save the updated chain  
            logger.info(f"New block created: {new_block.to_dict()}")
            return new_block
        else:
            logger.warning("No blocks in the chain. Cannot create a new block.")
            return None

    def run(self):
        """Run the blockchain node to create a block every minute."""
        threading.Thread(target=self.run_flask, daemon=True).start()
        while True:
            time.sleep(60)  # Wait for 1 minute
            self.create_block()  # Create a new block    

    def run_flask(self):
        """Run the Flask app."""
        app.run(host='0.0.0.0', port=5000)  # Make sure to use the correct port

    def broadcast_chain(self, peers):
        """Broadcast the current blockchain to the specified peers."""
        for peer in peers:
            try:
                response = requests.post(f'http://{peer}/chain', json={'chain': [block.to_dict() for block in self.chain]})
                if response.status_code == 200:
                    logger.info(f"Successfully broadcasted to {peer}")
                else:
                    logger.error(f"Failed to broadcast to {peer}: {response.text}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Error connecting to peer {peer}: {e}")

# Flask routes
@app.route('/transactions', methods=['POST'])
def add_transaction():
    data = request.get_json()
    sender = data.get('sender')
    recipient = data.get('recipient')
    amount = data.get('amount')

    # For this simple implementation, we won't actually process transactions
    # but you can log or handle them as needed.
    logger.info(f"Transaction received: {data}")
    return jsonify({"message": "Transaction received."}), 200

@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify({'chain': [block.to_dict() for block in blockchain.chain]}), 200

@app.route('/chain', methods=['POST'])
def receive_chain():
    data = request.get_json()
    if 'chain' in data:
        logger.info("Received blockchain from peer.")    
        # Here you can implement logic to validate and possibly replace the local chain
        return jsonify({"message": "Blockchain received."}), 200
    return jsonify({"error": "Invalid data."}), 400       

def main():
    parser = argparse.ArgumentParser(description='Simple Blockchain Node')
    parser.add_argument('--genesis', type=str, default='genesis_block.json', help='Path to the genesis block file')
    parser.add_argument('--chain', type=str, default='blockchain.json', help='Path to the blockchain file')       
    parser.add_argument('--peers', type=str, nargs='*', help='List of peer addresses to broadcast to')

    args = parser.parse_args()

    # Initialize the blockchain
    global blockchain
    blockchain = SimpleBlockchain(args.genesis, args.chain)

    # Start the blockchain node
    blockchain.run()

    # Broadcast the blockchain state to peers if provided    
    if args.peers:
        blockchain.broadcast_chain(args.peers)

if __name__ == "__main__":
    main()

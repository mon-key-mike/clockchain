import argparse
import time
from node import SimpleBlockchain

def main():
    parser = argparse.ArgumentParser(description='Simple Blockchain Main')
    parser.add_argument('--genesis', type=str, default='genesis_block.json', help='Path to the genesis block file')
    parser.add_argument('--chain', type=str, default='blockchain.json', help='Path to the blockchain file')       
    parser.add_argument('--peers', type=str, nargs='*', help='List of peer addresses to broadcast to')

    args = parser.parse_args()

    # Initialize the blockchain
    blockchain = SimpleBlockchain(args.genesis, args.chain)

    # Create the genesis block if the chain is empty     
    if not blockchain.chain:
        print("Creating genesis block...")
        blockchain.create_block()  # Create the genesis block
        print("Genesis block created.")

    # Example: Adding blocks to the blockchain
    while True:
        time.sleep(60)  # Wait for 60 seconds
        print("Creating a new block...")
        new_block = blockchain.create_block()  # Create a new block with the current timestamp
        
        if new_block:
            print("New block created and added to the blockchain.")
        
            # Broadcast the current chain to peers if provided
            if args.peers:
                blockchain.broadcast_chain(args.peers)       

if __name__ == "__main__":
    main()

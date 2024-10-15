from blockchain import SimpleBlockchain

def main():
    # Initialize the blockchain with the genesis file
    blockchain = SimpleBlockchain('genesis_block.json')

    # Start your node and run the Flask app
    # Note: Ensure node.py runs the Flask app which is already implemented in node.py

if __name__ == "__main__":
    main()

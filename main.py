import hashlib
import json
import time
import requests
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uvicorn

class SimpleBlockchain:
    def __init__(self, genesis_file, blockchain_file):   
        self.genesis_file = genesis_file
        self.blockchain_file = blockchain_file
        self.chain = self.load_chain()

    def load_chain(self):
        try:
            with open(self.blockchain_file, 'r') as f:   
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_chain(self):
        with open(self.blockchain_file, 'w') as f:       
            json.dump(self.chain, f, indent=4)

    def create_block(self, data):
        block = {
            'index': len(self.chain),
            'timestamp': self.get_nist_time().isoformat(),
            'data': data,
            'previous_hash': self.chain[-1]['hash'] if self.chain else '0',
        }
        block['hash'] = self.hash_block(block)
        return block

    def hash_block(self, block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()  

    def add_block(self, block):
        if len(self.chain) == 0 or block['previous_hash'] == self.chain[-1]['hash']:
            self.chain.append(block)
            self.save_chain()
            return True
        return False

    def get_latest_blocks(self, limit=10):
        return self.chain[-limit:]

    def format_block_time(self, timestamp):
        return datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    def get_nist_time(self):
        """
        Get the current time from NIST using HTTP.       
        """
        try:
            response = requests.get('http://worldtimeapi.org/api/timezone/Etc/UTC')
            if response.status_code == 200:
                current_time = response.json()['utc_datetime']
                return datetime.fromisoformat(current_time.replace('Z', '+00:00')).replace(second=0, microsecond=0)
        except requests.RequestException:
            # Fallback to local time if NIST time is unavailable
            return datetime.utcnow().replace(second=0, microsecond=0)

    def create_block_per_minute(self):
        current_minute = self.get_nist_time()

        if not self.chain:
            print("Blockchain is empty. Creating genesis 
block...")
            new_block = self.create_block("Genesis Block")
        else:
            # Corrected timestamp key from 'time' to 'timestamp'
            last_block_time = datetime.fromisoformat(self.chain[-1]['timestamp'])
            if current_minute > last_block_time:
                data_to_hash = f"Block for minute: {current_minute.isoformat()}"
                new_block = self.create_block(data_to_hash)
            else:
                return None  # No new block if the time hasn't changed

        return new_block

    def perpetual_sync(self):
        while True:
            new_block = self.create_block_per_minute()   
            if new_block:
                if self.add_block(new_block):
                    print(f"Added new block at {new_block['timestamp']}")
                else:
                    print("Failed to add new block")     
            time.sleep(60)  # Wait until the next minute 

# FastAPI server for blockchain interactions
app = FastAPI()
blockchain = SimpleBlockchain('genesis_block.json', 'blockchain.json')

class BlockData(BaseModel):
    data: str

class PeerTime(BaseModel):
    peer_times: List[datetime]

@app.post("/blocks/")
async def create_block(block_data: BlockData):
    new_block = blockchain.create_block(block_data.data) 

    if blockchain.add_block(new_block):
        return {"message": "Block added successfully", "block": new_block}

    raise HTTPException(status_code=400, detail="Invalid 
block")

@app.get("/blocks/")
async def get_blocks(limit: int = 10):
    return blockchain.get_latest_blocks(limit)

@app.get("/blocks/{index}")
async def get_block(index: int):
    if 0 <= index < len(blockchain.chain):
        block = blockchain.chain[index]
        return {**block, 'formatted_time': blockchain.format_block_time(block['timestamp'])}
    raise HTTPException(status_code=404, detail="Block not found")

@app.post("/sync/")
async def sync_time(peer_time: PeerTime):
    """
    Peer synchronization endpoint to verify times across 
peers.
    """
    nist_time = blockchain.get_nist_time()
    peer_times = peer_time.peer_times
    consensus = all(nist_time == peer_time for peer_time 
in peer_times)

    if consensus:
        return {"message": "Times are synchronized."}    
    else:
        raise HTTPException(status_code=400, detail="Time mismatch between peers.")

if __name__ == "__main__":
    # Run perpetual blockchain syncing in the background 
    blockchain.perpetual_sync()

    # Run FastAPI server
    uvicorn.run(app, host="127.0.0.1", port=8000) 

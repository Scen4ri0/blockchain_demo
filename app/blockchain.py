import hashlib
import time
from .transaction import Transaction
import logging
logging.basicConfig(level=logging.INFO)

class Block:
    def __init__(self, index, transactions, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        transaction_data = "".join([
            f"{t.sender}->{t.recipient}:{t.amount}"
            if isinstance(t, Transaction) else f"{t['sender']}->{t['recipient']}:{t['amount']}"
            for t in self.transactions
        ])
        value = f"{self.index}{self.timestamp}{transaction_data}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(value.encode()).hexdigest()

    def mine_block(self, difficulty):
        target = "0" * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()
        logging.info(f"Block {self.index} mined with hash: {self.hash}")

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [
                tx.to_dict() if isinstance(tx, Transaction) else tx for tx in self.transactions
            ],
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.difficulty = 4
        self.mining_reward = 50

    def create_genesis_block(self):
        return Block(0, [], "0")

    def add_block(self, data):
        latest_block = self.chain[-1]
        if isinstance(data, list) and all(isinstance(t, Transaction) for t in data):
            transactions = data
        else:
            fake_transaction = Transaction("System", "Unknown", data, None)
            transactions = [fake_transaction]

        new_block = Block(len(self.chain), transactions, latest_block.hash)
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        logging.info(f"Block {new_block.index} added to the chain.")

    def add_transaction(self, transaction, user_keys):
        if not transaction.sender or not transaction.recipient or not transaction.amount:
            raise ValueError("Transaction must include sender, recipient, and amount.")

        if transaction.sender != "System":
            if transaction.sender not in user_keys:
                raise ValueError(f"Sender '{transaction.sender}' not found.")
            public_key = user_keys[transaction.sender].public_key()
            if not transaction.verify_signature(public_key):
                raise ValueError("Transaction signature is invalid.")

        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self, miner_address):
        if not self.pending_transactions:
            return "No transactions to mine."

        reward_transaction = Transaction("System", miner_address, self.mining_reward, None)
        self.pending_transactions.append(reward_transaction)

        new_block = Block(len(self.chain), self.pending_transactions, self.chain[-1].hash)
        new_block.mine_block(self.difficulty)

        self.chain.append(new_block)
        self.pending_transactions = []
        logging.info(f"Block {new_block.index} mined and added to the chain.")

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current.hash != current.calculate_hash():
                logging.error(f"Invalid hash at block {current.index}.")
                return False
            if current.previous_hash != previous.hash:
                logging.error(f"Invalid previous hash at block {current.index}.")
                return False
        logging.info("Blockchain is valid.")
        return True

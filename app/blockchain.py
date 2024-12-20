import hashlib
import time
from .transaction import Transaction
import logging

logging.basicConfig(level=logging.INFO)

class Block:
    def __init__(self, index, transactions, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions  # Список транзакций
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """Генерирует хэш для блока."""
        transaction_data = "".join([
            f"{t.sender}->{t.recipient}:{t.amount}" 
            if isinstance(t, Transaction) else str(t)
            for t in self.transactions
        ])
        value = f"{self.index}{self.timestamp}{transaction_data}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(value.encode()).hexdigest()

    def mine_block(self, difficulty):
        """Майнинг блока с заданной сложностью."""
        target = "0" * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()
        logging.info(f"Block {self.index} mined with hash: {self.hash}")

    def to_dict(self):
        """Преобразует блок в словарь для JSON-сериализации."""
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
        """Создает начальный (генезисный) блок."""
        return Block(0, [], "0")

    def add_block(self, data):
        """Добавляет новый блок с заданными данными."""
        latest_block = self.chain[-1]

        # Если это список транзакций
        if isinstance(data, list) and all(isinstance(t, Transaction) for t in data):
            transactions = data
        else:
            # Если это не транзакции, создаем фейковую транзакцию
            fake_transaction = Transaction("System", "Unknown", data, None)
            transactions = [fake_transaction]

        new_block = Block(len(self.chain), transactions, latest_block.hash)
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)

    def add_transaction(self, transaction, user_keys):
        """Добавляет транзакцию в список ожидающих."""
        if not transaction.sender or not transaction.recipient or not transaction.amount:
            raise ValueError("Transaction must include sender, recipient, and amount.")

        # Проверяем подпись для ненаградных транзакций
        if transaction.sender != "System":
            if transaction.sender not in user_keys:
                raise ValueError(f"Sender '{transaction.sender}' not found in user keys.")
            public_key = user_keys[transaction.sender].public_key()
            if not transaction.verify_signature(public_key):
                raise ValueError("Transaction signature is invalid.")

        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self, miner_address):
        """Майнинг блока с ожидающими транзакциями."""
        if not self.pending_transactions:
            return "No transactions to mine."

        # Добавляем вознаграждение за майнинг
        reward_transaction = Transaction("System", miner_address, self.mining_reward, None)
        self.pending_transactions.append(reward_transaction)

        # Создаем новый блок с ожидающими транзакциями
        new_block = Block(len(self.chain), self.pending_transactions[:], self.chain[-1].hash)
        new_block.mine_block(self.difficulty)

        # Добавляем блок в цепочку и очищаем список ожидающих транзакций
        self.chain.append(new_block)
        self.pending_transactions = []

    def is_chain_valid(self):
        """Проверка целостности цепочки."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # Проверяем текущий хэш
            if current.hash != current.calculate_hash():
                logging.error(f"Invalid hash at block {current.index}.")
                return False

            # Проверяем предыдущий хэш
            if current.previous_hash != previous.hash:
                logging.error(f"Invalid previous hash at block {current.index}.")
                return False

        logging.info("Blockchain is valid.")
        return True

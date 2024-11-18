import hashlib
import time
from .transaction import Transaction

class Block:
    def __init__(self, index, transactions, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        if isinstance(self.transactions, list):
            # Если transactions — это список объектов Transaction
            transaction_data = "".join([
                f"{t.sender}->{t.recipient}:{t.amount}" for t in self.transactions
            ])
        else:
            # Если transactions — это строка или другой тип данных
            transaction_data = str(self.transactions)

        value = f"{self.index}{self.timestamp}{transaction_data}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(value.encode()).hexdigest()

    def mine_block(self, difficulty):
        target = "0" * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.difficulty = 4
        self.mining_reward = 50

    def create_genesis_block(self):
        return Block(0, [], "0")

    def add_block(self, data):
        """Добавление блока: поддерживает как строковые данные, так и транзакции."""
        latest_block = self.chain[-1]

        # Если передан список транзакций
        if isinstance(data, list) and all(isinstance(t, Transaction) for t in data):
            new_block = Block(len(self.chain), data, latest_block.hash)
        else:
            # Если передана строка, создаем фейковую транзакцию
            fake_transaction = Transaction("System", "Unknown", data, None)
            new_block = Block(len(self.chain), [fake_transaction], latest_block.hash)

        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        
    def add_transaction(self, transaction):
        """Добавление транзакции в список ожидающих."""
        if not transaction.sender or not transaction.recipient or not transaction.amount:
            raise ValueError("Transaction must include sender, recipient, and amount.")
        
        # Системные транзакции (вознаграждения) не требуют проверки подписи
        if transaction.sender != "System" and not transaction.verify_signature(transaction.sender):
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
        new_block = Block(len(self.chain), self.pending_transactions, self.chain[-1].hash)
        new_block.mine_block(self.difficulty)

        # Добавляем блок в цепочку и очищаем список ожидающих транзакций
        self.chain.append(new_block)
        self.pending_transactions = []

    def is_chain_valid(self):
        """Проверка целостности цепочки."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True

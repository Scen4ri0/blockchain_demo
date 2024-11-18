from flask import Blueprint, jsonify, request, render_template
from .blockchain import Blockchain
from .transaction import Transaction
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
import base64

# Создаем экземпляр блокчейна
blockchain = Blockchain()
routes = Blueprint('routes', __name__)

# Генерация ключей для пользователей
user_keys = {
    "Alice": rsa.generate_private_key(public_exponent=65537, key_size=2048),
    "Bob": rsa.generate_private_key(public_exponent=65537, key_size=2048),
}

def get_public_key(user):
    return base64.b64encode(user_keys[user].public_key().public_bytes(
        encoding=Encoding.PEM,
        format=PublicFormat.SubjectPublicKeyInfo
    )).decode()

# === Маршруты ===
@routes.route('/')
def index():
    return render_template('index.html')

@routes.route('/api/create_transaction', methods=['POST'])
def create_transaction():
    data = request.json
    sender = data.get("sender")
    recipient = data.get("recipient")
    amount = data.get("amount")

    if not sender or not recipient or not amount:
        return jsonify({"error": "Missing transaction fields"}), 400

    if sender not in user_keys:
        return jsonify({"error": f"Sender '{sender}' not found"}), 400

    private_key = user_keys[sender]
    transaction = Transaction(sender, recipient, float(amount), private_key)

    # Добавляем транзакцию с передачей user_keys
    try:
        blockchain.add_transaction(transaction, user_keys)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"message": "Transaction added to pending transactions", "transaction": transaction.to_dict()})


@routes.route('/api/mine', methods=['POST'])
def mine_transactions():
    miner_address = request.json.get("miner", "Unknown Miner")
    if not miner_address:
        return jsonify({"error": "Miner address is required"}), 400

    # Майнинг транзакций
    message = blockchain.mine_pending_transactions(miner_address)

    # Форматируем данные для ответа
    chain_data = [
        {
            "index": block.index,
            "timestamp": block.timestamp,
            "transactions": [tx.to_dict() for tx in block.transactions],
            "previous_hash": block.previous_hash,
            "hash": block.hash,
        }
        for block in blockchain.chain
    ]

    return jsonify({"message": message, "chain": chain_data})


@routes.route('/api/pending_transactions', methods=['GET'])
def get_pending_transactions():
    transactions = [{
        "sender": tx.sender,
        "recipient": tx.recipient,
        "amount": tx.amount,
        "signature": tx.signature.hex()
    } for tx in blockchain.pending_transactions]
    return jsonify(transactions)

@routes.route('/api/public_keys', methods=['GET'])
def get_public_keys():
    public_keys = {
        user: base64.b64encode(keys.public_key().public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        )).decode()
        for user, keys in user_keys.items()
    }
    return jsonify(public_keys)

@routes.route('/api/add_block', methods=['POST'])
def add_block():
    data = request.json.get('data', 'No data provided')

    # Преобразуем данные в список транзакций или оставляем как строку
    if isinstance(data, list):
        transactions = [Transaction(tx["sender"], tx["recipient"], tx["amount"], None) for tx in data]
    else:
        transactions = data

    blockchain.add_block(transactions)
    return jsonify({
        "message": "Block added successfully",
        "chain": [
            {
                "index": block.index,
                "timestamp": block.timestamp,
                "transactions": [tx.to_dict() if isinstance(tx, Transaction) else tx for tx in block.transactions],
                "previous_hash": block.previous_hash,
                "hash": block.hash,
            }
            for block in blockchain.chain
        ]
    })


@routes.route('/api/chain', methods=['GET'])
def get_chain():
    try:
        chain_data = [block.to_dict() for block in blockchain.chain]
        return jsonify(chain_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@routes.route('/chain', methods=['GET'])
def chain_page():
    return render_template('chain.html')

@routes.route('/api/validate', methods=['GET'])
def validate_chain():
    validation_steps = []
    is_valid = True

    for i in range(1, len(blockchain.chain)):
        current = blockchain.chain[i]
        previous = blockchain.chain[i - 1]

        # Добавляем отладочную информацию
        validation_steps.append({
            "block": current.index,
            "step": "Start validation",
            "details": f"Starting validation for Block {current.index}..."
        })

        # Проверка хэша текущего блока
        calculated_hash = current.calculate_hash()
        validation_steps.append({
            "block": current.index,
            "step": "Hash validation",
            "details": f"Expected hash: {calculated_hash}, Actual hash: {current.hash}"
        })
        if current.hash != calculated_hash:
            validation_steps.append({
                "block": current.index,
                "status": "invalid",
                "step": "Hash mismatch",
                "details": f"Hash mismatch: Expected {calculated_hash}, but got {current.hash}"
            })
            is_valid = False
            continue

        # Проверка ссылки на предыдущий блок
        validation_steps.append({
            "block": current.index,
            "step": "Previous hash validation",
            "details": f"Previous hash: {current.previous_hash}, Expected: {previous.hash}"
        })
        if current.previous_hash != previous.hash:
            validation_steps.append({
                "block": current.index,
                "status": "invalid",
                "step": "Previous hash mismatch",
                "details": f"Previous hash mismatch: Expected {previous.hash}, but got {current.previous_hash}"
            })
            is_valid = False
            continue

        validation_steps.append({
            "block": current.index,
            "status": "valid",
            "step": "Validation successful",
            "details": "Block is valid and correctly linked."
        })

    # Финальный результат
    validation_steps.insert(0, {
        "block": "Summary",
        "step": "Validation Result",
        "details": "Blockchain is valid!" if is_valid else "Blockchain is invalid!",
        "status": "valid" if is_valid else "invalid"
    })

    return jsonify({
        "valid": is_valid,
        "steps": validation_steps
    })
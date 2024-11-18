import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.hashes import SHA256


class Transaction:
    def __init__(self, sender, recipient, amount, private_key=None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = None if sender == "System" else self.sign_transaction(private_key)

    def sign_transaction(self, private_key):
        if private_key is None:
            return None  # Нет подписи для системных транзакций
        message = f"{self.sender}->{self.recipient}:{self.amount}".encode()
        return private_key.sign(
            message,
            padding.PSS(mgf=padding.MGF1(SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            SHA256()
        )

    def verify_signature(self, public_key):
        if self.sender == "System":
            # Системные транзакции не требуют проверки подписи
            return True
        message = f"{self.sender}->{self.recipient}:{self.amount}".encode()
        try:
            public_key.verify(
                self.signature,
                message,
                padding.PSS(mgf=padding.MGF1(SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                SHA256()
            )
            return True
        except Exception as e:
            print(f"Verification failed for transaction {self.to_dict()}: {e}")
            return False

    def to_dict(self):
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "signature": self.signature.hex() if self.signature else None,
        }

    @staticmethod
    def from_dict(data):
        signature = base64.b64decode(data['signature']) if data['signature'] else None
        return Transaction(
            sender=data['sender'],
            recipient=data['recipient'],
            amount=data['amount'],
            private_key=None  # Приватный ключ не требуется для восстановления
        )

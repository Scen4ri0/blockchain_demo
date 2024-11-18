import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.hashes import SHA256


class Transaction:
    def __init__(self, sender, recipient, amount, private_key=None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = None
        if sender != "System" and private_key:
            self.signature = self.sign_transaction(private_key)

    def sign_transaction(self, private_key):
        """Подписывает транзакцию, если передан приватный ключ."""
        if private_key is None:
            raise ValueError("Private key is required to sign the transaction.")
        message = self._generate_message().encode()
        return private_key.sign(
            message,
            padding.PSS(mgf=padding.MGF1(SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            SHA256()
        )

    def verify_signature(self, public_key):
        """Проверяет подпись транзакции."""
        if self.sender == "System":
            return True  # Системные транзакции не требуют подписи
        if not self.signature:
            print(f"Transaction from {self.sender} to {self.recipient} has no signature.")
            return False
        try:
            message = self._generate_message().encode()
            public_key.verify(
                self.signature,
                message,
                padding.PSS(mgf=padding.MGF1(SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                SHA256()
            )
            return True
        except Exception as e:
            print(f"Signature verification failed: {e}")
            return False

    def to_dict(self):
        """Возвращает словарь с данными транзакции."""
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "signature": base64.b64encode(self.signature).decode() if self.signature else None,
        }

    @staticmethod
    def from_dict(data):
        """Восстанавливает транзакцию из словаря."""
        signature = base64.b64decode(data['signature']) if data.get('signature') else None
        transaction = Transaction(
            sender=data['sender'],
            recipient=data['recipient'],
            amount=data['amount'],
        )
        transaction.signature = signature
        return transaction

    def _generate_message(self):
        """Создает строку для подписания."""
        return f"{self.sender}->{self.recipient}:{self.amount}"

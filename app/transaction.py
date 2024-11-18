class Transaction:
    def __init__(self, sender, recipient, amount, private_key):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = self.sign_transaction(private_key)

    def sign_transaction(self, private_key):
        if private_key is None:
            # Если ключ отсутствует, создаем пустую подпись
            return b""
        message = f"{self.sender}->{self.recipient}:{self.amount}".encode()
        return private_key.sign(
            message,
            padding.PSS(mgf=padding.MGF1(SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            SHA256()
        )

    def verify_signature(self, public_key):
        message = f"{self.sender}->{self.recipient}:{self.amount}".encode()
        try:
            public_key.verify(
                self.signature,
                message,
                padding.PSS(mgf=padding.MGF1(SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                SHA256()
            )
            return True
        except:
            return False

    def to_dict(self):
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "signature": base64.b64encode(self.signature).decode('utf-8') if self.signature else None
        }

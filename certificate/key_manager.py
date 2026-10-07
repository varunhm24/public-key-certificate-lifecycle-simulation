from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from pathlib import Path


KEYS_FOLDER = Path("keys")


def generate_key_pair(user_id):
    """
    Generate an RSA public/private key pair for a user.
    """

    # Create keys directory if it doesn't exist
    KEYS_FOLDER.mkdir(exist_ok=True)

    # Generate RSA private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # Extract public key
    public_key = private_key.public_key()

    # File paths
    private_key_path = KEYS_FOLDER / f"{user_id}_private_key.pem"
    public_key_path = KEYS_FOLDER / f"{user_id}_public_key.pem"

    # Save private key
    with open(private_key_path, "wb") as file:
        file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    # Save public key
    with open(public_key_path, "wb") as file:
        file.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

    return private_key_path, public_key_path
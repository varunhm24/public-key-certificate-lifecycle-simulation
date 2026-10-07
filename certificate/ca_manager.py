from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from datetime import datetime, timedelta, timezone
from pathlib import Path


CA_FOLDER = Path("ca")


def create_ca():
    """
    Generate the Certificate Authority private key
    and self-signed CA certificate.
    """

    CA_FOLDER.mkdir(exist_ok=True)

    private_key_path = CA_FOLDER / "ca_private_key.pem"
    certificate_path = CA_FOLDER / "ca_certificate.pem"

    # If CA already exists, don't create another one
    if private_key_path.exists() and certificate_path.exists():
        print("CA already exists.")
        return private_key_path, certificate_path

    # Generate CA private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # CA public key
    public_key = private_key.public_key()

    # CA identity
    subject = issuer = x509.Name([
        x509.NameAttribute(
            NameOID.COUNTRY_NAME,
            "IN"
        ),
        x509.NameAttribute(
            NameOID.ORGANIZATION_NAME,
            "INS Certificate Authority"
        ),
        x509.NameAttribute(
            NameOID.COMMON_NAME,
            "INS Root CA"
        ),
    ])

    # Create self-signed CA certificate
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(public_key)
        .serial_number(x509.random_serial_number())
        .not_valid_before(
            datetime.now(timezone.utc)
        )
        .not_valid_after(
            datetime.now(timezone.utc) + timedelta(days=3650)
        )
        .add_extension(
            x509.BasicConstraints(
                ca=True,
                path_length=None
            ),
            critical=True
        )
        .sign(
            private_key,
            hashes.SHA256()
        )
    )

    # Save CA private key
    with open(private_key_path, "wb") as file:
        file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    # Save CA certificate
    with open(certificate_path, "wb") as file:
        file.write(
            certificate.public_bytes(
                serialization.Encoding.PEM
            )
        )

    return private_key_path, certificate_path
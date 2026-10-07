from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509.oid import NameOID
from pathlib import Path


CERTIFICATE_FOLDER = Path("certificates")


def create_csr(
    user_id,
    common_name,
    organization,
    country,
    email
):
    """
    Create a Certificate Signing Request (CSR).
    """

    CERTIFICATE_FOLDER.mkdir(exist_ok=True)

    # Load the user's private key
    private_key_path = Path("keys") / f"{user_id}_private_key.pem"

    with open(private_key_path, "rb") as file:
        private_key = serialization.load_pem_private_key(
            file.read(),
            password=None
        )

    # Create subject information
    subject = x509.Name([
        x509.NameAttribute(
            NameOID.COUNTRY_NAME,
            country
        ),
        x509.NameAttribute(
            NameOID.ORGANIZATION_NAME,
            organization
        ),
        x509.NameAttribute(
            NameOID.COMMON_NAME,
            common_name
        ),
        x509.NameAttribute(
            NameOID.EMAIL_ADDRESS,
            email
        ),
    ])

    # Build CSR
    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(subject)
        .sign(
            private_key,
            hashes.SHA256()
        )
    )

    # Save CSR
    csr_path = CERTIFICATE_FOLDER / f"{user_id}_request.csr"

    with open(csr_path, "wb") as file:
        file.write(
            csr.public_bytes(
                serialization.Encoding.PEM
            )
        )

    return csr_path
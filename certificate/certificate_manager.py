from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509.oid import ExtensionOID
from datetime import datetime, timedelta, timezone
from pathlib import Path

from database.database import get_connection

CERTIFICATE_FOLDER = Path("certificates")
CA_FOLDER = Path("ca")


def issue_certificate(user_id, validity_days=365):
    CERTIFICATE_FOLDER.mkdir(exist_ok=True)

    csr_path = CERTIFICATE_FOLDER / f"{user_id}_request.csr"
    ca_private_key_path = CA_FOLDER / "ca_private_key.pem"
    ca_certificate_path = CA_FOLDER / "ca_certificate.pem"
    certificate_path = CERTIFICATE_FOLDER / f"{user_id}_certificate.pem"

    with open(csr_path, "rb") as file:
        csr = x509.load_pem_x509_csr(file.read())

    with open(ca_private_key_path, "rb") as file:
        ca_private_key = serialization.load_pem_private_key(
            file.read(),
            password=None
        )

    with open(ca_certificate_path, "rb") as file:
        ca_certificate = x509.load_pem_x509_certificate(
            file.read()
        )

    if not csr.is_signature_valid:
        raise ValueError("CSR signature is invalid.")

    now = datetime.now(timezone.utc)
    expiry = now + timedelta(days=validity_days)

    certificate_builder = (
        x509.CertificateBuilder()
        .subject_name(csr.subject)
        .issuer_name(ca_certificate.subject)
        .public_key(csr.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(expiry)
    )

    try:
        san_extension = csr.extensions.get_extension_for_oid(
            ExtensionOID.SUBJECT_ALTERNATIVE_NAME
        )

        certificate_builder = certificate_builder.add_extension(
            san_extension.value,
            critical=san_extension.critical
        )

    except x509.ExtensionNotFound:
        pass

    certificate_builder = certificate_builder.add_extension(
        x509.BasicConstraints(
            ca=False,
            path_length=None
        ),
        critical=True
    )

    certificate = certificate_builder.sign(
        private_key=ca_private_key,
        algorithm=hashes.SHA256()
    )

    with open(certificate_path, "wb") as file:
        file.write(
            certificate.public_bytes(
                serialization.Encoding.PEM
            )
        )

    # Store certificate in SQLite
    connection = get_connection()
    cursor = connection.cursor()
    
        # Mark previous active certificates as renewed
    cursor.execute(
        """
        UPDATE certificates
        SET status = 'RENEWED'
        WHERE user_id = ?
        AND status = 'ACTIVE'
        """,
        (user_id,)
    )

    cursor.execute(
        """
        INSERT INTO certificates (
            user_id,
            serial_number,
            certificate_path,
            issued_at,
            expires_at,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            str(certificate.serial_number),
            str(certificate_path),
            now.isoformat(),
            expiry.isoformat(),
            "ACTIVE"
        )
    )

    connection.commit()
    connection.close()

    return certificate_path
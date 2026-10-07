from certificate.revocation_manager import is_revoked
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import padding
from datetime import datetime, timezone
from pathlib import Path
from database.database import get_connection

CA_FOLDER = Path("ca")
CERTIFICATE_FOLDER = Path("certificates")


def verify_certificate(user_id):
    """
    Verify an applicant's certificate against our CA.
    """

    certificate_path = (
        CERTIFICATE_FOLDER / f"{user_id}_certificate.pem"
    )

    ca_certificate_path = (
        CA_FOLDER / "ca_certificate.pem"
    )

    # Check certificate exists
    if not certificate_path.exists():
        return {
            "valid": False,
            "message": "Certificate not found."
        }

    # Check CA certificate exists
    if not ca_certificate_path.exists():
        return {
            "valid": False,
            "message": "CA certificate not found."
        }

    # Load applicant certificate
    with open(certificate_path, "rb") as file:
        certificate = x509.load_pem_x509_certificate(
            file.read()
        )

    # Load CA certificate
    with open(ca_certificate_path, "rb") as file:
        ca_certificate = x509.load_pem_x509_certificate(
            file.read()
        )

    # Check issuer
    if certificate.issuer != ca_certificate.subject:
        return {
            "valid": False,
            "message": "Certificate issuer is not trusted."
        }

    # Check validity dates
    current_time = datetime.now(timezone.utc)

    if current_time < certificate.not_valid_before_utc:
        return {
            "valid": False,
            "message": "Certificate is not yet valid."
        }

    if current_time > certificate.not_valid_after_utc:
        return {
            "valid": False,
            "message": "Certificate has expired."
        }

    # Check revocation status
        # Check database lifecycle status
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT status
        FROM certificates
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id,)
    )

    database_record = cursor.fetchone()

    connection.close()

    if database_record:
        status = database_record[0]

        if status == "REVOKED":
            return {
                "valid": False,
                "message": "Certificate has been revoked."
            }

        if status == "EXPIRED":
            return {
                "valid": False,
                "message": "Certificate has expired."
            }

    # Verify CA signature
    try:
        ca_certificate.public_key().verify(
            certificate.signature,
            certificate.tbs_certificate_bytes,
            padding.PKCS1v15(),
            certificate.signature_hash_algorithm
        )

    except Exception:
        return {
            "valid": False,
            "message": "Certificate signature verification failed."
        }

    return {
        "valid": True,
        "message": "Certificate is valid and trusted."
    }
from certificate.csr_manager import create_csr
from certificate.certificate_manager import issue_certificate
from pathlib import Path


def renew_certificate(
    user_id,
    common_name,
    organization,
    country,
    email,
    validity_days=365
):
    """
    Renew a user's certificate.
    """

    # Create a new CSR
    csr_path = create_csr(
        user_id=user_id,
        common_name=common_name,
        organization=organization,
        country=country,
        email=email
    )

    # Issue a new certificate
    certificate_path = issue_certificate(
        user_id=user_id,
        validity_days=validity_days
    )

    return csr_path, certificate_path
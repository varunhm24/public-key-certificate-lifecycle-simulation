from cryptography import x509
from cryptography.hazmat.primitives import serialization


certificate_path = "certificates/user1_certificate.pem"


with open(certificate_path, "rb") as file:
    certificate = x509.load_pem_x509_certificate(
        file.read()
    )


print("=" * 60)
print("CERTIFICATE INFORMATION")
print("=" * 60)

print("Certificate Version:")
print(certificate.version)

print()

print("Serial Number:")
print(certificate.serial_number)

print()

print("Subject:")
print(certificate.subject)

print()

print("Issuer:")
print(certificate.issuer)

print()

print("Valid From:")
print(certificate.not_valid_before_utc)

print()

print("Valid Until:")
print(certificate.not_valid_after_utc)

print()

print("Signature Algorithm:")
print(certificate.signature_hash_algorithm.name)

print()

print("Public Key:")
print(
    certificate.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
)

print("=" * 60)
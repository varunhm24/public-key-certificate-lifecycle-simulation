from certificate.renewal_manager import renew_certificate


csr_path, certificate_path = renew_certificate(
    user_id="user1",
    common_name="Varun H M",
    organization="VTU",
    country="IN",
    email="varun@example.com",
    validity_days=365
)

print("=" * 60)
print("CERTIFICATE RENEWAL")
print("=" * 60)
print()

print("New CSR:")
print(csr_path)

print()

print("New Certificate:")
print(certificate_path)

print()

print("Certificate renewed successfully!")

print("=" * 60)
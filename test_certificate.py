from certificate.certificate_manager import issue_certificate


certificate_path = issue_certificate(
    user_id="user1",
    validity_days=365
)

print("Certificate issued successfully!")
print()
print("Certificate:")
print(certificate_path)
from certificate.ca_manager import create_ca


private_key, certificate = create_ca()

print("Certificate Authority created successfully!")

print()
print("CA Private Key:")
print(private_key)

print()
print("CA Certificate:")
print(certificate)
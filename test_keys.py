from certificate.key_manager import generate_key_pair


private_key, public_key = generate_key_pair("user1")

print("Key generation successful!")

print("Private Key:")
print(private_key)

print()

print("Public Key:")
print(public_key)
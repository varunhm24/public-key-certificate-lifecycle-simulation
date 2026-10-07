from certificate.verifier import verify_certificate


result = verify_certificate("user1")


print("=" * 60)
print("CERTIFICATE VERIFICATION")
print("=" * 60)

print()

if result["valid"]:
    print("STATUS: VALID")
    print(result["message"])
else:
    print("STATUS: INVALID")
    print(result["message"])

print()
print("=" * 60)
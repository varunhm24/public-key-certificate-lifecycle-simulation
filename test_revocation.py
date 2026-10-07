from certificate.revocation_manager import (
    revoke_certificate,
    is_revoked,
    get_revocation_details
)

user_id = "user1"

print("=" * 60)
print("CERTIFICATE REVOCATION TEST")
print("=" * 60)
print()

print("Revoking certificate...")

revoke_certificate(
    user_id,
    "User No Longer Authorized"
)

print("Certificate revoked successfully!")
print()

print("Checking revocation status...")

if is_revoked(user_id):
    print("STATUS: REVOKED")

    details = get_revocation_details(user_id)

    print("Reason:", details["reason"])
    print("Revoked At:", details["revoked_at"])
else:
    print("STATUS: ACTIVE")

print()
print("=" * 60)
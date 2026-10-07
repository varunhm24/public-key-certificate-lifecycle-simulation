from certificate.expiration_manager import expire_certificate
from database.database import get_connection


user_id = "user2"

print("=" * 60)
print("CERTIFICATE EXPIRATION TEST")
print("=" * 60)
print()

success = expire_certificate(user_id)

if success:
    print("Certificate marked as EXPIRED.")
else:
    print("No ACTIVE certificate found.")

print()

connection = get_connection()
cursor = connection.cursor()

cursor.execute(
    """
    SELECT
        user_id,
        serial_number,
        status
    FROM certificates
    WHERE user_id = ?
    ORDER BY id DESC
    """,
    (user_id,)
)

records = cursor.fetchall()

for record in records:
    print("User ID:", record[0])
    print("Serial Number:", record[1])
    print("Status:", record[2])
    print()

connection.close()

print("=" * 60)
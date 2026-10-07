from database.database import get_connection

connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
    SELECT
        user_id,
        serial_number,
        status,
        issued_at,
        expires_at
    FROM certificates
""")

records = cursor.fetchall()

print("=" * 70)
print("CERTIFICATE DATABASE RECORDS")
print("=" * 70)

for record in records:
    print()
    print("User ID:", record[0])
    print("Serial Number:", record[1])
    print("Status:", record[2])
    print("Issued At:", record[3])
    print("Expires At:", record[4])

connection.close()

print()
print("=" * 70)
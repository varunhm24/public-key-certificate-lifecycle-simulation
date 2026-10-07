from certificate.csr_manager import create_csr


csr_path = create_csr(
    user_id="user1",
    common_name="Varun H M",
    organization="VTU",
    country="IN",
    email="varun@example.com"
)

print("CSR generation successful!")
print("CSR file:")
print(csr_path)

from certificate.csr_manager import create_csr


csr_path = create_csr(
    user_id="user1",
    common_name="Varun H M",
    organization="VTU",
    country="IN",
    email="varun@example.com"
)

print("CSR generation successful!")
print("CSR file:")
print(csr_path)
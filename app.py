from flask import Flask, render_template, request, redirect, url_for

from certificate.key_manager import generate_key_pair
from certificate.csr_manager import create_csr
from certificate.ca_manager import create_ca
from certificate.certificate_manager import issue_certificate
from certificate.verifier import verify_certificate
from certificate.revocation_manager import revoke_certificate
from certificate.expiration_manager import expire_certificate

from database.database import get_connection, initialize_database
from database.audit import log_action, get_logs

from datetime import datetime, timezone


from cryptography import x509
from cryptography.hazmat.primitives import serialization
from pathlib import Path

from flask import send_file


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)


# =========================================================
# INITIALIZE DATABASE AND ROOT CA
# =========================================================

initialize_database()
create_ca()


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# CERTIFICATE DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    connection = get_connection()
    cursor = connection.cursor()

    # Get all certificates
    cursor.execute(
        """
        SELECT
            id,
            user_id,
            serial_number,
            issued_at,
            expires_at,
            status,
            revocation_reason,
            revoked_at
        FROM certificates
        ORDER BY id DESC
        """
    )

    certificates = cursor.fetchall()

    # Count ACTIVE certificates
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM certificates
        WHERE status = 'ACTIVE'
        """
    )

    active_count = cursor.fetchone()[0]

    # Count REVOKED certificates
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM certificates
        WHERE status = 'REVOKED'
        """
    )

    revoked_count = cursor.fetchone()[0]

    # Count EXPIRED certificates
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM certificates
        WHERE status = 'EXPIRED'
        """
    )

    expired_count = cursor.fetchone()[0]

    # Count RENEWED certificates
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM certificates
        WHERE status = 'RENEWED'
        """
    )

    renewed_count = cursor.fetchone()[0]

    connection.close()

    return render_template(
        "dashboard.html",
        certificates=certificates,
        active_count=active_count,
        revoked_count=revoked_count,
        expired_count=expired_count,
        renewed_count=renewed_count
    )


# =========================================================
# REGISTER APPLICANT
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # ---------------------------------------------
        # Get form data
        # ---------------------------------------------

        user_id = request.form["user_id"].strip()
        common_name = request.form["common_name"].strip()
        organization = request.form["organization"].strip()
        country = request.form["country"].strip().upper()
        email = request.form["email"].strip()

        # ---------------------------------------------
        # Check if User ID already exists
        # ---------------------------------------------

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT user_id
            FROM applicants
            WHERE user_id = ?
            """,
            (user_id,)
        )

        existing_user = cursor.fetchone()

        connection.close()

        if existing_user:

            return render_template(
                "register.html",
                error=(
                    "User ID already exists. "
                    "Please choose another User ID."
                )
            )

        # ---------------------------------------------
        # Generate RSA key pair
        # ---------------------------------------------

        generate_key_pair(user_id)

        # ---------------------------------------------
        # Generate CSR
        # ---------------------------------------------

        create_csr(
            user_id=user_id,
            common_name=common_name,
            organization=organization,
            country=country,
            email=email
        )

        # ---------------------------------------------
        # Store applicant in database
        # ---------------------------------------------

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO applicants
            (
                user_id,
                common_name,
                organization,
                country,
                email,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                common_name,
                organization,
                country,
                email,
                datetime.now(timezone.utc).isoformat()
            )
        )

        connection.commit()
        connection.close()

        # ---------------------------------------------
        # Issue X.509 certificate
        # ---------------------------------------------

        issue_certificate(user_id)

        # ---------------------------------------------
        # Record audit log
        # ---------------------------------------------

        log_action(
            user_id,
            "CERTIFICATE_ISSUED",
            "New X.509 certificate issued."
        )

        # ---------------------------------------------
        # Redirect to dashboard
        # ---------------------------------------------

        return redirect(url_for("dashboard"))

    # GET request
    return render_template("register.html")


# =========================================================
# VERIFY CERTIFICATE
# =========================================================

@app.route("/verify/<user_id>")
def verify(user_id):

    result = verify_certificate(user_id)

    log_action(
        user_id,
        "CERTIFICATE_VERIFIED",
        result["message"]
    )

    return render_template(
        "verify.html",
        user_id=user_id,
        result=result
    )


# =========================================================
# REVOKE CERTIFICATE
# =========================================================

@app.route("/revoke/<user_id>", methods=["POST"])
def revoke(user_id):

    reason = request.form.get(
        "reason",
        "User No Longer Authorized"
    )

    success = revoke_certificate(
        user_id,
        reason
    )

    if success:

        log_action(
            user_id,
            "CERTIFICATE_REVOKED",
            reason
        )

    return redirect(url_for("dashboard"))


# =========================================================
# RENEW CERTIFICATE
# =========================================================

@app.route("/renew/<user_id>", methods=["POST"])
def renew(user_id):

    # ---------------------------------------------
    # Get applicant information
    # ---------------------------------------------

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            common_name,
            organization,
            country,
            email
        FROM applicants
        WHERE user_id = ?
        """,
        (user_id,)
    )

    applicant = cursor.fetchone()

    connection.close()

    if applicant is None:

        return "Applicant not found.", 404

    common_name = applicant[0]
    organization = applicant[1]
    country = applicant[2]
    email = applicant[3]

    # ---------------------------------------------
    # Generate new RSA key pair
    # ---------------------------------------------

    generate_key_pair(user_id)

    # ---------------------------------------------
    # Generate new CSR
    # ---------------------------------------------

    create_csr(
        user_id=user_id,
        common_name=common_name,
        organization=organization,
        country=country,
        email=email
    )

    # ---------------------------------------------
    # Issue renewed certificate
    # ---------------------------------------------

    issue_certificate(
        user_id,
        validity_days=365
    )

    # ---------------------------------------------
    # Audit log
    # ---------------------------------------------

    log_action(
        user_id,
        "CERTIFICATE_RENEWED",
        "Certificate renewed for 365 days."
    )

    return redirect(url_for("dashboard"))


# =========================================================
# CERTIFICATE DETAILS
# =========================================================

@app.route("/certificate/<int:certificate_id>")
def certificate_details(certificate_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            user_id,
            serial_number,
            issued_at,
            expires_at,
            status,
            revocation_reason,
            revoked_at
        FROM certificates
        WHERE id = ?
        """,
        (certificate_id,)
    )

    certificate = cursor.fetchone()

    connection.close()

    if certificate is None:

        return "Certificate not found.", 404

    return render_template(
        "certificate.html",
        certificate=certificate
    )


# =========================================================
# AUDIT LOGS
# =========================================================

@app.route("/logs")
def logs():

    logs = get_logs()

    return render_template(
        "logs.html",
        logs=logs
    )


# =========================================================
# SIMULATE CERTIFICATE EXPIRATION
# =========================================================

@app.route("/expire/<user_id>", methods=["POST"])
def expire(user_id):

    success = expire_certificate(user_id)

    if success:

        log_action(
            user_id,
            "CERTIFICATE_EXPIRED",
            "Certificate expiration simulated."
        )

    return redirect(url_for("dashboard"))


@app.route("/ca")
def ca_management():

    ca_certificate_path = Path("ca/ca_certificate.pem")

    if not ca_certificate_path.exists():
        return "CA certificate not found.", 404

    with open(ca_certificate_path, "rb") as file:
        ca_certificate = x509.load_pem_x509_certificate(
            file.read()
        )

    subject = ca_certificate.subject
    issuer = ca_certificate.issuer

    common_name = subject.get_attributes_for_oid(
        x509.NameOID.COMMON_NAME
    )[0].value

    organization = subject.get_attributes_for_oid(
        x509.NameOID.ORGANIZATION_NAME
    )[0].value

    serial_number = str(
        ca_certificate.serial_number
    )

    not_valid_before = (
        ca_certificate.not_valid_before_utc
    )

    not_valid_after = (
        ca_certificate.not_valid_after_utc
    )

    public_key = ca_certificate.public_key()

    key_size = public_key.key_size

    signature_algorithm = (
        ca_certificate.signature_hash_algorithm.name
    )

    return render_template(
        "ca.html",
        common_name=common_name,
        organization=organization,
        serial_number=serial_number,
        issuer=issuer.rfc4514_string(),
        subject=subject.rfc4514_string(),
        valid_from=not_valid_before,
        valid_until=not_valid_after,
        key_size=key_size,
        signature_algorithm=signature_algorithm,
        certificate_path=str(
            ca_certificate_path
        )
    )


@app.route("/download/certificate/<user_id>")
def download_certificate(user_id):

    certificate_path = Path(
        f"certificates/{user_id}_certificate.pem"
    )

    if not certificate_path.exists():
        return "Certificate not found.", 404

    return send_file(
        certificate_path,
        as_attachment=True,
        download_name=f"{user_id}_certificate.pem",
        mimetype="application/x-pem-file"
    )
    
    
@app.route("/download/public-key/<user_id>")
def download_public_key(user_id):

    public_key_path = Path(
        f"keys/{user_id}_public_key.pem"
    )

    if not public_key_path.exists():
        return "Public key not found.", 404

    return send_file(
        public_key_path,
        as_attachment=True,
        download_name=f"{user_id}_public_key.pem",
        mimetype="application/x-pem-file"
    )
    
@app.route("/certificate/pem/<user_id>")
def certificate_pem(user_id):

    certificate_path = Path(
        f"certificates/{user_id}_certificate.pem"
    )

    if not certificate_path.exists():
        return "Certificate not found.", 404

    with open(certificate_path, "r") as file:
        certificate_data = file.read()

    return render_template(
        "pem_viewer.html",
        user_id=user_id,
        certificate_data=certificate_data
    )

# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run()
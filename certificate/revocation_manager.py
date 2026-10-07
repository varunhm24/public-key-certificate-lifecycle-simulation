from database.database import get_connection
from datetime import datetime, timezone


def revoke_certificate(user_id, reason):
    """
    Revoke the currently active certificate of a user.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM certificates
        WHERE user_id = ?
        AND status = 'ACTIVE'
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id,)
    )

    certificate = cursor.fetchone()

    if certificate is None:
        connection.close()
        return False

    certificate_id = certificate[0]

    revoked_at = datetime.now(timezone.utc).isoformat()

    cursor.execute(
        """
        UPDATE certificates
        SET status = 'REVOKED',
            revocation_reason = ?,
            revoked_at = ?
        WHERE id = ?
        """,
        (
            reason,
            revoked_at,
            certificate_id
        )
    )

    connection.commit()
    connection.close()

    return True


def is_revoked(user_id):
    """
    Check whether the latest certificate is revoked.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT status
        FROM certificates
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id,)
    )

    result = cursor.fetchone()

    connection.close()

    if result is None:
        return False

    return result[0] == "REVOKED"


def get_revocation_details(user_id):
    """
    Get revocation information.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            revocation_reason,
            revoked_at
        FROM certificates
        WHERE user_id = ?
        AND status = 'REVOKED'
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id,)
    )

    result = cursor.fetchone()

    connection.close()

    if result is None:
        return None

    return {
        "reason": result[0],
        "revoked_at": result[1]
    }
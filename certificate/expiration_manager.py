from database.database import get_connection


def expire_certificate(user_id):
    """
    Simulate expiration of the latest active certificate.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE certificates
        SET status = 'EXPIRED'
        WHERE id = (
            SELECT id
            FROM certificates
            WHERE user_id = ?
            AND status = 'ACTIVE'
            ORDER BY id DESC
            LIMIT 1
        )
        """,
        (user_id,)
    )

    connection.commit()

    updated = cursor.rowcount

    connection.close()

    return updated > 0
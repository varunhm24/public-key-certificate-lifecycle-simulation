from database.database import get_connection
from datetime import datetime, timezone


def log_action(user_id, action, details=""):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO audit_logs
        (user_id, action, details, timestamp)
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            action,
            details,
            datetime.now(timezone.utc).isoformat()
        )
    )

    connection.commit()
    connection.close()


def get_logs():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            user_id,
            action,
            details,
            timestamp
        FROM audit_logs
        ORDER BY id DESC
        """
    )

    logs = cursor.fetchall()

    connection.close()

    return logs
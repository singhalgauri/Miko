# Owner: Person 2
# Purpose: Activity log tracking and one-click undo management
# TODO(person2): Implement real reversible file/email operations and undo verification

import json
import uuid
from typing import Any

from backend.app.core.db import get_db_connection
from backend.app.core.logging import logger


def log_action(
    action_type: str,
    params: dict[str, Any],
    agent: str,
    provider: str,
    status: str = "completed",
    undo_payload: dict[str, Any] | None = None,
) -> str:
    """Logs an executed action to the activity log, recording the model provider.

    Returns the generated action ID.
    """
    action_id = str(uuid.uuid4())
    logger.info("Logging action [%s] type=%s provider=%s", action_id, action_type, provider)

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO activity_log (id, action_type, params, agent, provider, status, undo_payload)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                action_id,
                action_type,
                json.dumps(params),
                agent,
                provider,
                status,
                json.dumps(undo_payload) if undo_payload else None,
            ),
        )
        conn.commit()
        return action_id
    finally:
        conn.close()


def get_activity_logs(limit: int = 50) -> list[dict[str, Any]]:
    """Retrieves recent activity logs."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, action_type, params, agent, provider, status, undo_payload, created_at
            FROM activity_log
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        result = []
        for row in rows:
            item = dict(row)
            try:
                item["params"] = json.loads(item["params"])
            except Exception:
                pass
            if item.get("undo_payload"):
                try:
                    item["undo_payload"] = json.loads(item["undo_payload"])
                except Exception:
                    pass
            result.append(item)
        return result
    finally:
        conn.close()


def undo(action_id: str) -> bool:
    """Reverts an action using its stored undo_payload.

    Returns True if successfully undone.
    """
    logger.info("Undoing action [%s]", action_id)
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT action_type, undo_payload, status FROM activity_log WHERE id = ?",
            (action_id,),
        )
        row = cursor.fetchone()
        if not row:
            logger.warning("Action %s not found for undo", action_id)
            return False

        # TODO(person2): Implement real tool undo execution dispatching
        cursor.execute(
            "UPDATE activity_log SET status = 'undone' WHERE id = ?",
            (action_id,),
        )
        conn.commit()
        return True
    finally:
        conn.close()

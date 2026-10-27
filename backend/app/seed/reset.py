# Owner: Person 3
# Purpose: Resets SQLite database and recreates synthetic seed data for testing and demo
# TODO(person3): Add optional reset for file organisation downloads directory

from typing import Any

from backend.app.core.db import get_db_connection, init_db
from backend.app.core.logging import logger


def reset_all_sample_data() -> dict[str, Any]:
    """Resets database tables and seeds demo activity records and tasks."""
    logger.info("Resetting sample data to factory baseline")
    init_db()

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Clean existing tables
        cursor.execute("DELETE FROM activity_log;")
        cursor.execute("DELETE FROM tasks;")

        # Seed sample activity entries
        cursor.execute(
            """
            INSERT INTO activity_log (id, action_type, params, agent, provider, status, undo_payload)
            VALUES
            ('seed-act-1', 'file.move', '{"source": "Downloads/invoice_102.pdf", "destination": "Documents/Invoices/invoice_102.pdf"}', 'file_organiser', 'mock', 'completed', '{"action_type": "file.move", "reverse_params": {"source": "Documents/Invoices/invoice_102.pdf", "destination": "Downloads/invoice_102.pdf"}}'),
            ('seed-act-2', 'email.draft', '{"recipient": "sarah.lead@company.com", "subject": "Draft reply to roadmap"}', 'inbox', 'nebius', 'completed', NULL),
            ('seed-act-3', 'document.search', '{"query": "termination notice period"}', 'document', 'local', 'completed', NULL);
            """
        )

        # Seed sample tasks
        cursor.execute(
            """
            INSERT INTO tasks (id, title, agent, status)
            VALUES
            ('task-1', 'Triage morning inbox', 'inbox', 'completed'),
            ('task-2', 'Organise Downloads directory', 'file_organiser', 'pending'),
            ('task-3', 'Generate daily briefing', 'briefing', 'completed');
            """
        )

        conn.commit()
        return {"status": "success", "message": "Sample data reset successfully", "seeded_items": 3}
    finally:
        conn.close()

# Owner: Person 2
# Purpose: Smoke tests for Permission Gateway policies and activity logging
# TODO(person2): Add tests for parameter schema validation errors

from backend.app.core.db import init_db
from backend.app.gateway.permission_gateway import ApprovalRequired, Result, execute_tool


def test_permission_gateway_policies():
    """Verify permission gateway routes actions according to security policy."""
    init_db()

    # 1. Test 'ask_first' policy (file.move defaults to ask_first)
    res_approval = execute_tool(
        action_type="file.move",
        params={"source": "test.txt", "destination": "docs/test.txt"},
        agent="file_organiser",
        provider="mock",
    )
    assert isinstance(res_approval, ApprovalRequired)
    assert res_approval.action_type == "file.move"
    assert res_approval.status == "pending"

    # 2. Test 'never' policy (file.delete defaults to never)
    res_never = execute_tool(
        action_type="file.delete",
        params={"path": "test.txt"},
        agent="file_organiser",
        provider="mock",
    )
    assert isinstance(res_never, Result)
    assert res_never.success is False
    assert "Permission denied" in (res_never.error or "")

    # 3. Test 'act_alone' policy (email.draft defaults to act_alone)
    res_act = execute_tool(
        action_type="email.draft",
        params={"recipient": "user@test.com", "subject": "Hi", "body": "Hello"},
        agent="inbox",
        provider="mock",
    )
    assert isinstance(res_act, Result)
    assert res_act.success is True
    assert res_act.action_id is not None

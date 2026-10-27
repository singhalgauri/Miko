# Owner: Person 2
# Purpose: Gateway package initialization
# TODO(person2): Export gateway functions and approval models

from backend.app.gateway.permission_gateway import ApprovalRequired, Result, execute_tool

__all__ = ["execute_tool", "Result", "ApprovalRequired"]

# Owner: Person 2
# Purpose: LangGraph workflow for directory scanning and file reorganization with approval pauses
# TODO(person2): Add rollback compensation node if a batch move partially fails

from typing import Any, TypedDict

from backend.app.core.logging import logger
from backend.app.providers.base import ModelProvider


class FileOrganiserState(TypedDict, total=False):
    target_dir: str
    discovered_files: list[str]
    proposed_moves: list[dict[str, str]]
    pending_approval: dict[str, Any] | None
    status: str


def create_file_organiser_graph(provider: ModelProvider):
    """Creates LangGraph file organiser workflow with approval-pause node for file operations."""

    def scan_directory_node(state: FileOrganiserState) -> FileOrganiserState:
        logger.info("FileOrganiserGraph: Scanning target directory %s", state.get("target_dir"))
        return {
            **state,
            "discovered_files": ["receipt_oct.pdf", "family_photo.jpg"],
            "status": "scanned",
        }

    def plan_organisation_node(state: FileOrganiserState) -> FileOrganiserState:
        logger.info("FileOrganiserGraph: Generating file move plan with provider %s", provider.name)
        moves = [
            {"source": "Downloads/receipt_oct.pdf", "destination": "Documents/Receipts/receipt_oct.pdf"},
            {"source": "Downloads/family_photo.jpg", "destination": "Pictures/family_photo.jpg"},
        ]
        return {**state, "proposed_moves": moves, "status": "planned"}

    def approval_pause_node(state: FileOrganiserState) -> FileOrganiserState:
        logger.info("FileOrganiserGraph: Pausing for user approval before moving files")
        approval = {
            "action": "file.move",
            "items": state.get("proposed_moves", []),
            "prompt": "Approve moving 2 files to organised folders?",
        }
        return {**state, "pending_approval": approval, "status": "paused_for_approval"}

    def execute_moves_node(state: FileOrganiserState) -> FileOrganiserState:
        logger.info("FileOrganiserGraph: Executing approved file moves")
        return {**state, "status": "completed"}

    return {
        "nodes": {
            "scan": scan_directory_node,
            "plan": plan_organisation_node,
            "approval_pause": approval_pause_node,
            "execute": execute_moves_node,
        },
        "entry_point": "scan",
    }

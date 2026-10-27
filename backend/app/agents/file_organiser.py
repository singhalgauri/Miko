# Owner: Person 2
# Purpose: Autonomous file organising agent with undo support
# TODO(person2): Add file extension clustering, date-based sorting, and duplicate file hashing

from typing import Any

from backend.app.core.logging import logger
from backend.app.providers.base import ModelProvider
from backend.app.tools.files import move_file


class FileOrganiserAgent:
    """Scans cluttered directories and organises them into structured folders."""

    def __init__(self, provider: ModelProvider):
        self.provider = provider

    async def organise_directory(self, target_dir: str = "Downloads") -> dict[str, Any]:
        """Proposes and executes folder organization with gateway-enforced approvals."""
        logger.info("FileOrganiserAgent organising '%s' with provider='%s'", target_dir, self.provider.name)

        # Provider reasoning turn to propose organization structure
        chat_res = await self.provider.chat(
            messages=[
                {
                    "role": "user",
                    "content": f"Propose clean organization rules for directory: {target_dir}",
                }
            ]
        )

        # Trigger move tool via gateway (this will return ApprovalRequired if ask_first is set)
        move_outcome = move_file(
            source=f"{target_dir}/receipt_1027.pdf",
            destination="Documents/Receipts/receipt_1027.pdf",
            agent="file_organiser",
            provider=self.provider.name,
        )

        return {
            "agent": "file_organiser",
            "provider": self.provider.name,
            "target_dir": target_dir,
            "proposal": chat_res.content,
            "operation": move_outcome.model_dump(),
        }

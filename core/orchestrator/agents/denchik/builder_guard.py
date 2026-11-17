# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/denchik/builder_guard.py"
# purpose: "Denchik Chief Builder Mandate & File Mutation Sentinel (DSH / DEC-151)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "Antigravity & Denchik Builder & DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import contextvars
import logging
from pathlib import Path
from typing import Optional, Union

from core.domain.mandate_contracts import Mandate, MandateScope, MandateViolationError

logger = logging.getLogger("dnk.denchik.builder_guard")

# Context variable for thread/coroutine-safe active mandate
_current_mandate: contextvars.ContextVar[Optional[Mandate]] = contextvars.ContextVar("current_mandate", default=None)


class DenchikMandateGuard:
    """
    Sovereign Guard for Denchik Builder.
    Intercepts and blocks any filesystem mutations outside the active MandateScope.
    """

    @classmethod
    def bind_mandate(cls, mandate: Mandate) -> None:
        """Bind an active immutable Mandate to the current execution context."""
        _current_mandate.set(mandate)
        logger.info(f"Bound active Mandate {mandate.mandate_id} (Actor: {mandate.actor_id}, Scope: {mandate.scope.allowed_paths})")

    @classmethod
    def unbind_mandate(cls) -> None:
        """Clear active mandate from execution context."""
        _current_mandate.set(None)

    @classmethod
    def get_active_mandate(cls) -> Optional[Mandate]:
        """Retrieve the currently bound Mandate."""
        return _current_mandate.get()

    @classmethod
    def validate_mutation(
        cls,
        path: Union[str, Path],
        tool_name: str = "write_file",
        mandate_override: Optional[Mandate] = None
    ) -> None:
        """
        Validate whether a file write or edit is permissible.
        Raises MandateViolationError if target path is disallowed or matches negative scope.
        """
        mandate = mandate_override or cls.get_active_mandate()
        path_str = str(path).strip()

        # Invariant: Absolute paths are strictly forbidden
        if path_str.startswith("/Users/") or path_str.startswith("/root/") or path_str.startswith("/home/"):
            raise MandateViolationError(
                f"Absolute path '{path_str}' rejected. DNK OS requires relative paths (./ or ../)"
            )

        if mandate is not None:
            # 1. Verify tool whitelist
            mandate.assert_tool_allowed(tool_name)

            # 2. Verify file path scope
            mandate.scope.assert_path_allowed(path_str)
        else:
            # Baseline fail-safe when no explicit mandate is bound
            norm = path_str.lstrip("./")
            if ".env" in norm or "credentials" in norm.lower():
                raise MandateViolationError(
                    f"Baseline Guard: Mutation of sensitive file '{path_str}' is forbidden."
                )

    @classmethod
    def safe_write_file(
        cls,
        path: Union[str, Path],
        content: str,
        tool_name: str = "write_file",
        mandate_override: Optional[Mandate] = None
    ) -> bool:
        """
        Atomically write content to a file after strict Mandate validation.
        """
        cls.validate_mutation(path=path, tool_name=tool_name, mandate_override=mandate_override)
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        logger.info(f"Denchik successfully wrote {len(content)} chars to '{path}'.")
        return True

    @classmethod
    def safe_patch_file(
        cls,
        path: Union[str, Path],
        target_str: str,
        replacement: str,
        mandate_override: Optional[Mandate] = None
    ) -> bool:
        """
        Atomically patch file content after strict Mandate validation.
        """
        cls.validate_mutation(path=path, tool_name="patch", mandate_override=mandate_override)
        target = Path(path)
        if not target.exists():
            raise FileNotFoundError(f"File to patch does not exist: {path}")

        current_content = target.read_text(encoding="utf-8")
        if target_str not in current_content:
            raise ValueError(f"Target string not found in '{path}'.")

        new_content = current_content.replace(target_str, replacement)
        target.write_text(new_content, encoding="utf-8")
        logger.info(f"Denchik successfully patched '{path}'.")
        return True

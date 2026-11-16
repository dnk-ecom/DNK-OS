# --- DNK-MRH-HEADER ---
# mrh_id: "core/sentinel/grounding_guard.py"
# purpose: "Deterministic Anti-Hallucination Grounding Guard (assimilated from cactus-compute/cactus)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

"""
Deterministic Anti-Hallucination Grounding Guard.
Assimilated from cactus-compute/cactus (Apache 2.0).
Zero dependencies, pure Python: verifies that numeric values, dates, and amounts
emitted by agents in tool arguments or output contracts are strictly grounded
in the upstream source texts.
"""

from __future__ import annotations

import datetime
import decimal
import re
from typing import Any, Dict, List, Optional, Set, Tuple


class GroundingValidationError(ValueError):
    """Raised when extracted or emitted values are not grounded in upstream context."""


class GroundingGuard:
    """Deterministic validator preventing hallucinated numbers, dates, and prices."""

    _NUMBER_TOKEN = re.compile(
        r"(?<![\w.,])(?:[-+]?\d{1,3}(?:,\d{3})+(?:\.\d+)?|[-+]?\d+(?:\.\d+)?)(?!\d)"
    )
    _DATE_FACT = re.compile(
        r"date:\s*\d{4}-\d{2}-\d{2}(?:\s+[A-Za-z]{3})?(?:\s+\d{2}:\d{2})?|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?"
    )
    _ISO_STAMP = re.compile(r"\d{4}-\d{2}-\d{2}")
    _RELATIVE_CUE = re.compile(
        r"\b(today|tonight|tomorrow|yesterday|next|this|coming|now|in \d+ (?:days?|weeks?|months?|years?)|"
        r"monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
        re.IGNORECASE,
    )

    @classmethod
    def extract_source_numbers(cls, *sources: str) -> Set[decimal.Decimal]:
        """Extract all numeric values explicitly written in source texts."""
        clean_sources = [cls._DATE_FACT.sub(" ", s or "") for s in sources]
        combined = "\n".join(clean_sources)
        return {
            decimal.Decimal(match.group(0).replace(",", ""))
            for match in cls._NUMBER_TOKEN.finditer(combined)
        }

    @classmethod
    def extract_source_years(cls, text: str) -> Set[int]:
        """Extract explicit calendar years from text."""
        months = (
            r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
            r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|"
            r"oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\.?"
        )
        patterns = [
            rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s+{months}[\s,]+(\d{{1,4}})(?![0-9A-Za-z]|:\d|\s*[ap]\.?m\b)",
            rf"\b{months}\s+\d{{1,2}}(?:st|nd|rd|th)?\s*,?\s+(\d{{1,4}})(?![0-9A-Za-z]|:\d|\s*[ap]\.?m\b)",
            rf"\b{months}[\s,]+(\d{{3,4}})(?![0-9A-Za-z])",
            r"\byear\s+(\d{1,4})(?![0-9A-Za-z])",
            r"(?<![0-9])(\d{4})(?=[-/]\d{1,2}[-/]\d{1,2}(?![0-9]))",
        ]
        lowered = text.lower()
        years = {
            int(match.group(1))
            for pattern in patterns
            for match in re.finditer(pattern, lowered)
        }
        # Also include 4-digit numbers in the reasonable year range (1900..2100)
        for match in re.finditer(r"\b(19\d{2}|20\d{2}|2100)\b", lowered):
            years.add(int(match.group(1)))
        return years

    @classmethod
    def _numeric_paths(cls, data: Any, path: str = ""):
        """Traverse data structures yielding (path, value) for every numeric leaf."""
        if isinstance(data, bool):
            return
        if isinstance(data, (int, float, decimal.Decimal)):
            yield path, data
        elif isinstance(data, dict):
            for k, v in data.items():
                new_path = f"{path}.{k}" if path else str(k)
                yield from cls._numeric_paths(v, new_path)
        elif isinstance(data, (list, tuple, set)):
            for i, v in enumerate(data):
                yield from cls._numeric_paths(v, f"{path}[{i}]")

    @classmethod
    def validate_grounding(
        cls,
        arguments: Dict[str, Any],
        source_context: str,
        system_context: Optional[str] = None,
        allow_zero_or_one: bool = True,
    ) -> List[str]:
        """
        Validate that every numeric parameter in arguments is grounded in source texts.
        Returns a list of ungrounded parameter paths (empty list if 100% grounded).
        """
        sources = [source_context]
        if system_context:
            sources.append(system_context)

        licensed_numbers = cls.extract_source_numbers(*sources)
        if allow_zero_or_one:
            licensed_numbers.add(decimal.Decimal(0))
            licensed_numbers.add(decimal.Decimal(1))

        ungrounded: List[str] = []
        for path, val in cls._numeric_paths(arguments):
            try:
                dec_val = decimal.Decimal(str(val))
                if dec_val not in licensed_numbers:
                    ungrounded.append(f"{path}={val}")
            except (decimal.InvalidOperation, ValueError):
                continue

        return ungrounded

    @classmethod
    def enforce(
        cls,
        arguments: Dict[str, Any],
        source_context: str,
        system_context: Optional[str] = None,
        tool_name: str = "tool",
    ) -> None:
        """
        Strict assertion: raises GroundingValidationError if ungrounded values are found.
        """
        ungrounded = cls.validate_grounding(arguments, source_context, system_context)
        if ungrounded:
            detail = ", ".join(ungrounded)
            raise GroundingValidationError(
                f"Tool '{tool_name}' emitted ungrounded numeric hallucination(s): {detail}"
            )

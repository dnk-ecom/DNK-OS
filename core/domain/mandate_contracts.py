# --- DNK-MRH-HEADER ---
# mrh_id: "core/domain/mandate_contracts.py"
# purpose: "Unified Pydantic SSOT machine contracts for DSH Superagent Mandate, Admission Gate, and Tickets."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "Antigravity & Denchik Builder & DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import fnmatch
import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, ConfigDict, Field


class MandateViolationError(Exception):
    """Raised when an agent attempts an action or file modification outside its Mandate scope."""
    pass


class Strength(str, Enum):
    """Strength of authorization basis (DEC-151 / DSH Architecture)."""
    EXPLICIT = "explicit"
    INFERRED = "inferred"
    NOT_ADMITTED = "not_admitted"


class DecisionKind(str, Enum):
    """Eval decision outcome."""
    ACCEPT = "accept"
    STOP = "stop"
    IGNORE = "ignore"
    UNAVAILABLE = "unavailable"


class TicketStage(str, Enum):
    """Stage of a Ticket based on attention/work condition."""
    QUEUED = "working/queued"
    WORKING = "working"
    IDLE = "idle"
    PERSON_ATTENTION = "person/attention"
    PERSON_REVIEW = "person/review"
    PERSON_BLOCKED = "person/blocked"
    PERSON_FAILED = "person/failed"
    ENDED = "ended"


class AssignmentState(str, Enum):
    """State of an Executor Assignment."""
    PENDING = "pending"
    RUNNING = "running"
    ENDED = "ended"


class ReportStatus(str, Enum):
    """Status reported by an Assignment."""
    PROGRESS = "progress"
    WAITING = "waiting"
    READY = "ready"
    BLOCKED = "blocked"
    FAILED = "failed"
    DROPPED = "dropped"


class MandateScope(BaseModel):
    """Execution boundaries granted to an agent."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    allowed_paths: List[str] = Field(
        default_factory=list,
        description="Glob patterns or relative prefixes permitted for mutation"
    )
    negative_scope: List[str] = Field(
        default_factory=list,
        description="Forbidden glob patterns that cannot be touched under any circumstance"
    )
    allowed_tools: List[str] = Field(
        default_factory=list,
        description="Whitelist of tool names permitted for this mandate"
    )
    max_tool_calls: int = Field(default=25, description="MASE limit per turn (DEC-057)")
    timeout_seconds: int = Field(default=1800, description="Max turn duration in seconds")

    def is_path_allowed(self, path: str) -> bool:
        """Check if a path matches allowed globs and does not match negative scope."""
        norm_path = path.strip().lstrip("./")
        
        # 1. Check negative scope first (fail-closed)
        for neg in self.negative_scope:
            neg_norm = neg.strip().lstrip("./")
            if fnmatch.fnmatch(norm_path, neg_norm) or norm_path.startswith(neg_norm):
                return False

        # 2. If allowed_paths is empty, default to allow unless in negative scope
        if not self.allowed_paths:
            return True

        # 3. Check allowed paths
        for allowed in self.allowed_paths:
            allowed_norm = allowed.strip().lstrip("./")
            if fnmatch.fnmatch(norm_path, allowed_norm) or norm_path.startswith(allowed_norm):
                return True

        return False

    def assert_path_allowed(self, path: str) -> None:
        """Assert that path is allowed; raise MandateViolationError if violated."""
        if not self.is_path_allowed(path):
            raise MandateViolationError(
                f"Path '{path}' violates MandateScope. Allowed: {self.allowed_paths}, Negative: {self.negative_scope}"
            )


class Mandate(BaseModel):
    """Immutable authorization contract granting work permissions (DSH / DEC-151)."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    mandate_id: str = Field(default_factory=lambda: f"mnd_{uuid.uuid4().hex[:12]}")
    policy_version: str = Field(..., description="Policy version identifier under which mandate was issued")
    scope: MandateScope = Field(..., description="Target file whitelist, negative scope, and tool boundaries")
    strength: Strength = Field(..., description="Basis strength: explicit or inferred")
    matched_rules: List[str] = Field(default_factory=list, description="Rules matched during assessment")
    actor_id: str = Field(..., description="Originating actor/sender identifier")
    source_id: str = Field(..., description="Originating source (e.g. github, feishu, cli)")
    created_at_epoch: float = Field(default_factory=time.time)

    def check_tool_allowed(self, tool_name: str) -> bool:
        """Verify whether a tool call is permitted by this mandate."""
        if not self.scope.allowed_tools:
            return True
        return tool_name in self.scope.allowed_tools

    def assert_tool_allowed(self, tool_name: str) -> None:
        """Assert that tool call is permitted; raise MandateViolationError if violated."""
        if not self.check_tool_allowed(tool_name):
            raise MandateViolationError(
                f"Tool '{tool_name}' is not in Mandate allowed_tools whitelist: {self.scope.allowed_tools}"
            )


class AdmissionGate(BaseModel):
    """Deterministic first-layer admission check (Zero LLM Waste)."""
    model_config = ConfigDict(extra="forbid")

    allowed_actors: Set[str] = Field(default_factory=set)
    banned_actors: Set[str] = Field(default_factory=set)
    known_bots: Set[str] = Field(default_factory=set)
    allow_inferred_candidates: bool = Field(default=True)

    def admit(self, actor_id: str, is_bot: bool, is_direct_or_mention: bool) -> Strength:
        """
        Evaluate admission deterministically without LLM calls:
        - Banned actors -> NOT_ADMITTED
        - Allowed human with mention/direct -> EXPLICIT
        - Known bot -> INFERRED (if allowed_inferred_candidates)
        - Unknown human with mention/direct -> INFERRED
        - All other cases -> NOT_ADMITTED
        """
        if actor_id in self.banned_actors:
            return Strength.NOT_ADMITTED

        if is_bot:
            if actor_id in self.known_bots and self.allow_inferred_candidates:
                return Strength.INFERRED
            return Strength.NOT_ADMITTED

        if actor_id in self.allowed_actors and is_direct_or_mention:
            return Strength.EXPLICIT

        if is_direct_or_mention and self.allow_inferred_candidates:
            return Strength.INFERRED

        return Strength.NOT_ADMITTED


class ReportRecord(BaseModel):
    """Discrete status report from an Assignment."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    report_id: str = Field(default_factory=lambda: f"rep_{uuid.uuid4().hex[:8]}")
    status: ReportStatus
    summary: str
    attention_question: Optional[str] = None
    created_at_epoch: float = Field(default_factory=time.time)


class Ticket(BaseModel):
    """Unit of authorized work bound to an immutable Mandate."""
    model_config = ConfigDict(extra="forbid")

    ticket_id: str = Field(default_factory=lambda: f"tkt_{uuid.uuid4().hex[:12]}")
    short_name: str = Field(..., description="Human-readable ticket slug")
    mandate: Mandate = Field(..., description="Authorizing mandate")
    stage: TicketStage = Field(default=TicketStage.QUEUED)
    active_assignment_id: Optional[str] = None
    channels: List[str] = Field(default_factory=list, description="Write channel destinations")
    attention_question: Optional[str] = None
    reports: List[ReportRecord] = Field(default_factory=list)
    created_at_epoch: float = Field(default_factory=time.time)
    ended_at_epoch: Optional[float] = None

    def assign(self, executor_id: str) -> str:
        """Bind Ticket to an Executor Assignment."""
        if self.stage == TicketStage.ENDED:
            raise ValueError(f"Cannot assign ended ticket {self.ticket_id}")
        assignment_id = f"asg_{uuid.uuid4().hex[:8]}_{executor_id}"
        self.active_assignment_id = assignment_id
        self.stage = TicketStage.WORKING
        return assignment_id

    def post_report(self, status: ReportStatus, summary: str, question: Optional[str] = None) -> ReportRecord:
        """Record a structured report from the executor and transition stage."""
        record = ReportRecord(
            status=status,
            summary=summary,
            attention_question=question
        )
        self.reports.append(record)

        if question:
            self.attention_question = question
            self.stage = TicketStage.PERSON_ATTENTION
        elif status == ReportStatus.READY:
            self.stage = TicketStage.PERSON_REVIEW
        elif status == ReportStatus.BLOCKED:
            self.stage = TicketStage.PERSON_BLOCKED
        elif status == ReportStatus.FAILED:
            self.stage = TicketStage.PERSON_FAILED
        elif status == ReportStatus.WAITING:
            self.stage = TicketStage.IDLE
        elif status == ReportStatus.PROGRESS:
            self.stage = TicketStage.WORKING
        elif status == ReportStatus.DROPPED:
            self.stage = TicketStage.ENDED
            self.ended_at_epoch = time.time()

        return record

    def answer_attention(self, answer: str) -> None:
        """Clear attention question and resume working stage."""
        if self.stage != TicketStage.PERSON_ATTENTION:
            raise ValueError(f"Ticket {self.ticket_id} is not awaiting attention (current stage: {self.stage})")
        self.attention_question = None
        self.stage = TicketStage.WORKING

    def stop(self, reason: str) -> None:
        """Explicitly stop ticket and move to ENDED stage."""
        self.post_report(ReportStatus.DROPPED, summary=f"Stopped: {reason}")
        self.stage = TicketStage.ENDED
        self.ended_at_epoch = time.time()

    def resume(self) -> None:
        """Resume ended ticket if mandate is still valid."""
        if self.stage != TicketStage.ENDED:
            return
        self.stage = TicketStage.WORKING
        self.ended_at_epoch = None

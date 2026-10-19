"""
AeroMem: Decentralized Episodic State & Vector Memory Bridge for Fetch.ai Agents
Module: aeromem_models.py

Defines the core data contracts, episodic schemas, and communication messages
built on `uagents.Model` for cross-agent memory ingestion and retrieval.
"""

from enum import Enum
import time
from typing import Any, Dict, List, Optional
from uagents import Field, Model


class MemoryType(str, Enum):
    """
    Episodic memory classification types corresponding to cognitive agent stages:
    - OBSERVATION: Raw environmental signals, log alerts, metric anomalies.
    - REASONING: Internal deliberations, root-cause hypotheses, planner thoughts.
    - EXECUTION: Remediation actions, API calls, bash commands, configuration diffs.
    - REFLECTION: Post-mortem evaluation, lessons learned, outcome verification.
    """
    OBSERVATION = "OBSERVATION"
    REASONING = "REASONING"
    EXECUTION = "EXECUTION"
    REFLECTION = "REFLECTION"


class MemoryItem(Model):
    """
    Represents an atomic episodic memory entry indexed inside AeroMem.
    Includes contextual metadata and semantic similarity metrics.
    """
    memory_id: str = Field(description="Unique identifier for this episodic memory item.")
    session_id: str = Field(description="Correlation identifier grouping an incident or conversation.")
    task_name: str = Field(description="Name or title of the task / incident.")
    memory_type: MemoryType = Field(description="Cognitive classification of this memory.")
    summary: str = Field(description="High-level concise summary for dense vector indexing.")
    detailed_content: str = Field(description="Exhaustive payload, execution logs, or cognitive steps.")
    metadata: Dict[str, Any] = Field(default={}, description="Custom structured attributes (e.g. env, host, error_code).")
    timestamp: float = Field(default=0.0, description="Unix epoch timestamp when memory was captured.")
    similarity_score: Optional[float] = Field(default=None, description="Semantic relevance score computed during recall (0.0 to 1.0).")

    def to_indexable_text(self) -> str:
        """
        Combines summary and detailed content into a unified embedding payload.
        """
        return f"[{self.memory_type.value}] Task: {self.task_name} | Summary: {self.summary}\nContent: {self.detailed_content}"


class EpisodicCommitRequest(Model):
    """
    Protocol message sent by a worker agent to persist a new episodic state into AeroMem.
    """
    session_id: str = Field(description="Current workflow or incident session ID.")
    task_name: str = Field(description="Designation of the task being recorded.")
    memory_type: MemoryType = Field(default=MemoryType.EXECUTION, description="Cognitive category of the memory.")
    summary: str = Field(description="Dense synopsis used for vector search indexing.")
    detailed_content: str = Field(description="Comprehensive step-by-step trace or payload.")
    metadata: Dict[str, Any] = Field(default={}, description="Arbitrary metadata key-value tags.")
    timestamp: Optional[float] = Field(default=None, description="Optional custom timestamp; defaults to current epoch if None.")


class EpisodicCommitResponse(Model):
    """
    Acknowledgment receipt returned by AeroMem after indexing the episodic state.
    """
    success: bool = Field(description="True if commit and indexing succeeded.")
    memory_id: str = Field(description="Assigned unique ID of the stored memory item.")
    message: str = Field(description="Human-readable status or error description.")
    timestamp: float = Field(default=0.0, description="Timestamp of acknowledgment.")


class SemanticRecallRequest(Model):
    """
    Protocol query message to perform cross-agent vector retrieval against AeroMem.
    """
    query: str = Field(description="Natural language query or problem description.")
    top_k: int = Field(default=3, description="Maximum number of relevant memories to retrieve.")
    memory_type: Optional[MemoryType] = Field(default=None, description="Optional filter by memory type.")
    session_id: Optional[str] = Field(default=None, description="Optional filter by session ID.")
    task_name: Optional[str] = Field(default=None, description="Optional filter by specific task name.")
    min_similarity: float = Field(default=0.0, description="Minimum cosine similarity cutoff.")


class SemanticRecallResponse(Model):
    """
    Protocol response containing semantically matched episodic memories.
    """
    query: str = Field(description="Echoed query string.")
    results: List[MemoryItem] = Field(default=[], description="Ranked list of semantically relevant memories.")
    total_found: int = Field(description="Total count of matching items returned.")
    timestamp: float = Field(default=0.0, description="Timestamp of query response.")

"""
AeroMem: Decentralized Episodic State & Vector Memory Bridge for Fetch.ai Agents
Module: aeromem_protocol.py

Implements the Fetch.ai `Protocol` ("AeroMemEpisodicBridge", "1.0.0") handling:
1. `EpisodicCommitRequest` -> Indexes memory in high-dimensional vector space + syncs to `ctx.storage`
2. `SemanticRecallRequest` -> Performs semantic vector search & returns ranked `MemoryItem`s
Addresses Category A (Agent Memory & State Bottlenecks) from Dey & Viradecha, arXiv:2606.20570.
"""

import logging
import os
import time
import uuid
from typing import Any, Dict, List, Optional

import numpy as np
from uagents import Context, Protocol

from aeromem_models import (
    EpisodicCommitRequest,
    EpisodicCommitResponse,
    MemoryItem,
    MemoryType,
    SemanticRecallRequest,
    SemanticRecallResponse,
)

# ---------------------------------------------------------------------------
# Vector Memory Engine (ChromaDB + Fallback Semantic Cosine Similarity Engine)
# ---------------------------------------------------------------------------

logger = logging.getLogger("AeroMemProtocol")


class AeroMemVectorStore:
    """
    Decentralized Vector Memory Engine for Fetch.ai Agents.
    Supports persistent ChromaDB collection with automatic fallback to an
    in-memory TF-IDF semantic vector space for resilient zero-dependency execution.
    """

    def __init__(self, db_path: Optional[str] = None, collection_name: str = "aeromem_episodes"):
        # Default to user home directory to avoid Windows OneDrive sync lock interference
        default_dir = os.path.join(os.path.expanduser("~"), ".aeromem_chroma_db")
        self.db_path = db_path or os.getenv("AEROMEM_CHROMA_DIR", default_dir)
        self.collection_name = collection_name
        self.use_chroma = False
        self.chroma_client = None
        self.collection = None
        self.memory_registry: Dict[str, MemoryItem] = {}

        # Fallback Vector Space components (TF-IDF + Cosine Similarity)
        self._fallback_docs: List[str] = []
        self._fallback_ids: List[str] = []

        self._init_chroma()

    def _init_chroma(self) -> None:
        """Attempts to initialize ChromaDB PersistentClient with self-healing check."""
        try:
            import chromadb
            from chromadb.config import Settings

            os.makedirs(self.db_path, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(anonymized_telemetry=False, is_persistent=True),
            )
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "AeroMem Cross-Agent Episodic Vector Index"},
            )
            # Perform quick sanity count to guarantee index integrity
            _ = self.collection.count()
            self.use_chroma = True
            logger.info(f"AeroMem Vector Store initialized with ChromaDB [PERSISTENT at {self.db_path}]")
        except Exception as exc:
            logger.warning(
                f"ChromaDB initialization deferred: {exc}. "
                "Engaging high-performance local semantic cosine-similarity engine fallback."
            )
            self.use_chroma = False

    def insert(self, item: MemoryItem) -> None:
        """Indexes an episodic memory item into the vector store."""
        self.memory_registry[item.memory_id] = item
        doc_text = item.to_indexable_text()

        if self.use_chroma and self.collection is not None:
            try:
                # Sanitize metadata for ChromaDB (scalars only)
                meta = {
                    "memory_id": item.memory_id,
                    "session_id": str(item.session_id),
                    "task_name": str(item.task_name),
                    "memory_type": str(item.memory_type.value),
                    "timestamp": float(item.timestamp),
                }
                self.collection.upsert(
                    ids=[item.memory_id],
                    documents=[doc_text],
                    metadatas=[meta],
                )
            except Exception as exc:
                logger.warning(f"ChromaDB upsert failed, indexing in fallback vector space: {exc}")
                self.use_chroma = False

        # Always synchronize with fallback in-memory index for zero-latency failover
        if item.memory_id not in self._fallback_ids:
            self._fallback_ids.append(item.memory_id)
            self._fallback_docs.append(doc_text)
        else:
            idx = self._fallback_ids.index(item.memory_id)
            self._fallback_docs[idx] = doc_text

    def query(
        self,
        query_text: str,
        top_k: int = 3,
        memory_type: Optional[MemoryType] = None,
        session_id: Optional[str] = None,
        task_name: Optional[str] = None,
        min_similarity: float = 0.0,
    ) -> List[MemoryItem]:
        """
        Executes semantic vector retrieval against indexed episodic memories.
        Returns ranked MemoryItem models with assigned similarity_score.
        """
        if not self.memory_registry:
            return []

        # 1. Primary Retrieval via ChromaDB
        if self.use_chroma and self.collection is not None and self.collection.count() > 0:
            try:
                where_clause: Dict[str, Any] = {}
                filters = []
                if memory_type:
                    filters.append({"memory_type": memory_type.value})
                if session_id:
                    filters.append({"session_id": session_id})
                if task_name:
                    filters.append({"task_name": task_name})

                if len(filters) == 1:
                    where_clause = filters[0]
                elif len(filters) > 1:
                    where_clause = {"$and": filters}

                n_results = min(top_k, self.collection.count())
                results = self.collection.query(
                    query_texts=[query_text],
                    n_results=n_results,
                    where=where_clause if where_clause else None,
                    include=["distances", "metadatas", "documents"],
                )

                matched_items: List[MemoryItem] = []
                ids = results.get("ids", [[]])[0]
                distances = results.get("distances", [[]])[0]

                for mem_id, dist in zip(ids, distances):
                    if mem_id in self.memory_registry:
                        # Cosine distance range is [0, 2], normalized similarity: 1.0 - (dist / 2.0)
                        similarity = max(0.0, min(1.0, 1.0 - (dist / 2.0)))
                        if similarity >= min_similarity:
                            item = self.memory_registry[mem_id].copy(deep=True)
                            item.similarity_score = round(similarity, 4)
                            matched_items.append(item)

                if matched_items:
                    return matched_items
            except Exception as exc:
                logger.warning(f"ChromaDB query encountered issue: {exc}. Using fallback engine.")
                self.use_chroma = False

        # 2. Resilient Fallback: TF-IDF + Cosine Similarity Vector Space
        return self._fallback_query(query_text, top_k, memory_type, session_id, task_name, min_similarity)

    def _fallback_query(
        self,
        query_text: str,
        top_k: int,
        memory_type: Optional[MemoryType],
        session_id: Optional[str],
        task_name: Optional[str],
        min_similarity: float,
    ) -> List[MemoryItem]:
        """Calculates cosine similarity using scikit-learn TfidfVectorizer."""
        candidate_ids = []
        candidate_docs = []

        for mem_id, item in self.memory_registry.items():
            if memory_type and item.memory_type != memory_type:
                continue
            if session_id and item.session_id != session_id:
                continue
            if task_name and item.task_name != task_name:
                continue
            candidate_ids.append(mem_id)
            candidate_docs.append(item.to_indexable_text())

        if not candidate_ids:
            return []

        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
            tfidf_matrix = vectorizer.fit_transform(candidate_docs + [query_text])
            query_vec = tfidf_matrix[-1]
            doc_vecs = tfidf_matrix[:-1]

            sims = cosine_similarity(query_vec, doc_vecs).flatten()
            ranked_indices = np.argsort(sims)[::-1]

            results = []
            for idx in ranked_indices[:top_k]:
                score = float(sims[idx])
                if score >= min_similarity:
                    item = self.memory_registry[candidate_ids[idx]].copy(deep=True)
                    item.similarity_score = round(score, 4)
                    results.append(item)
            return results
        except Exception as exc:
            logger.error(f"Fallback vector search failed: {exc}")
            # Substring matching fallback
            results = []
            query_words = set(query_text.lower().split())
            for mem_id in candidate_ids:
                item = self.memory_registry[mem_id]
                doc_words = set(item.to_indexable_text().lower().split())
                overlap = len(query_words & doc_words)
                score = overlap / max(1, len(query_words))
                if score >= min_similarity:
                    copied = item.copy(deep=True)
                    copied.similarity_score = round(score, 4)
                    results.append(copied)
            results.sort(key=lambda x: x.similarity_score or 0.0, reverse=True)
            return results[:top_k]


# Global Vector Engine Instance shared across protocol handlers
vector_engine = AeroMemVectorStore()

# ---------------------------------------------------------------------------
# Fetch.ai Versioned Protocol Definition
# ---------------------------------------------------------------------------

PROTOCOL_NAME = "AeroMemEpisodicBridge"
PROTOCOL_VERSION = "1.0.0"

aeromem_proto = Protocol(name=PROTOCOL_NAME, version=PROTOCOL_VERSION)


@aeromem_proto.on_message(model=EpisodicCommitRequest, replies={EpisodicCommitResponse})
async def handle_commit(ctx: Context, sender: str, msg: EpisodicCommitRequest) -> None:
    """
    Handles structured episodic memory ingestion from client agents:
    1. Validates memory attributes and formats atomic MemoryItem
    2. Indexes memory inside AeroMem high-dimensional vector space (ChromaDB)
    3. Persists fallback state into native Agentverse `ctx.storage` (resolving volatility)
    4. Returns confirmation receipt to sender
    """
    ctx.logger.info(
        f"[AEROMEM:COMMIT] Ingesting {msg.memory_type.value} memory from {sender[:16]}... "
        f"| Task: '{msg.task_name}' | Session: {msg.session_id}"
    )

    memory_id = f"mem_{uuid.uuid4().hex[:12]}"
    timestamp = msg.timestamp if msg.timestamp is not None and msg.timestamp > 0 else time.time()

    memory_item = MemoryItem(
        memory_id=memory_id,
        session_id=msg.session_id,
        task_name=msg.task_name,
        memory_type=msg.memory_type,
        summary=msg.summary,
        detailed_content=msg.detailed_content,
        metadata=msg.metadata,
        timestamp=timestamp,
    )

    # 1. Real Vector Embedding & Indexing
    vector_engine.insert(memory_item)

    # 2. Dual-Layer Fallback to Agentverse Native Flat Key-Value Storage (ctx.storage)
    try:
        raw_episodes = ctx.storage.get("aeromem_episodes") or []
        raw_episodes.append(memory_item.dict())
        ctx.storage.set("aeromem_episodes", raw_episodes)

        stats = ctx.storage.get("aeromem_stats") or {"total_commits": 0, "last_updated": 0.0}
        stats["total_commits"] += 1
        stats["last_updated"] = timestamp
        ctx.storage.set("aeromem_stats", stats)

        ctx.logger.info(
            f"[AEROMEM:STORAGE] Synchronized memory '{memory_id}' with ctx.storage "
            f"(Total persisted episodes: {len(raw_episodes)})"
        )
    except Exception as exc:
        ctx.logger.warning(f"[AEROMEM:STORAGE] ctx.storage sync warning: {exc}")

    # 3. Send structured acknowledgment back to the committing agent
    response = EpisodicCommitResponse(
        success=True,
        memory_id=memory_id,
        message=f"Memory committed and indexed successfully into AeroMem (ChromaDB mode: {vector_engine.use_chroma}).",
        timestamp=time.time(),
    )
    await ctx.send(sender, response)


@aeromem_proto.on_message(model=SemanticRecallRequest, replies={SemanticRecallResponse})
async def handle_recall(ctx: Context, sender: str, msg: SemanticRecallRequest) -> None:
    """
    Handles natural language semantic recall requests across distributed agents:
    1. Executes dense vector similarity search against indexed experiences
    2. Filters by type, session, or confidence cutoff if requested
    3. Cross-checks `ctx.storage` if needed to guarantee zero state loss across restarts
    4. Returns ranked matching incident mitigations and reflections
    """
    ctx.logger.info(
        f"[AEROMEM:RECALL] Semantic query from {sender[:16]}...: '{msg.query}' "
        f"(top_k={msg.top_k}, type_filter={msg.memory_type.value if msg.memory_type else 'ALL'})"
    )

    # If local vector registry is empty, hydrate from ctx.storage (recovering from restart)
    if not vector_engine.memory_registry:
        try:
            persisted = ctx.storage.get("aeromem_episodes") or []
            if persisted:
                ctx.logger.info(f"[AEROMEM:HYDRATE] Restoring {len(persisted)} episodes from ctx.storage...")
                for item_dict in persisted:
                    restored_item = MemoryItem(**item_dict)
                    vector_engine.insert(restored_item)
        except Exception as exc:
            ctx.logger.warning(f"[AEROMEM:HYDRATE] Failed to restore from ctx.storage: {exc}")

    # Perform vector similarity retrieval
    matched_items = vector_engine.query(
        query_text=msg.query,
        top_k=msg.top_k,
        memory_type=msg.memory_type,
        session_id=msg.session_id,
        task_name=msg.task_name,
        min_similarity=msg.min_similarity,
    )

    ctx.logger.info(
        f"[AEROMEM:RECALL_RESULT] Found {len(matched_items)} matching episodes. "
        f"Top score: {matched_items[0].similarity_score if matched_items else 0.0}"
    )

    response = SemanticRecallResponse(
        query=msg.query,
        results=matched_items,
        total_found=len(matched_items),
        timestamp=time.time(),
    )
    await ctx.send(sender, response)

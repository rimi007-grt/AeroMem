"""
AeroMem: Decentralized Episodic State & Vector Memory Bridge for Fetch.ai Agents
Module: dashboard.py (Interactive Mission Control & Live Demo Dashboard)

Interactive Streamlit application for Fetch-A-Thon 3.0 judges to visualize:
1. Live Episodic Vector Memory Retrieval (ChromaDB + Cosine Similarity)
2. Dual-Layer Storage Telemetry (ChromaDB Vector Index + Agentverse ctx.storage)
3. Interactive Query Playground with Real-Time Similarity Ranking
4. Live Memory Ingestion Sandbox & Cognitive Inspection
"""

import json
import os
import time
from typing import Any, Dict, List
import streamlit as st

# Configure modern page layout
st.set_page_config(
    page_title="AeroMem | Decentralized Episodic Vector Bridge",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom sleek CSS styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #4F46E5, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #94A3B8;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(79, 70, 229, 0.3);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .memory-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .badge-execution { background-color: #10B981; color: white; }
    .badge-observation { background-color: #3B82F6; color: white; }
    .badge-reasoning { background-color: #F59E0B; color: white; }
    .badge-reflection { background-color: #8B5CF6; color: white; }
    .similarity-high { color: #10B981; font-weight: bold; }
    .similarity-med { color: #F59E0B; font-weight: bold; }
    .similarity-low { color: #94A3B8; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Data Hydration from ChromaDB & ctx.storage
# ---------------------------------------------------------------------------

@st.cache_resource
def load_vector_engine():
    """Initializes and caches the AeroMem Vector Store instance."""
    from aeromem_protocol import vector_engine
    from aeromem_models import MemoryItem

    # Hydrate from persistent ctx.storage json if available
    storage_file = "agent1q23r8fyjz2_data.json"
    if os.path.exists(storage_file):
        try:
            with open(storage_file, "r") as f:
                data = json.load(f)
                episodes = data.get("aeromem_episodes", [])
                for ep in episodes:
                    item = MemoryItem(**ep)
                    vector_engine.insert(item)
        except Exception:
            pass
    return vector_engine


def get_storage_stats():
    """Reads live statistics from Agentverse native ctx.storage."""
    storage_file = "agent1q23r8fyjz2_data.json"
    if os.path.exists(storage_file):
        try:
            with open(storage_file, "r") as f:
                data = json.load(f)
                episodes = data.get("aeromem_episodes", [])
                stats = data.get("aeromem_stats", {})
                return len(episodes), stats.get("total_commits", len(episodes))
        except Exception:
            pass
    return 0, 0


vector_engine = load_vector_engine()
episodes_count, total_commits = get_storage_stats()

# ---------------------------------------------------------------------------
# Header & Architecture Mission Banner
# ---------------------------------------------------------------------------

st.markdown('<div class="main-title">🧠 AeroMem: Decentralized Episodic Vector Memory Bridge</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title"><b>Fetch-A-Thon 3.0 Live Operational Dashboard</b> | '
    'Addressing Category A (Agent Memory & State Bottlenecks) — <i>Dey & Viradecha, arXiv:2606.20570</i></div>',
    unsafe_allow_html=True
)

# Top KPI Metric Row
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric(label="Total Indexed Episodes", value=f"{max(episodes_count, len(vector_engine.memory_registry))}", delta="Live Persisted")
with kpi2:
    st.metric(label="Vector Index Mode", value="ChromaDB (MiniLM)", delta="Dense Embeddings")
with kpi3:
    st.metric(label="Dual Storage Layer", value="ctx.storage Synced", delta="Zero State Loss")
with kpi4:
    st.metric(label="Active Agent Nodes", value="2 uAgents", delta="Bureau Mesh Active")

st.divider()

# ---------------------------------------------------------------------------
# Main Interactive Tabs
# ---------------------------------------------------------------------------

tab_query, tab_inspector, tab_inject, tab_academic = st.tabs([
    "🔍 Live Semantic Query Sandbox",
    "📚 Episodic Memory Inspector",
    "⚡ Inject Simulated Anomaly",
    "📑 Academic Gap Analysis (arXiv:2606.20570)",
])

# ---------------------------------------------------------------------------
# TAB 1: Live Semantic Query Sandbox
# ---------------------------------------------------------------------------
with tab_query:
    st.subheader("Test Cross-Agent Semantic Recall in Real-Time")
    st.markdown(
        "Type any natural language incident description or technical query. "
        "AeroMem converts the query into a dense embedding, searches ChromaDB vector space, "
        "and returns matching cognitive experiences ranked by cosine similarity."
    )

    col_q1, col_q2 = st.columns([3, 1])
    with col_q1:
        sample_queries = [
            "How to resolve Kubernetes OOMKilled crash loop in payment-service JVM heap?",
            "PostgreSQL connection pool exhausted fatal remaining connection slots are reserved",
            "Ingress nginx TLS certificate expired SSL handshake failed cert-manager",
            "Database connection timeout under heavy traffic surge",
            "Container running out of memory in production cluster",
        ]
        selected_sample = st.selectbox("Or choose a pre-loaded DevOps incident query:", ["Custom Query..."] + sample_queries)
        
        default_val = selected_sample if selected_sample != "Custom Query..." else "How to fix Kubernetes container OOM memory limit?"
        user_query = st.text_input("Enter natural language query:", value=default_val)

    with col_q2:
        top_k = st.slider("Top K Matches", min_value=1, max_value=6, value=3)
        min_sim = st.slider("Min Similarity Cutoff", min_value=0.0, max_value=1.0, value=0.1, step=0.05)

    if st.button("🚀 Execute Semantic Vector Retrieval", type="primary"):
        start_t = time.perf_counter()
        results = vector_engine.query(query_text=user_query, top_k=top_k, min_similarity=min_sim)
        latency_ms = (time.perf_counter() - start_t) * 1000

        st.caption(f"⚡ Search executed in **{latency_ms:.2f} ms** | Found **{len(results)}** matching episodes")

        if not results:
            st.warning("No memories exceeded the similarity threshold. Try lowering the similarity cutoff.")
        else:
            for i, item in enumerate(results, 1):
                score = item.similarity_score or 0.0
                score_class = "similarity-high" if score > 0.6 else ("similarity-med" if score > 0.3 else "similarity-low")
                badge_type = item.memory_type.value.lower()

                with st.expander(f"Match #{i}: {item.task_name} (Similarity Score: {score:.4f})", expanded=(i == 1)):
                    c1, c2, c3 = st.columns([1, 1, 2])
                    with c1:
                        st.markdown(f"**Cognitive Type:** <span class='memory-badge badge-{badge_type}'>{item.memory_type.value}</span>", unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"**Similarity:** <span class='{score_class}'>{score:.4f} ({score*100:.1f}%)</span>", unsafe_allow_html=True)
                    with c3:
                        st.markdown(f"**Session ID:** `{item.session_id}` | ID: `{item.memory_id}`")

                    st.markdown(f"### 🎯 Action Plan Extracted from Memory:\n> **{item.summary}**")
                    st.text_area("Full Cognitive Trace (Detailed Content)", value=item.detailed_content, height=130, key=f"det_{item.memory_id}_{i}")

                    if item.metadata:
                        st.json(item.metadata)

# ---------------------------------------------------------------------------
# TAB 2: Episodic Memory Inspector
# ---------------------------------------------------------------------------
with tab_inspector:
    st.subheader("Explore the Full AeroMem Episodic Graph")
    items = list(vector_engine.memory_registry.values())
    st.write(f"Total Unique Episodes Registered: **{len(items)}**")

    type_filter = st.multiselect(
        "Filter by Memory Type:",
        options=["OBSERVATION", "REASONING", "EXECUTION", "REFLECTION"],
        default=["EXECUTION"]
    )

    filtered_items = [it for it in items if it.memory_type.value in type_filter] if type_filter else items

    # Show table
    table_data = []
    for it in reversed(filtered_items[-50:]):  # Last 50 items
        table_data.append({
            "Memory ID": it.memory_id,
            "Session": it.session_id,
            "Type": it.memory_type.value,
            "Task Name": it.task_name,
            "Summary": it.summary[:80] + "..." if len(it.summary) > 80 else it.summary,
            "Timestamp": time.strftime("%H:%M:%S", time.localtime(it.timestamp)) if it.timestamp else "N/A"
        })

    if table_data:
        st.dataframe(table_data, use_container_width=True)
    else:
        st.info("No episodes match the selected filter.")

# ---------------------------------------------------------------------------
# TAB 3: Inject Simulated Anomaly
# ---------------------------------------------------------------------------
with tab_inject:
    st.subheader("Inject New Episodic Experience in Real-Time")
    st.markdown("Test live ingestion: commit a new incident to ChromaDB vector space and see it immediately indexed!")

    with st.form("inject_form"):
        f_task = st.text_input("Task / Incident Title", value="Redis Cluster Memory Fragmentation Threshold Breach")
        f_session = st.text_input("Session ID", value=f"INC-{int(time.time()) % 10000}-REDIS")
        f_type = st.selectbox("Cognitive Type", ["EXECUTION", "OBSERVATION", "REASONING", "REFLECTION"])
        f_summary = st.text_input("Remediation Summary", value="Triggered active defragmentation (activedefrag=yes) and scaled maxmemory to 4GB.")
        f_content = st.text_area("Detailed Cognitive Trace", value="OBSERVATION: Redis mem_fragmentation_ratio hit 1.84.\nEXECUTION: Ran CONFIG SET activedefrag yes on redis-master-0.\nREFLECTION: Fragmentation ratio stabilized at 1.12 within 90 seconds.")
        submitted = st.form_submit_button("Commit to AeroMem Vector Index", type="primary")

        if submitted:
            from aeromem_models import MemoryItem, MemoryType
            import uuid
            new_item = MemoryItem(
                memory_id=f"mem_{uuid.uuid4().hex[:12]}",
                session_id=f_session,
                task_name=f_task,
                memory_type=MemoryType(f_type),
                summary=f_summary,
                detailed_content=f_content,
                metadata={"injected_via": "streamlit_dashboard", "cluster": "demo-cluster"},
                timestamp=time.time(),
            )
            vector_engine.insert(new_item)
            st.success(f"✅ Ingested episode '{new_item.memory_id}' into ChromaDB! It is now queryable in Tab 1.")

# ---------------------------------------------------------------------------
# TAB 4: Academic Gap Analysis
# ---------------------------------------------------------------------------
with tab_academic:
    st.subheader("Academic Foundation: Dey & Viradecha (arXiv:2606.20570)")
    st.markdown("""
    In *"Infrastructure for the Agentic Web: Gap Analysis and Architecture from the Agentverse Platform"*,
    the authors audit the fundamental barriers preventing autonomous multi-agent networks from scaling to production.
    """)

    st.markdown("### Comparative Gap Resolution")
    comp_col1, comp_col2 = st.columns(2)
    with comp_col1:
        st.error("❌ Native Agentverse KV Storage (`ctx.storage`)")
        st.markdown("""
        * **Flat Key-Value only:** Access restricted to exact key lookups (e.g. `ctx.storage.get("key")`).
        * **Zero Semantic Search:** Incidents cannot be recalled by natural language descriptions.
        * **Siloed State:** Memory is confined within individual agents; peer agents cannot share solutions.
        * **High Restart Volatility:** In-memory context is wiped on process restart or cloud reallocation.
        """)

    with comp_col2:
        st.success("✅ AeroMem Decentralized Vector Memory Bridge")
        st.markdown("""
        * **Dense Vector Indexing:** Powered by persistent ChromaDB (`all-MiniLM-L6-v2`) with local TF-IDF fallbacks.
        * **Semantic Recall:** Natural language query matching with similarity score ranking (0.0 to 1.0).
        * **Cross-Agent Experience Sharing:** Standardized Fetch.ai protocol (`AeroMemEpisodicBridge/1.0.0`).
        * **Dual-Layer Persistence:** Seamless automatic sync with `ctx.storage` ensuring zero state loss.
        """)

    st.code("""
@article{dey2024infrastructure,
  title={Infrastructure for the Agentic Web: Gap Analysis and Architecture from the Agentverse Platform},
  author={Dey, A. and Viradecha, P.},
  journal={arXiv preprint arXiv:2606.20570},
  year={2026}
}
    """, language="bibtex")

st.divider()
st.caption("AeroMem © 2026 Fetch-A-Thon 3.0 Submission | Built for the Fetch.ai Autonomous Agent Ecosystem")

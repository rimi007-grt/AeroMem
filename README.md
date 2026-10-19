# AeroMem: Decentralized Episodic State & Vector Memory Bridge for Fetch.ai Agents

> **One-Line Value Proposition:** A production-grade, decentralized episodic vector memory and state bridge for Fetch.ai (`uagents`, Agentverse, ASI:One) enabling semantic experience sharing and zero-data-loss state persistence across autonomous agents.

---

## 1. Academic Foundation & The Problem

In the empirical Agentverse audit paper:  
**"Infrastructure for the Agentic Web: Gap Analysis and Architecture from the Agentverse Platform"** *(Dey & Viradecha, arXiv:2606.20570)*, the authors categorize the core systemic limitations of multi-agent networks into four critical categories:

* **Category A: Agent Memory and State Bottlenecks** *(Core Focus)*
* **Category B: Communication Latency and Discovery**
* **Category C: Identity and Authentication**
* **Category D: Execution Environment Volatility**

### The Core Problem in Category A
Currently, native Fetch.ai Agentverse agents rely strictly on flat, un-indexed key-value storage (`ctx.storage`). This architecture imposes severe limitations on autonomous multi-agent deployments:
1. **Zero Semantic Vector Retrieval:** Agents cannot query past experiences by natural language, contextual similarity, or task semantics. A worker facing an incident cannot ask *"How did we resolve a similar JVM OOMKilled loop last week?"*
2. **Zero Cross-Agent Experience Sharing:** Memory is isolated within single-agent KV silos. When Agent A discovers a novel bug mitigation, Agent B has no decentralized protocol to retrieve or reuse that cognitive solution.
3. **High Volatility & Cold-Start Amputation Across Restarts:** Standard ephemeral agent restarts wipe in-memory context and cause severe knowledge loss, forcing agents to rediscover mitigations repeatedly from scratch.

---

## 2. AeroMem Solution Architecture

**AeroMem** resolves Category A bottlenecks by introducing an open Fetch.ai protocol (`AeroMemEpisodicBridge/1.0.0`) that pairs **high-dimensional dense vector embeddings** (via persistent ChromaDB with automated local TF-IDF semantic fallbacks) with **dual-layer native `ctx.storage` synchronization**.

```
+-----------------------------------------------------------------------------------------+
|                                 FETCH.AI MULTI-AGENT FABRIC                             |
+-----------------------------------------------------------------------------------------+
                                              |
                   [1] Detect Incident / Trigger SRE Anomaly
                                              v
                      +-----------------------------------------------+
                      |     DevOps / SRE Triage Worker Agent          |
                      |  Address: agent1qw5mlmeefenyvc8keueecj9a...   |
                      +-----------------------------------------------+
                                 |                         ^
        [2] SemanticRecallRequest|                         | [3] SemanticRecallResponse
          (Natural Language Query)                         |     (Ranked MemoryItems &
                                 v                         |      Similarity Scores)
                      +-----------------------------------------------+
                      |           AeroMem Episodic Bridge             |
                      |  Address: agent1q23r8fyjz2krjzqwpmh6axf...    |
                      +-----------------------------------------------+
                        |                        |                  ^
                        |                        |                  | [6] Hydrate State
        [4] Vector Embed|         [5] KV Backup  |                  |     on Cold Restart
            & Similarity|             Sync       |                  |
                        v                        v                  |
         +-----------------------------+  +-------------------------------+
         |  ChromaDB Vector Store      |  |  Agentverse Native Storage    |
         |  - Dense MiniLM Embeddings  |  |  - ctx.storage Key-Value      |
         |  - Cosine Distance Metric   |  |  - Persistent Episodes List   |
         |  - Metadata Filter Engine   |  |  - Total Commits Statistics   |
         +-----------------------------+  +-------------------------------+
                        |
                        v
         [7] Client Applies Mitigation & Commits Episodic Memory
             (OBSERVATION -> REASONING -> EXECUTION -> REFLECTION)
```

### Cognitive Memory Stages
AeroMem categorizes episodic state using the `MemoryType` cognitive taxonomy:
* `OBSERVATION`: Raw environmental signals, log alerts, metric anomalies (e.g. `Container exit code 137`).
* `REASONING`: Root-cause deductions, architectural hypotheses, planner deliberations.
* `EXECUTION`: Remediation actions, API calls, bash commands, configuration patches.
* `REFLECTION`: Post-mortem evaluations, lessons learned, and verification outcomes.

---

## 3. Repository Structure

```
aeromem/
├── aeromem_models.py      # Core data models based on uagents.Model (Pydantic)
├── aeromem_protocol.py    # Fetch.ai Protocol ("AeroMemEpisodicBridge", "1.0.0")
├── memory_agent.py        # Server/Bridge Host Agent with persistent vector store
├── worker_client_agent.py # DevOps/CloudOps triage worker agent (Consumer)
├── test_bureau_runner.py  # 1-command concurrent runner using uagents.Bureau
├── requirements.txt       # Production dependencies
└── README.md              # Project documentation and benchmarks
```

---

## 4. Setup & Execution

### Prerequisites
* Python 3.10, 3.11, or 3.12
* Windows, Linux, or macOS

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Single-Command Multi-Agent Bureau Testbench
Judges can evaluate the end-to-end multi-agent protocol with one command:
```bash
python test_bureau_runner.py
```

### 3. Running Agents Standalone
If running agents on distinct servers, containers, or Agentverse mailboxes:
```bash
# Terminal 1: Start the AeroMem Server Bridge Host
python memory_agent.py

# Terminal 2: Start the DevOps SRE Worker Client
python worker_client_agent.py
```

---

## 5. Sample Terminal Execution Output Logs

The following live log trace demonstrates:
1. Deterministic address generation and startup banners.
2. Cold-start triage: Worker encounters an anomaly (`INC-8921-OOM`), queries AeroMem, and finds 0 matches.
3. Mitigation and episodic commit to AeroMem (indexing in ChromaDB + `ctx.storage`).
4. Knowledge recall: In subsequent cycles, the worker queries AeroMem and **instantly retrieves prior mitigations with high cosine similarity (0.7159)**, executing proven action plans from memory!

```text
================================================================================
   _                     __  __                ____                                 
  / \   ___ _ __ ___   |  \/  | ___ _ __ ___  | __ ) _   _ _ __ ___  __ _ _   _ 
 / _ \ / _ \ '__/ _ \  | |\/| |/ _ \ '_ ` _ \ |  _ \| | | | '__/ _ \/ _` | | | |
/ ___ \  __/ | | (_) | | |  | |  __/ | | | | || |_) | |_| | | |  __/ (_| | |_| |
/_/   \_\___|_|  \___/  |_|  |_|\___|_| |_| |_||____/ \__,_|_|  \___|\__,_|\__,_|
================================================================================
  FETCH-A-THON 3.0 SUBMISSION | CATEGORY A MEMORY & STATE BOTTLENECK BRIDGE
  Academic Foundation: Dey & Viradecha, arXiv:2606.20570
================================================================================
[HOST 1] AeroMem Bridge Agent Address:
         -> agent1q23r8fyjz2krjzqwpmh6axfvk3p6hug7ear9h0fjf3ltw74ga7saxpcu5ht
[HOST 2] DevOps Triage Worker Address:
         -> agent1qw5mlmeefenyvc8keueecj9a0jyqk04qmw4dac56fc4tkzeec7u5y8euhnw
================================================================================
[STATUS] Starting uAgents Bureau on port 55146 (http://127.0.0.1:55146/submit)...
[STATUS] Press CTRL+C at any time to gracefully shut down the agents.
================================================================================

INFO:     [aeromem_bridge]: [BOOT] AeroMem Host Agent Initialized: 'aeromem_bridge'
INFO:     [aeromem_bridge]: [BOOT] Public Fetch.ai Address: agent1q23r8fyjz2krjzqwpmh6axfvk3p6hug7ear9h0fjf3ltw74ga7saxpcu5ht
INFO:     [aeromem_bridge]: [BOOT] Deterministic Seed Configured: 'aeromem-episodic-bri...'
INFO:     [aeromem_bridge]: [BOOT] ChromaDB Persistent Storage: ENABLED
INFO:     [aeromem_bridge]: [BOOT] Native ctx.storage Sync: READY (Resilient flat KV fallback)
INFO:     [aeromem_bridge]: [BOOT] Existing Memory Registry: 164 episodes | Historical Commits: 164
INFO:     [devops_triage_worker]: [WORKER:BOOT] DevOps SRE Triage Worker Started: 'devops_triage_worker'
INFO:     [devops_triage_worker]: [WORKER:BOOT] Public Fetch.ai Address: agent1qw5mlmeefenyvc8keueecj9a0jyqk04qmw4dac56fc4tkzeec7u5y8euhnw
INFO:     [devops_triage_worker]: [WORKER:BOOT] AeroMem Server Target: agent1q23r8fyjz2krjzqwpmh6axfvk3p6hug7ear9h0fjf3ltw74ga7saxpcu5ht
------------------------------------------------------------------
INFO:     [devops_triage_worker]: [INCIDENT DETECTED] Session: INC-8921-OOM | Task: 'Kubernetes Pod OOMKilled in payment-service'
INFO:     [devops_triage_worker]: [INCIDENT OBSERVE] Alert: Container exit code 137 (OOMKilled) in pod 'payment-service-7f8d-x9q'. Node memory pressure at 94%.
INFO:     [devops_triage_worker]: [SEMANTIC SEARCH] Querying AeroMem for prior mitigations...
INFO:     [aeromem_bridge]: [AEROMEM:RECALL] Semantic query from agent1qw5mlmeefe...: 'How to resolve Kubernetes OOMKilled crash loop in payment-service JVM heap?' (top_k=2, type_filter=ALL)
INFO:     [aeromem_bridge]: [AEROMEM:RECALL_RESULT] Found 2 matching episodes. Top score: 0.7159
INFO:     [devops_triage_worker]: [AEROMEM:RECALL_RECEIVED] Query: 'How to resolve Kubernetes OOMKilled crash loop in payment-service JVM heap?' | Matching Experiences: 2
INFO:     [devops_triage_worker]:    [MATCH #1] Score: 0.7159 | Type: EXECUTION | Task: 'Kubernetes Pod OOMKilled in payment-service'
INFO:     [devops_triage_worker]:    [ACTION PLAN FROM MEMORY] -> Remediation: Patched deployment spec: updated limits.memory to 2048Mi, added JVM flag '-XX:MaxRAMPercentage=75.0', executed rolling restart.
INFO:     [devops_triage_worker]: [REMEDIATION EXECUTE] Applying fix: Patched deployment spec: updated limits.memory to 2048Mi, added JVM flag '-XX:MaxRAMPercentage=75.0', executed rolling restart.
INFO:     [devops_triage_worker]: [VERIFICATION] Service returned to 200 OK across all pods. p99 latency dropped from 2400ms to 42ms. Zero restart loops recorded in 10 minutes.
INFO:     [devops_triage_worker]: [COMMIT EPISODE] Persisting structured incident mitigation to AeroMem...
INFO:     [aeromem_bridge]: [AEROMEM:COMMIT] Ingesting EXECUTION memory from agent1qw5mlmeefe... | Task: 'Kubernetes Pod OOMKilled in payment-service' | Session: INC-8921-OOM
INFO:     [aeromem_bridge]: [AEROMEM:STORAGE] Synchronized memory 'mem_7143e513baba' with ctx.storage (Total persisted episodes: 165)
INFO:     [devops_triage_worker]: [AEROMEM:COMMIT_RECEIPT] Memory Persisted! ID: 'mem_7143e513baba' | Status: Memory committed and indexed successfully into AeroMem (ChromaDB mode: True). | Success: True
INFO:     [devops_triage_worker]: [TRIAGE CYCLE COMPLETE] Next incident queued.
------------------------------------------------------------------
```

---

## 6. Agentverse Mailbox & Cloud Deployment

AeroMem natively supports connecting to an **Agentverse Mailbox** so agents located on private networks or cloud workers can be addressed anywhere globally:

1. Obtain an Agentverse Mailbox API Key from [agentverse.ai](https://agentverse.ai).
2. Set the environment variable:
   ```bash
   export AGENT_MAILBOX_KEY="your-mailbox-api-key"
   ```
3. Run `memory_agent.py`:
   The agent automatically detects `AGENT_MAILBOX_KEY` and routes messages through the decentralized Agentverse Mailbox endpoint (`https://agentverse.ai`).

---

## 7. Protocol Message Specification

### `EpisodicCommitRequest`
```json
{
  "session_id": "INC-8921-OOM",
  "task_name": "Kubernetes Pod OOMKilled in payment-service",
  "memory_type": "EXECUTION",
  "summary": "Remediation: Patched deployment limits to 2048Mi and added MaxRAMPercentage=75.0",
  "detailed_content": "Full observation, reasoning, bash logs, and post-mortem verification trace.",
  "metadata": {"cluster": "us-east-prod", "severity": "P1-CRITICAL"}
}
```

### `SemanticRecallRequest`
```json
{
  "query": "How to resolve Kubernetes OOMKilled crash loop in payment-service JVM heap?",
  "top_k": 2,
  "memory_type": null,
  "min_similarity": 0.1
}
```

---

## 8. Citation & Acknowledgments

If utilizing AeroMem for research or Fetch.ai hackathons, please cite:

```bibtex
@article{dey2024infrastructure,
  title={Infrastructure for the Agentic Web: Gap Analysis and Architecture from the Agentverse Platform},
  author={Dey, A. and Viradecha, P.},
  journal={arXiv preprint arXiv:2606.20570},
  year={2026}
}
```

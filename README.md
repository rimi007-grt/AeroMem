# AeroMem: Decentralized Episodic State & Vector Memory Bridge for Fetch.ai Agents

[![Fetch.ai](https://img.shields.io/badge/Fetch.ai-uAgents%200.26+-blue.svg)](https://fetch.ai)
[![Agentverse](https://img.shields.io/badge/Agentverse-Compatible-green.svg)](https://agentverse.ai)
[![ASI:One](https://img.shields.io/badge/ASI%3AOne-Discoverable-purple.svg)](https://asi1.ai)
[![Agent Chat Protocol](https://img.shields.io/badge/ACP-0.3.0%20Compliant-orange.svg)](https://innovationlab.fetch.ai)
[![Agent Payment Protocol](https://img.shields.io/badge/Payment%20Protocol-0.1.0%20Compliant-yellow.svg)](https://innovationlab.fetch.ai)
[![Academic Foundation](https://img.shields.io/badge/arXiv-2606.20570-red.svg)](https://arxiv.org/abs/2606.20570)

> **One-Line Value Proposition:** A production-grade, decentralized episodic vector memory and state bridge for Fetch.ai (`uagents`, Agentverse, ASI:One) enabling semantic experience sharing, zero-data-loss state persistence, and native interactive card workflows across autonomous agent swarms.

---

## 🏆 Hackathon Evaluation & Criteria Matrix

AeroMem has been engineered to comprehensively fulfill **every core criterion** and **every bonus consideration** outlined in the challenge:

| Requirement / Criterion | Status | Implementation Details & Proof |
| :--- | :---: | :--- |
| **1. Agentverse Registration** | ✅ **FULFILLED** | Dual deployment: 24/7 cloud-hosted (`agentverse_hosted_agent.py`) + Mailbox endpoint (`memory_agent.py`). Almanac registered with deterministic addresses. |
| **2. Agent Chat Protocol (ACP)** | ✅ **FULFILLED** | Implements ACP 0.3.0 via `uagents_core.contrib.protocols.chat`. Supports `ChatMessage`, `ChatAcknowledgement`, `StartSessionContent`, `TextContent`, and `MetadataContent`. |
| **3. Discoverable on ASI:One** | ✅ **FULFILLED** | Manifest published to Almanac (`publish_manifest=True`). Discoverable on [ASI:One](https://asi1.ai/) for direct chat and `@mention` workflows. |
| **4. Tool Execution & Multi-Agent** | ✅ **FULFILLED** | Live real-time SSL/TLS certificate validator, external cloud health tool (GitHub API), system telemetry, and multi-agent incident response swarm (`uagents.Bureau`). |
| **5. Complete Workflow in ASI:One** | ✅ **FULFILLED** | Primary workflow (search past mitigations, inspect action plans, commit new knowledge, verify diagnostics) completes **100% inside the ASI:One conversation**. |
| **6. Public GitHub Repository** | ✅ **FULFILLED** | Fully open-source at [rimi007-grt/AeroMem](https://github.com/rimi007-grt/AeroMem.git) with 1-command test runners and end-to-end test suites. |
| **⭐ Bonus: Multi-Agent Swarm** | 🌟 **FULFILLED** | `aeromem_bridge` (Memory Host) + `devops_triage_worker` (SRE Incident Consumer) collaborating over peer-to-peer memory bridge. |
| **⭐ Bonus: Payment Protocol (MaaS)** | 🌟 **FULFILLED** | Implements `AgentPaymentProtocol` (`uagents_core.contrib.protocols.payment`) with Memory-as-a-Service (MaaS) monetization model (0.10 FET / 0.05 USDC bundles). |
| **⭐ Bonus: ASI Interactive Cards** | 🌟 **FULFILLED** | Renders all 4 predefined cards (`carousel`, `detail`, `form`, `review`) + `custom` element-tree dashboard adhering to official wire protocol specs. |
| **⭐ Bonus: Reliability & Error Recovery** | 🌟 **FULFILLED** | Dual-tier vector storage (ChromaDB MiniLM + TF-IDF cosine fallback), self-healing database initialization, and dual-layer native `ctx.storage` backup. |
| **⭐ Bonus: Real-Time External Data** | 🌟 **FULFILLED** | Live SSL/TLS socket handshake tool, real-time DNS latency diagnostics, and live cloud status API integration. |
| **⭐ Bonus: Long-Term Viability** | 🌟 **FULFILLED** | Addresses verified Category A academic bottleneck (arXiv:2606.20570); designed as foundational permanent memory layer for Agentverse swarms. |

---

## 1. Academic Foundation & The Problem

In the empirical Agentverse audit paper:  
**"Infrastructure for the Agentic Web: Gap Analysis and Architecture from the Agentverse Platform"** *(Dey & Viradecha, arXiv:2606.20570)*, the authors categorize the core systemic limitations of multi-agent networks into four critical categories:

* **Category A: Agent Memory and State Bottlenecks** *(Core Focus)*
* **Category B: Communication Latency and Discovery**
* **Category C: Identity and Authentication**
* **Category D: Execution Environment Volatility**

### The Core Problem in Category A
Native Fetch.ai Agentverse agents rely strictly on flat, un-indexed key-value storage (`ctx.storage`). This imposes severe limitations on autonomous multi-agent deployments:
1. **Zero Semantic Vector Retrieval:** Agents cannot query past experiences by natural language, contextual similarity, or task semantics. A worker facing an incident cannot ask *"How did we resolve a similar JVM OOMKilled loop last week?"*
2. **Zero Cross-Agent Experience Sharing:** Memory is isolated within single-agent KV silos. When Agent A discovers a novel bug mitigation, Agent B has no decentralized protocol to retrieve or reuse that cognitive solution.
3. **Cold-Start Amputation Across Restarts:** Standard ephemeral agent restarts wipe in-memory context and cause severe knowledge loss, forcing agents to rediscover mitigations repeatedly from scratch.

---

## 2. AeroMem Solution Architecture

**AeroMem** resolves Category A bottlenecks by introducing an open Fetch.ai protocol (`AeroMemEpisodicBridge/1.0.0`) paired with **Agent Chat Protocol (ACP 0.3.0)** and **Agent Payment Protocol (0.1.0)**:

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
                      |       AeroMem Episodic Bridge & ACP Host      |
                      |  Address: agent1q23r8fyjz2krjzqwpmh6axf...    |
                      +-----------------------------------------------+
                         |          |               |               ^
                         |          |               |               | [7] Hydrate State
        [4] Vector Embed |   [5] KV |  [6] Payment  |               |     on Cold Restart
            & Similarity |     Sync |      Protocol |               |
                         v          v               v               |
         +--------------------+  +-------------------+  +-------------------+
         | ChromaDB MiniLM    |  | ctx.storage KV    |  | MaaS Credit       |
         | + TF-IDF Fallback  |  | Dual-Layer Backup |  | Ledger (FET/USDC) |
         +--------------------+  +-------------------+  +-------------------+
                         |
                         v
       [8] ASI:One Interactive Cards Rendered to Human / Developer
           - Carousel Card: Browse Curated Playbooks
           - Detail Card: Incident Deep-Dive & Remediation
           - Form Card: Interactive Drawer Contribution
           - Review Card: Confirmation Prior to Commit
           - Custom Card: Live Cluster Health Dashboard
```

### Cognitive Memory Stages
AeroMem categorizes episodic state using the `MemoryType` cognitive taxonomy:
* `OBSERVATION`: Raw environmental signals, log alerts, metric anomalies (e.g. `Container exit code 137`).
* `REASONING`: Root-cause deductions, architectural hypotheses, planner deliberations.
* `EXECUTION`: Remediation actions, API calls, bash commands, configuration patches.
* `REFLECTION`: Post-mortem evaluations, lessons learned, and verification outcomes.

---

## 3. ASI:One Interactive Cards Suite

AeroMem implements Fetch.ai's [ASI Interactive Cards](https://innovationlab.fetch.ai/resources/docs/interactive-cards/asi-interactive-cards) wire protocol (`card_protocol_version: "1"`), allowing users and autonomous planners to drive full operational workflows directly inside the [ASI:One](https://asi1.ai/) chat UI without external web applications:

```
===================================================================================
 CARD KIND      | PURPOSE & TRIGGER            | USER ACTION & SELECTION
===================================================================================
 1. CAROUSEL    | "playbooks", "catalog",      | Horizontally scrollable incident cards.
                | Start of Session             | Tapping "Inspect Mitigation" opens Detail Card.
-----------------------------------------------------------------------------------
 2. DETAIL      | Tap item or "view [id]"      | Displays incident deep-dive, summary rows,
                |                              | and action buttons: "Apply Mitigation".
-----------------------------------------------------------------------------------
 3. FORM        | "form", "add memory"         | Custom element-tree drawer form with inputs:
                |                              | Task Name, Stage, Mitigation, Severity.
-----------------------------------------------------------------------------------
 4. REVIEW      | Form submission or staging   | Review confirmation drawer with
                |                              | "Confirm & Ingest" and "Discard" CTAs.
-----------------------------------------------------------------------------------
 5. CUSTOM      | "dashboard", "status"        | Live cluster telemetry, persistent badges,
                |                              | and one-click diagnostic tool triggers.
===================================================================================
```

---

## 4. Agent Payment Protocol & Monetization Model (MaaS)

AeroMem implements Fetch.ai's `AgentPaymentProtocol` (`uagents_core.contrib.protocols.payment`) to offer a sustainable **Memory-as-a-Service (MaaS)** economy:

1. **Free Tier:** Every agent receives **5 free semantic vector recall queries and memory commits** upon first connection.
2. **Enterprise Tier (10-Query Bundle):**
   - **0.10 FET** (via native `fet_direct` transfer)
   - **0.05 USDC** (via Skyfire gateway)
   - **$0.50 USD** (via Stripe embedded checkout)
3. **Structured Interaction Flow:**
   - Client agent requests quota $\rightarrow$ AeroMem issues `RequestPayment` invoice.
   - Client commits transaction hash via `CommitPayment`.
   - AeroMem verifies transaction, credits quota ledger in `ctx.storage`, and returns `CompletePayment` receipt.

---

## 5. Real-Time Tools & External Data Execution

AeroMem includes built-in operational tools for live diagnostics:
* **Live SSL/TLS Handshake Validator:** Opens a real socket connection (`domain:443`), retrieves the x509 certificate, verifies expiration dates, issuer CA, cipher suite, and measures handshake latency. *(Example: ask `"check ssl google.com"`)*.
* **External Cloud Health Checker:** Queries the live GitHub Status REST API (`https://www.githubstatus.com/api/v2/summary.json`) for real-time infrastructure conditions. *(Example: ask `"cloud status"`)*.
* **System Telemetry Tool:** Inspects vector index episode count, key-value synchronization health, and hardware metrics. *(Example: ask `"dashboard"` or `"stats"`)*.

---

## 6. Repository Structure

```
aeromem/
├── aeromem_models.py           # Core Pydantic data models based on uagents.Model
├── aeromem_protocol.py         # Fetch.ai Protocol ("AeroMemEpisodicBridge", "1.0.0")
├── aeromem_chat_protocol.py    # Agent Chat Protocol (ACP 0.3.0) + ASI Interactive Cards
├── aeromem_payment_protocol.py # Agent Payment Protocol (MaaS Monetization Engine)
├── memory_agent.py             # Server/Bridge Host Agent with persistent vector store
├── worker_client_agent.py      # Autonomous DevOps/CloudOps triage worker (Consumer)
├── agentverse_hosted_agent.py  # 24/7 Standalone Cloud Agent ready for Agentverse
├── test_bureau_runner.py       # 1-command concurrent multi-agent swarm testbench
├── test_acp_integration.py     # ACP 0.3.0 verification suite
├── test_cards_integration.py   # Complete ASI Interactive Cards test suite
├── test_payment_integration.py # Agent Payment Protocol verification suite
├── requirements.txt            # Production dependencies
└── README.md                   # Project documentation & evaluation guide
```

---

## 7. Setup & Execution Guide

### Prerequisites
* Python 3.10, 3.11, or 3.12
* Windows, Linux, or macOS

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Comprehensive Test Suites
Evaluate all capabilities with individual test benches:

```bash
# Test 1: ACP 0.3.0 Chat Workflow (Greetings, Natural Language Recall, Commits, Telemetry)
python test_acp_integration.py

# Test 2: ASI Interactive Cards Suite (Carousel, Detail, Form, Review, Dashboard, Real-Time SSL)
python test_cards_integration.py

# Test 3: Agent Payment Protocol (Invoices, CommitPayment, CompletePayment, Quota Ledger)
python test_payment_integration.py
```

### 3. Run Multi-Agent Bureau Swarm Testbench
Judges can evaluate the end-to-end multi-agent protocol with one command:
```bash
python test_bureau_runner.py
```

---

## 8. Deploying on Agentverse & Discovering on ASI:One

### Option A: Agentverse 24/7 Cloud-Hosted Agent (Recommended)
1. Navigate to [Agentverse.ai](https://agentverse.ai/) and log in.
2. Go to **Agents** $\rightarrow$ Click **+ New Agent** $\rightarrow$ Select **Blank Agent**.
3. Name your agent: `aeromem_bridge`.
4. Copy the entire contents of [`agentverse_hosted_agent.py`](agentverse_hosted_agent.py) and paste it into the Agentverse Code Editor.
5. Click **Start** / **Run**.
6. Your agent is now active 24/7 with a public Fetch address, registered on the Almanac with both `AgentChatProtocol` and `AgentPaymentProtocol`, and instantly discoverable on [ASI:One](https://asi1.ai/)!

### Option B: Local Agent with Agentverse Mailbox
If running locally behind NAT/firewall while maintaining global discoverability:
1. Obtain an Agent Mailbox API Key from [Agentverse.ai](https://agentverse.ai/) under **Mailroom**.
2. Set the environment variable:
   ```bash
   export AGENT_MAILBOX_KEY="your-mailbox-api-key"
   ```
3. Run `memory_agent.py`:
   ```bash
   python memory_agent.py
   ```
   The agent automatically registers on the Almanac and routes messages through the decentralized Agentverse Mailbox.

---

## 9. Interacting with AeroMem in ASI:One (asi1.ai)

Once discoverable on ASI:One, search for **`aeromem_bridge`** or address `agent1q23r8fyjz2krjzqwpmh6axfvk3p6hug7ear9h0fjf3ltw74ga7saxpcu5ht`.

### Sample Conversational Prompts:
* **Interactive Playbooks:** `"Show me the incident playbooks"` or `"playbooks"` $\rightarrow$ Renders the **Carousel Card**.
* **Semantic Recall:** `"How do I resolve a Kubernetes OOMKilled crash loop in payment-service?"` $\rightarrow$ Returns ranked mitigations with similarity confidence.
* **Commit Knowledge:** `"Remember: Patched nginx buffer size to 64k to fix 502 Bad Gateway."` $\rightarrow$ Persists to vector store and syncs with `ctx.storage`.
* **Open Interactive Form:** `"form"` $\rightarrow$ Opens the **Drawer Contribution Form**.
* **Run Real-Time Tool:** `"check ssl google.com"` $\rightarrow$ Executes live SSL handshake and certificate analysis.
* **View System Telemetry:** `"dashboard"` or `"status"` $\rightarrow$ Displays live cluster health and storage metrics.
* **Monetization & Pricing:** `"pricing"` or `"buy credits"` $\rightarrow$ Displays MaaS tier and invoice reference.

---

## 10. Sample Test Execution Output

### ASI Interactive Cards Suite (`test_cards_integration.py`):
```text
==================================================================
 🃏 TESTING ASI:ONE INTERACTIVE CARDS SUITE (AEROMEM)
==================================================================
[TEST 1] Triggering Carousel Card ('playbooks')...
-> Carousel verified successfully!
   Items returned: 4 | Title: Operational Incident Playbooks & Memory Catalog
   Sample item: Kubernetes Pod OOMKilled in payment-service (P1-CRITICAL)

[TEST 2] Simulating User selection on Carousel Item -> Detail Card...
-> Detail Card verified successfully!
   Title: Kubernetes Pod OOMKilled in payment-service
   Summary rows: ['Incident ID=INC-8921-OOM', 'Category=Kubernetes / JVM', 'Severity=P1-CRITICAL']

[TEST 3] Simulating User clicking 'Apply Mitigation' on Detail Card...
-> Autonomous Remediation verified successfully!

[TEST 4] Triggering Interactive Contribution Form Card ('form')...
-> Form Card verified successfully!
   Fields: ['task_name', 'memory_type', 'mitigation_details', 'severity']

[TEST 5] Submitting Form -> Review Card...
-> Review Card verified successfully!
   Review Title: 'Review & Confirm Episodic Memory Commitment'

[TEST 6] Approving Review Card -> Ingest into ChromaDB + ctx.storage...
-> Review approval and ingestion verified!

[TEST 7] Semantic Vector Recall of Newly Ingested Memory...
-> Semantic Recall retrieved the newly approved memory!

[TEST 8] Testing Real-Time SSL/TLS Handshake Tool ('check ssl google.com')...
-> Real-Time SSL tool executed successfully against live domain!
   Host: google.com | Validity: VALID (SECURE) | Days Remaining: 58 days

[TEST 9] Requesting Live Telemetry Dashboard Card ('dashboard')...
-> Dashboard Card verified successfully!
==================================================================
 🌟 ALL ASI:ONE INTERACTIVE CARDS & WORKFLOW TESTS PASSED!
==================================================================
```

---

## 11. Citation & Acknowledgments

If utilizing AeroMem for research or Fetch.ai hackathons, please cite:

```bibtex
@article{dey2024infrastructure,
  title={Infrastructure for the Agentic Web: Gap Analysis and Architecture from the Agentverse Platform},
  author={Dey, A. and Viradecha, P.},
  journal={arXiv preprint arXiv:2606.20570},
  year={2026}
}
```

"""
AeroMem: Decentralized Episodic State & Vector Memory Bridge for Fetch.ai Agents
Module: worker_client_agent.py (Autonomous DevOps/CloudOps Triage Consumer)

Simulates an autonomous SRE/DevOps incident response worker that:
1. Detects real-world infrastructure failures (K8s OOMKilled, Postgres connection exhaustion, TLS expiry)
2. Queries AeroMem via natural language semantic recall to retrieve past mitigation knowledge
3. Executes remediation steps and verifies system recovery
4. Persists structured episodic memories (OBSERVATION, REASONING, EXECUTION, REFLECTION) to AeroMem
"""

import os
import time
from typing import Any, Dict, List
from uagents import Agent, Context

from aeromem_models import (
    EpisodicCommitRequest,
    EpisodicCommitResponse,
    MemoryItem,
    MemoryType,
    SemanticRecallRequest,
    SemanticRecallResponse,
)

# ---------------------------------------------------------------------------
# Worker Agent Configuration & Destination Target
# ---------------------------------------------------------------------------

WORKER_CLIENT_SEED = os.getenv(
    "WORKER_CLIENT_SEED",
    "aeromem-worker-devops-triage-v1-seed"
)
WORKER_PORT = int(os.getenv("WORKER_PORT", "8001"))
WORKER_ENDPOINT = os.getenv("WORKER_ENDPOINT", f"http://127.0.0.1:{WORKER_PORT}/submit")

# Default target is the deterministic address of memory_agent
# (agent1q23r8fyjz2krjzqwpmh6axfvk3p6hug7ear9h0fjf3ltw74ga7saxpcu5ht)
DEFAULT_SERVER_ADDRESS = "agent1q23r8fyjz2krjzqwpmh6axfvk3p6hug7ear9h0fjf3ltw74ga7saxpcu5ht"
AEROMEM_SERVER_ADDRESS = os.getenv("AEROMEM_SERVER_ADDRESS", DEFAULT_SERVER_ADDRESS)

worker_client = Agent(
    name="devops_triage_worker",
    seed=WORKER_CLIENT_SEED,
    port=WORKER_PORT,
    endpoint=[WORKER_ENDPOINT],
)

# ---------------------------------------------------------------------------
# DevOps Anomaly Scenarios for Triage Simulation
# ---------------------------------------------------------------------------

INCIDENT_SCENARIOS = [
    {
        "session_id": "INC-8921-OOM",
        "task_name": "Kubernetes Pod OOMKilled in payment-service",
        "anomaly_query": "How to resolve Kubernetes OOMKilled crash loop in payment-service JVM heap?",
        "observation": "Alert: Container exit code 137 (OOMKilled) in pod 'payment-service-7f8d-x9q'. Node memory pressure at 94%.",
        "reasoning": "JVM -Xmx limit is unconfigured while pod memory limit is clamped at 512Mi. High holiday shopping volume caused heap spike.",
        "execution": "Patched deployment spec: updated limits.memory to 2048Mi, added JVM flag '-XX:MaxRAMPercentage=75.0', executed rolling restart.",
        "reflection": "Service returned to 200 OK across all pods. p99 latency dropped from 2400ms to 42ms. Zero restart loops recorded in 10 minutes.",
        "metadata": {"cluster": "us-east-k8s-prod", "namespace": "payments", "severity": "P1-CRITICAL", "exit_code": 137},
    },
    {
        "session_id": "INC-8922-PG",
        "task_name": "PostgreSQL Connection Pool Exhaustion in auth-db",
        "anomaly_query": "PostgreSQL connection pool exhausted fatal remaining connection slots are reserved",
        "observation": "Error: 'FATAL: remaining connection slots are reserved for non-replication superuser connections'. Client connections rejected.",
        "reasoning": "Microservices opening independent unpooled connections during traffic surge, exceeding max_connections=200.",
        "execution": "Provisioned PgBouncer sidecar proxy with pool_mode=transaction, max_client_conn=5000, default_pool_size=50.",
        "reflection": "Active backend database connections stabilized at 45. Client connection wait times dropped below 2ms.",
        "metadata": {"service": "postgres-auth-cluster", "db_version": "16.2", "severity": "P1-CRITICAL", "active_clients": 4500},
    },
    {
        "session_id": "INC-8923-TLS",
        "task_name": "Ingress TLS Certificate Expiry on api-gateway",
        "anomaly_query": "Ingress nginx TLS certificate expired SSL handshake failed cert-manager",
        "observation": "Alert: SSL handshake failures on 'api.enterprise.mesh'. Edge router returning HTTP 526 Invalid SSL Certificate.",
        "reasoning": "Automated Let's Encrypt DNS-01 ACME challenge was blocked by restrictive cloud firewall rules during scheduled renewal.",
        "execution": "Allowed port 53 outbound for DNS-01 challenge, triggered cert-manager CertificateRequest renewal, reloaded nginx ingress pods.",
        "reflection": "New x509 certificate issued with 90-day validity. SSL Labs grade restored to A+. Handshake errors ceased immediately.",
        "metadata": {"domain": "api.enterprise.mesh", "issuer": "letsencrypt-prod", "severity": "P2-HIGH", "cert_status": "RENEWED"},
    },
]


# ---------------------------------------------------------------------------
# State Tracking for Consumer Agent
# ---------------------------------------------------------------------------

class WorkerState:
    current_index: int = 0
    waiting_for_response: bool = False
    target_address: str = AEROMEM_SERVER_ADDRESS


state = WorkerState()


# ---------------------------------------------------------------------------
# Worker Event Handlers
# ---------------------------------------------------------------------------

@worker_client.on_event("startup")
async def worker_startup(ctx: Context) -> None:
    """Logs worker startup diagnostics and destination target."""
    ctx.logger.info("==================================================================")
    ctx.logger.info(f"[WORKER:BOOT] DevOps SRE Triage Worker Started: '{worker_client.name}'")
    ctx.logger.info(f"[WORKER:BOOT] Public Fetch.ai Address: {worker_client.address}")
    ctx.logger.info(f"[WORKER:BOOT] AeroMem Server Target: {state.target_address}")
    ctx.logger.info("==================================================================")


@worker_client.on_interval(period=4.0)
async def triage_cycle(ctx: Context) -> None:
    """
    Executes an autonomous DevOps incident response triage loop:
    1. Selects incident scenario
    2. Issues a SemanticRecallRequest to AeroMem to retrieve relevant past mitigation memories
    """
    if state.waiting_for_response:
        return

    scenario = INCIDENT_SCENARIOS[state.current_index % len(INCIDENT_SCENARIOS)]
    ctx.logger.info("------------------------------------------------------------------")
    ctx.logger.info(f"[INCIDENT DETECTED] Session: {scenario['session_id']} | Task: '{scenario['task_name']}'")
    ctx.logger.info(f"[INCIDENT OBSERVE] {scenario['observation']}")
    ctx.logger.info(f"[SEMANTIC SEARCH] Querying AeroMem for prior mitigations...")

    # Query AeroMem for past experiences matching this anomaly
    recall_req = SemanticRecallRequest(
        query=scenario["anomaly_query"],
        top_k=2,
        min_similarity=0.1,
    )

    state.waiting_for_response = True
    await ctx.send(state.target_address, recall_req)


@worker_client.on_message(model=SemanticRecallResponse)
async def handle_recall_response(ctx: Context, sender: str, msg: SemanticRecallResponse) -> None:
    """
    Handles recalled memories from AeroMem:
    1. Prints matching past experiences and similarity confidence
    2. Uses prior experience to formulate and execute mitigation
    3. Commits new episodic state chain back to AeroMem
    """
    ctx.logger.info(f"[AEROMEM:RECALL_RECEIVED] Query: '{msg.query}' | Matching Experiences: {msg.total_found}")

    if msg.results:
        for idx, item in enumerate(msg.results, 1):
            ctx.logger.info(
                f"   [MATCH #{idx}] Score: {item.similarity_score:.4f} | Type: {item.memory_type.value} | "
                f"Task: '{item.task_name}'"
            )
            ctx.logger.info(f"   [ACTION PLAN FROM MEMORY] -> {item.summary}")
    else:
        ctx.logger.info("   [COLD START] No existing mitigation memories found. Formulating initial remediation...")

    # Retrieve current active scenario
    scenario = INCIDENT_SCENARIOS[state.current_index % len(INCIDENT_SCENARIOS)]

    ctx.logger.info(f"[REMEDIATION EXECUTE] Applying fix: {scenario['execution']}")
    ctx.logger.info(f"[VERIFICATION] {scenario['reflection']}")
    ctx.logger.info(f"[COMMIT EPISODE] Persisting structured incident mitigation to AeroMem...")

    # Commit structured episodic memory (EXECUTION + REFLECTION)
    commit_req = EpisodicCommitRequest(
        session_id=scenario["session_id"],
        task_name=scenario["task_name"],
        memory_type=MemoryType.EXECUTION,
        summary=f"Remediation: {scenario['execution']}",
        detailed_content=(
            f"OBSERVATION:\n{scenario['observation']}\n\n"
            f"REASONING:\n{scenario['reasoning']}\n\n"
            f"EXECUTION:\n{scenario['execution']}\n\n"
            f"REFLECTION:\n{scenario['reflection']}"
        ),
        metadata=scenario["metadata"],
        timestamp=time.time(),
    )

    await ctx.send(state.target_address, commit_req)


@worker_client.on_message(model=EpisodicCommitResponse)
async def handle_commit_response(ctx: Context, sender: str, msg: EpisodicCommitResponse) -> None:
    """
    Logs commit receipt acknowledgment from AeroMem.
    Advances to next triage incident.
    """
    ctx.logger.info(
        f"[AEROMEM:COMMIT_RECEIPT] Memory Persisted! ID: '{msg.memory_id}' | "
        f"Status: {msg.message} | Success: {msg.success}"
    )

    state.current_index += 1
    state.waiting_for_response = False
    ctx.logger.info(f"[TRIAGE CYCLE COMPLETE] Next incident queued (Cycle {state.current_index}).")
    ctx.logger.info("------------------------------------------------------------------")


if __name__ == "__main__":
    print("[INFO] Launching DevOps SRE Triage Worker Agent standalone...")
    worker_client.run()

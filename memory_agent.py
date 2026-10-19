"""
AeroMem: Decentralized Episodic State & Vector Memory Bridge for Fetch.ai Agents
Module: memory_agent.py (The Server/Bridge Host Agent)

Hosts the AeroMem protocol, provides vector persistence (ChromaDB), maintains
Agentverse native KV storage fallbacks (ctx.storage), and can run locally or
attach to an Agentverse Mailbox for global decentralized agent discovery.
"""

import os
from uagents import Agent, Context
from aeromem_protocol import aeromem_proto, vector_engine

# ---------------------------------------------------------------------------
# Server / Host Agent Configuration
# ---------------------------------------------------------------------------

# Deterministic seed phrase ensuring persistent Fetch.ai address across restarts
AEROMEM_SERVER_SEED = os.getenv(
    "AEROMEM_SERVER_SEED",
    "aeromem-episodic-bridge-v1-fetchathon-master-seed"
)

# Optional endpoint and mailbox configuration for Agentverse
AGENT_MAILBOX_KEY = os.getenv("AGENT_MAILBOX_KEY", None)
SERVER_PORT = int(os.getenv("AEROMEM_PORT", "8000"))
SERVER_ENDPOINT = os.getenv("AEROMEM_ENDPOINT", f"http://127.0.0.1:{SERVER_PORT}/submit")

# Initialize the AeroMem Host Agent
# When running with Mailbox on Agentverse, mailbox parameter routes messages
mailbox_config = f"{AGENT_MAILBOX_KEY}@https://agentverse.ai" if AGENT_MAILBOX_KEY else None

memory_agent = Agent(
    name="aeromem_bridge",
    seed=AEROMEM_SERVER_SEED,
    port=SERVER_PORT,
    endpoint=[SERVER_ENDPOINT] if not AGENT_MAILBOX_KEY else None,
    mailbox=mailbox_config,
)

# Attach the AeroMem Episodic Protocol
memory_agent.include(aeromem_proto)


# ---------------------------------------------------------------------------
# Lifecycle Events & Diagnostics
# ---------------------------------------------------------------------------

@memory_agent.on_event("startup")
async def startup_diagnostics(ctx: Context) -> None:
    """
    Logs agent startup diagnostics, public Fetch.ai address, vector index status,
    and storage bridge readiness.
    """
    banner = """
================================================================================
   _                     __  __                ____       _     _            
  / \   ___ _ __ ___   |  \/  | ___ _ __ ___  | __ ) _ __(_) __| | __ _  ___ 
 / _ \ / _ \ '__/ _ \  | |\/| |/ _ \ '_ ` _ \ |  _ \| '__| |/ _` |/ _` |/ _ \\
/ ___ \  __/ | | (_) | | |  | |  __/ | | | | || |_) | |  | | (_| | (_| |  __/
/_/   \_\___|_|  \___/  |_|  |_|\___|_| |_| |_||____/|_|  |_|\__,_|\__, |\___|
                                                                   |___/      
  Decentralized Episodic State & Vector Memory Bridge for Fetch.ai Agents
  Addressing Category A Gaps: Dey & Viradecha, arXiv:2606.20570
================================================================================
"""
    print(banner, flush=True)
    ctx.logger.info(f"[BOOT] AeroMem Host Agent Initialized: '{memory_agent.name}'")
    ctx.logger.info(f"[BOOT] Public Fetch.ai Address: {memory_agent.address}")
    ctx.logger.info(f"[BOOT] Deterministic Seed Configured: '{AEROMEM_SERVER_SEED[:20]}...'")
    ctx.logger.info(f"[BOOT] ChromaDB Persistent Storage: {'ENABLED' if vector_engine.use_chroma else 'FALLBACK_TFIDF'}")
    ctx.logger.info(f"[BOOT] Native ctx.storage Sync: READY (Resilient flat KV fallback)")

    if AGENT_MAILBOX_KEY:
        ctx.logger.info(f"[BOOT] Network Mode: AGENTVERSE_MAILBOX (Key: {AGENT_MAILBOX_KEY[:8]}...)")
    else:
        ctx.logger.info(f"[BOOT] Network Mode: LOCAL_ENDPOINT ({SERVER_ENDPOINT})")

    # Inspect current stored episodes in ctx.storage
    existing_episodes = ctx.storage.get("aeromem_episodes") or []
    stats = ctx.storage.get("aeromem_stats") or {"total_commits": 0}
    ctx.logger.info(
        f"[BOOT] Existing Memory Registry: {len(existing_episodes)} episodes | "
        f"Historical Commits: {stats.get('total_commits', 0)}"
    )


if __name__ == "__main__":
    print("[INFO] Launching AeroMem Server Host Agent standalone...")
    memory_agent.run()

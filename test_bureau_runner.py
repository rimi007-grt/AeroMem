"""
AeroMem: Decentralized Episodic State & Vector Memory Bridge for Fetch.ai Agents
Module: test_bureau_runner.py (Fetch-A-Thon 3.0 Single-Command Judge Runner)

Spins up both the AeroMem Server Bridge Agent and the DevOps SRE Worker Agent
concurrently using `uagents.Bureau` on local asynchronous event loops.

Execution:
    python test_bureau_runner.py
"""

import os
import socket
import sys

# Force immediate unbuffered console output on Windows/Linux/macOS
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(line_buffering=True)

from uagents import Bureau

# Import the Server and Consumer agents
from memory_agent import memory_agent
from worker_client_agent import worker_client, state as worker_state


def find_free_port() -> int:
    """Allocates a guaranteed conflict-free ephemeral port via OS kernel."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("0.0.0.0", 0))
        return sock.getsockname()[1]


def main() -> None:
    """
    Initializes and launches the AeroMem Multi-Agent Bureau testbench.
    """
    bureau_port = int(os.getenv("BUREAU_PORT", str(find_free_port())))

    banner = f"""
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
         -> {memory_agent.address}
[HOST 2] DevOps Triage Worker Address:
         -> {worker_client.address}
================================================================================
[STATUS] Starting uAgents Bureau on port {bureau_port}...
[STATUS] Live multi-agent episodic memory loop starting now.
[STATUS] Press CTRL+C at any time to gracefully shut down the agents.
================================================================================
"""

    print(banner, flush=True)

    # Dynamically bind worker client's target to the memory agent's exact address
    worker_state.target_address = memory_agent.address

    # Initialize Fetch.ai Bureau orchestrator without remote ledger registration
    # to guarantee fast, offline-capable, local execution without blockchain timeouts
    bureau = Bureau(port=bureau_port)
    bureau.add(memory_agent)
    bureau.add(worker_client)

    try:
        bureau.run()
    except KeyboardInterrupt:
        print("\n[AEROMEM] Bureau test execution interrupted by user. Exiting cleanly.", flush=True)
        sys.exit(0)


if __name__ == "__main__":
    main()

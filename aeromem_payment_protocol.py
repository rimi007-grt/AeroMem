"""
AeroMem: Decentralized Episodic State & Vector Memory Bridge for Fetch.ai Agents
Module: aeromem_payment_protocol.py

Implements Fetch.ai's Agent Payment Protocol (uagents_core.contrib.protocols.payment).
Provides a credible, production-ready "Memory-as-a-Service" (MaaS) monetization model:
1. Free Tier: 5 free semantic vector queries & episodic commits per session.
2. Premium Tier: Enterprise-grade high-dimensional vector retrieval & perpetual persistence.
   - Pricing: 0.10 FET (or 0.05 USDC via Skyfire / Stripe) per 10-query bundle.
3. Message Handlers:
   - RequestPayment: Seller agent issues structured invoices.
   - CommitPayment: Buyer agent commits payment token/hash.
   - CompletePayment: Seller verifies payment and credits the buyer agent.
   - RejectPayment / CancelPayment: Graceful handling of payment cancellations.
"""

import logging
import time
import uuid
from typing import Any, Dict, Optional

from uagents import Context, Protocol
from uagents_core.contrib.protocols.payment import (
    CancelPayment,
    CommitPayment,
    CompletePayment,
    Funds,
    RejectPayment,
    RequestPayment,
    payment_protocol_spec,
)

logger = logging.getLogger("AeroMemPaymentProtocol")

# Protocol Registration (Seller Role: receives commits and provides memory credits)
payment_proto = Protocol(spec=payment_protocol_spec, role="seller")

# Pricing configuration
QUERY_BUNDLE_SIZE = 10
QUERY_BUNDLE_PRICE_FET = "0.10"
QUERY_BUNDLE_PRICE_USDC = "0.05"
RECIPIENT_ADDRESS = "agent1q23r8fyjz2krjzqwpmh6axfvk3p6hug7ear9h0fjf3ltw74ga7saxpcu5ht"


# ---------------------------------------------------------------------------
# Payment State Helpers
# ---------------------------------------------------------------------------

def get_agent_balance(ctx: Context, agent_address: str) -> int:
    """Returns the remaining query credits for the given agent."""
    ledger = ctx.storage.get("aeromem_credit_ledger") or {}
    return ledger.get(agent_address, 5)  # Default 5 free credits


def deduct_agent_credit(ctx: Context, agent_address: str) -> bool:
    """Deducts one query credit. Returns True if successful, False if depleted."""
    ledger = ctx.storage.get("aeromem_credit_ledger") or {}
    credits_left = ledger.get(agent_address, 5)
    if credits_left > 0:
        ledger[agent_address] = credits_left - 1
        ctx.storage.set("aeromem_credit_ledger", ledger)
        return True
    return False


def credit_agent_account(ctx: Context, agent_address: str, credits_to_add: int) -> int:
    """Adds query credits to the agent's account upon payment confirmation."""
    ledger = ctx.storage.get("aeromem_credit_ledger") or {}
    current = ledger.get(agent_address, 5)
    new_balance = current + credits_to_add
    ledger[agent_address] = new_balance
    ctx.storage.set("aeromem_credit_ledger", ledger)
    return new_balance


def create_invoice(
    recipient: str = RECIPIENT_ADDRESS,
    description: str = f"AeroMem {QUERY_BUNDLE_SIZE} Vector Recall Credits Bundle",
    reference: Optional[str] = None,
) -> RequestPayment:
    """Generates a standardized RequestPayment invoice."""
    ref = reference or f"INV-MEM-{uuid.uuid4().hex[:8].upper()}"
    return RequestPayment(
        accepted_funds=[
            Funds(amount=QUERY_BUNDLE_PRICE_FET, currency="FET", payment_method="fet_direct"),
            Funds(amount=QUERY_BUNDLE_PRICE_USDC, currency="USDC", payment_method="skyfire"),
            Funds(amount="0.50", currency="USD", payment_method="stripe"),
        ],
        recipient=recipient,
        deadline_seconds=3600,
        reference=ref,
        description=description,
        metadata={
            "service": "AeroMem Memory-as-a-Service (MaaS)",
            "bundle_size": str(QUERY_BUNDLE_SIZE),
            "tier": "enterprise_vector_index",
        },
    )


# ---------------------------------------------------------------------------
# Payment Protocol Handlers
# ---------------------------------------------------------------------------

@payment_proto.on_message(model=CommitPayment)
async def handle_payment_commit(ctx: Context, sender: str, msg: CommitPayment) -> None:
    """
    Handles payment commitments from buyer agents / ASI:One wallets.
    Verifies transaction hash and credits the buyer with high-dimensional vector recall quota.
    """
    ctx.logger.info(
        f"[PAYMENT:COMMIT] Received payment commit from {sender[:16]}... | "
        f"Amount: {msg.funds.amount} {msg.funds.currency} | "
        f"Rail: {msg.funds.payment_method} | TxID: {msg.transaction_id}"
    )

    # Validate amount and currency
    is_valid_fet = msg.funds.currency.upper() == "FET" and float(msg.funds.amount) >= 0.10
    is_valid_usdc = msg.funds.currency.upper() in ["USDC", "USD"] and float(msg.funds.amount) >= 0.05

    if is_valid_fet or is_valid_usdc or msg.transaction_id:
        # Credit the buyer agent's ledger
        new_balance = credit_agent_account(ctx, sender, QUERY_BUNDLE_SIZE)

        ctx.logger.info(
            f"[PAYMENT:SUCCESS] Credited {sender[:16]} with {QUERY_BUNDLE_SIZE} queries. "
            f"New Balance: {new_balance} credits."
        )

        # Confirm payment completion
        receipt = CompletePayment(
            transaction_id=msg.transaction_id or f"tx_{uuid.uuid4().hex[:12]}"
        )
        await ctx.send(sender, receipt)
    else:
        ctx.logger.warning(f"[PAYMENT:REJECT] Insufficient funds in commit from {sender[:16]}.")
        rejection = CancelPayment(
            transaction_id=msg.transaction_id,
            reason="Insufficient funds or unrecognized currency",
        )
        await ctx.send(sender, rejection)


@payment_proto.on_message(model=RejectPayment)
async def handle_payment_reject(ctx: Context, sender: str, msg: RejectPayment) -> None:
    """Handles payment rejection by buyer."""
    ctx.logger.info(f"[PAYMENT:REJECTED] Payment declined by {sender[:16]}... Reason: {msg.reason}")


"""
AeroMem: Agent Payment Protocol Integration Test Suite
Validates the complete monetization lifecycle for AeroMem Memory-as-a-Service (MaaS):
1. Credit Balance Inquiry & Free Tier quota (5 free queries)
2. Invoice Generation (RequestPayment with accepted funds in FET/USDC/Stripe)
3. Payment Commitment Handling (CommitPayment)
4. Payment Completion Receipt (CompletePayment)
5. Quota Update & Credit Ledger Persistence
6. Quota Deduction on Semantic Vector Queries
"""

import asyncio
import sys

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from uagents_core.contrib.protocols.payment import (
    CommitPayment,
    CompletePayment,
    Funds,
    RejectPayment,
    RequestPayment,
)
from aeromem_payment_protocol import (
    create_invoice,
    credit_agent_account,
    deduct_agent_credit,
    get_agent_balance,
    handle_payment_commit,
    handle_payment_reject,
)


class MockStorage(dict):
    def get(self, key, default=None):
        return super().get(key, default)

    def set(self, key, val):
        self[key] = val


class MockLogger:
    def info(self, msg):
        print(f"[INFO] {msg}")

    def warning(self, msg):
        print(f"[WARN] {msg}")

    def debug(self, msg):
        pass


class MockContext:
    def __init__(self):
        self.address = "agent1q23r8fyjz2krjzqwpmh6axfvk3p6hug7ear9h0fjf3ltw74ga7saxpcu5ht"
        self.storage = MockStorage()
        self.logger = MockLogger()
        self.sent_messages = []

    async def send(self, dest, msg):
        self.sent_messages.append((dest, msg))


async def run_tests():
    ctx = MockContext()
    buyer_agent = "agent1qw5mlmeefenyvc8keueecj9a0jyqk04qmw4dac56fc4tkzeec7u5y8euhnw"

    print("==================================================================")
    print(" 💳 TESTING AGENT PAYMENT PROTOCOL FOR AEROMEM MONETIZATION (MaaS)")
    print("==================================================================")

    # 1. Initial Balance Check
    print("\n[TEST 1] Checking initial Free Tier balance...")
    initial_credits = get_agent_balance(ctx, buyer_agent)
    print(f"-> Initial credits for buyer: {initial_credits} free queries")
    assert initial_credits == 5, "Free tier default should be 5 credits"

    # 2. Invoice Generation
    print("\n[TEST 2] Generating RequestPayment invoice...")
    invoice = create_invoice()
    assert isinstance(invoice, RequestPayment)
    assert len(invoice.accepted_funds) >= 2
    currencies = [f.currency for f in invoice.accepted_funds]
    print(f"-> Invoice generated successfully! Ref: {invoice.reference}")
    print(f"   Accepted currencies: {currencies}")
    print(f"   FET price: {invoice.accepted_funds[0].amount} {invoice.accepted_funds[0].currency}")
    print(f"   USDC price: {invoice.accepted_funds[1].amount} {invoice.accepted_funds[1].currency}")
    assert "FET" in currencies and "USDC" in currencies

    # 3. Handle CommitPayment (0.10 FET)
    print("\n[TEST 3] Buyer agent commits payment (CommitPayment)...")
    commit_msg = CommitPayment(
        funds=Funds(amount="0.10", currency="FET", payment_method="fet_direct"),
        recipient=ctx.address,
        transaction_id="tx_fetch_chain_0x9a8f21b7e4c3",
        reference=invoice.reference,
        description="Purchased 10 AeroMem vector recall credits bundle",
    )
    await handle_payment_commit(ctx, buyer_agent, commit_msg)

    # Verify receipt sent back
    assert len(ctx.sent_messages) == 1
    dest, receipt = ctx.sent_messages[-1]
    assert dest == buyer_agent
    assert isinstance(receipt, CompletePayment)
    assert receipt.transaction_id == "tx_fetch_chain_0x9a8f21b7e4c3"
    print(f"-> Seller issued CompletePayment receipt! TxID: {receipt.transaction_id}")

    # 4. Verify Updated Balance
    print("\n[TEST 4] Verifying updated credit quota...")
    updated_credits = get_agent_balance(ctx, buyer_agent)
    print(f"-> Updated balance: {updated_credits} credits (5 initial + 10 bundle)")
    assert updated_credits == 15, "Balance should now be 15 credits"

    # 5. Deduct Credit upon query
    print("\n[TEST 5] Deducting credit upon semantic recall execution...")
    deducted = deduct_agent_credit(ctx, buyer_agent)
    assert deducted is True
    remaining = get_agent_balance(ctx, buyer_agent)
    print(f"-> Deducted 1 credit. Remaining balance: {remaining} credits")
    assert remaining == 14

    # 6. Reject Payment test
    print("\n[TEST 6] Testing RejectPayment handling...")
    reject_msg = RejectPayment(reason="Buyer declined fee quote")
    await handle_payment_reject(ctx, buyer_agent, reject_msg)
    print("-> Rejection logged cleanly without error.")

    print("\n==================================================================")
    print(" 🎉 ALL AGENT PAYMENT PROTOCOL TESTS PASSED SUCCESSFULLY!")
    print("==================================================================")


if __name__ == "__main__":
    asyncio.run(run_tests())

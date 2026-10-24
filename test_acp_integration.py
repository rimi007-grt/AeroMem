"""
AeroMem: ACP (Agent Chat Protocol) Integration Test
Validates that ASI:One chat messages correctly trigger semantic recall,
memory ingestion, and telemetry reporting.
"""

import asyncio
import sys

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from uagents_core.contrib.protocols.chat import (
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
)
from aeromem_chat_protocol import handle_chat_message
from aeromem_protocol import vector_engine


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
    user_sender = "agent1q_asi1_chat_client"

    print("==================================================================")
    print(" 🧪 TESTING AGENT CHAT PROTOCOL (ACP) FOR ASI:ONE INTEGRATION")
    print("==================================================================")

    # 1. Greeting
    print("\n[TEST 1] Sending Greeting / Start Session...")
    msg1 = ChatMessage(content=[TextContent(text="hello")])
    await handle_chat_message(ctx, user_sender, msg1)
    ack1 = ctx.sent_messages[-2][1]
    reply1 = ctx.sent_messages[-1][1]
    assert isinstance(ack1, ChatAcknowledgement)
    assert isinstance(reply1, ChatMessage)
    print("-> Ack verified:", ack1.acknowledged_msg_id == msg1.msg_id)
    print("-> Greeting response preview:\n", reply1.content[0].text[:120], "...\n")

    # 2. Ingest Memory via Chat
    print("[TEST 2] Committing new mitigation via Chat ('Remember: ...')...")
    msg2 = ChatMessage(
        content=[
            TextContent(
                text="Remember: Scaled Redis cluster replicas from 2 to 6 to absorb holiday traffic spike."
            )
        ]
    )
    await handle_chat_message(ctx, user_sender, msg2)
    reply2 = ctx.sent_messages[-1][1]
    print("-> Commit response:\n", reply2.content[0].text, "\n")
    assert "Episodic Memory Successfully Committed!" in reply2.content[0].text

    # 3. Recall Memory via Natural Language
    print("[TEST 3] Querying memory via natural language...")
    msg3 = ChatMessage(
        content=[
            TextContent(
                text="How to scale Redis cluster replicas for high traffic spikes?"
            )
        ]
    )
    await handle_chat_message(ctx, user_sender, msg3)
    reply3 = ctx.sent_messages[-1][1]
    print("-> Recall response:\n", reply3.content[0].text, "\n")
    assert "AeroMem Semantic Vector Recall" in reply3.content[0].text

    # 4. Telemetry
    print("[TEST 4] Requesting system telemetry ('stats')...")
    msg4 = ChatMessage(content=[TextContent(text="stats")])
    await handle_chat_message(ctx, user_sender, msg4)
    reply4 = ctx.sent_messages[-1][1]
    print("-> Stats response:\n", reply4.content[0].text, "\n")
    assert "Telemetry" in reply4.content[0].text

    print("==================================================================")
    print(" 🎉 ALL ACP WORKFLOW TESTS PASSED SUCCESSFULLY!")
    print("==================================================================")


if __name__ == "__main__":
    asyncio.run(run_tests())

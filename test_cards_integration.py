"""
AeroMem: ASI Interactive Cards Integration Test Suite
Validates the complete lifecycle of all ASI Interactive Cards in ASI:One:
1. Carousel Card (Playbook Catalog)
2. Detail Card (Incident Deep-Dive & Remediation Options)
3. Custom Form Card (Interactive Memory Contribution)
4. Review Card (Confirmation prior to indexing/remediation)
5. Custom Dashboard Card (Live Cluster Telemetry)
6. Action Handling (Direct-mention JSON payloads & real-time tool calls)
"""

import asyncio
import json
import sys

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    MetadataContent,
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


def extract_card_metadata(msg: ChatMessage) -> dict:
    """Extracts card metadata dict from a ChatMessage."""
    for item in msg.content:
        if isinstance(item, MetadataContent):
            return item.metadata
    return {}


async def run_tests():
    ctx = MockContext()
    user_sender = "agent1q_asi1_card_tester"

    print("==================================================================")
    print(" 🃏 TESTING ASI:ONE INTERACTIVE CARDS SUITE (AEROMEM)")
    print("==================================================================")

    # -----------------------------------------------------------------------
    # TEST 1: Carousel Card
    # -----------------------------------------------------------------------
    print("\n[TEST 1] Triggering Carousel Card ('playbooks')...")
    msg1 = ChatMessage(content=[TextContent(text="playbooks")])
    await handle_chat_message(ctx, user_sender, msg1)
    reply1 = ctx.sent_messages[-1][1]
    meta1 = extract_card_metadata(reply1)

    assert meta1.get("card_protocol_version") == "1", "card_protocol_version must be '1'"
    assert meta1.get("requires_card_interaction") == "true", "requires_card_interaction must be 'true'"
    assert meta1.get("card_kind") == "carousel", "card_kind must be 'carousel'"

    payload1 = json.loads(meta1.get("card_payload", "{}"))
    assert "items" in payload1 and len(payload1["items"]) >= 4, "Carousel must contain at least 4 items"
    print("-> Carousel verified successfully!")
    print(f"   Items returned: {len(payload1['items'])} | Title: {payload1['title']}")
    print(f"   Sample item: {payload1['items'][0]['title']} ({payload1['items'][0]['badges'][0]['label']})")

    # -----------------------------------------------------------------------
    # TEST 2: Detail Card
    # -----------------------------------------------------------------------
    print("\n[TEST 2] Simulating User selection on Carousel Item -> Detail Card...")
    # User clicks "Inspect Mitigation" on 'off_oom'
    select_payload = json.dumps({"action": "view_incident", "incident_key": "off_oom"})
    msg2 = ChatMessage(content=[TextContent(text=select_payload)])
    await handle_chat_message(ctx, user_sender, msg2)
    reply2 = ctx.sent_messages[-1][1]
    meta2 = extract_card_metadata(reply2)

    assert meta2.get("card_kind") == "detail", "card_kind must be 'detail'"
    payload2 = json.loads(meta2.get("card_payload", "{}"))
    assert "summary_rows" in payload2, "Detail card must have summary_rows"
    assert "primary_cta" in payload2, "Detail card must have primary_cta"
    print("-> Detail Card verified successfully!")
    print(f"   Title: {payload2['title']}")
    print(f"   Summary rows: {[r['label'] + '=' + r['value'] for r in payload2['summary_rows'][:3]]}")

    # -----------------------------------------------------------------------
    # TEST 3: Action Execution from Detail Card
    # -----------------------------------------------------------------------
    print("\n[TEST 3] Simulating User clicking 'Apply Mitigation' on Detail Card...")
    exec_payload = json.dumps({"action": "execute_remediation", "incident_id": "INC-8921-OOM"})
    msg3 = ChatMessage(content=[TextContent(text=exec_payload)])
    await handle_chat_message(ctx, user_sender, msg3)
    reply3 = ctx.sent_messages[-1][1]
    text3 = reply3.content[0].text
    assert "Autonomous Remediation Execution Triggered!" in text3
    assert "INC-8921-OOM" in text3
    print("-> Autonomous Remediation verified successfully!")
    print("   Output preview:\n", text3[:140], "...\n")

    # -----------------------------------------------------------------------
    # TEST 4: Custom Form Card
    # -----------------------------------------------------------------------
    print("[TEST 4] Triggering Interactive Contribution Form Card ('form')...")
    msg4 = ChatMessage(content=[TextContent(text="form")])
    await handle_chat_message(ctx, user_sender, msg4)
    reply4 = ctx.sent_messages[-1][1]
    meta4 = extract_card_metadata(reply4)

    assert meta4.get("card_kind") == "custom", "card_kind must be 'custom' element-tree"
    payload4 = json.loads(meta4.get("card_payload", "{}"))
    assert "root" in payload4, "Form card must contain 'root'"
    assert payload4["root"]["type"] == "section"
    print("-> Form Card verified successfully!")
    print(f"   Root Section: '{payload4['root']['title']}'")
    print(f"   Fields: {[c['name'] for c in payload4['root']['children'] if c.get('type') == 'input']}")

    # -----------------------------------------------------------------------
    # TEST 5: Form Submission -> Review Card
    # -----------------------------------------------------------------------
    print("\n[TEST 5] Submitting Form -> Review Card...")
    form_submit = json.dumps({
        "action": "submit_memory_form",
        "task_name": "Kafka Consumer Lag Spike in order-stream",
        "memory_type": "EXECUTION",
        "mitigation_details": "Scaled consumer pods from 3 to 9 and increased max.poll.records to 500.",
        "severity": "P2-HIGH",
    })
    msg5 = ChatMessage(content=[TextContent(text=form_submit)])
    await handle_chat_message(ctx, user_sender, msg5)
    reply5 = ctx.sent_messages[-1][1]
    meta5 = extract_card_metadata(reply5)

    assert meta5.get("card_kind") == "review", "card_kind must be 'review'"
    payload5 = json.loads(meta5.get("card_payload", "{}"))
    assert "approve_cta" in payload5 and "reject_cta" in payload5
    print("-> Review Card verified successfully!")
    print(f"   Review Title: '{payload5['title']}'")
    print(f"   Approve CTA: '{payload5['approve_cta']['label']}'")

    # -----------------------------------------------------------------------
    # TEST 6: Review Card Approval -> Persistence
    # -----------------------------------------------------------------------
    print("\n[TEST 6] Approving Review Card -> Ingest into ChromaDB + ctx.storage...")
    approve_submit = json.dumps(payload5["approve_cta"]["selection"])
    msg6 = ChatMessage(content=[TextContent(text=approve_submit)])
    await handle_chat_message(ctx, user_sender, msg6)
    reply6 = ctx.sent_messages[-1][1]
    text6 = reply6.content[0].text
    assert "Episodic Memory Successfully Committed via Review Card!" in text6
    print("-> Review approval and ingestion verified!")

    # Verify query retrieves the newly added memory
    print("\n[TEST 7] Semantic Vector Recall of Newly Ingested Memory...")
    msg7 = ChatMessage(content=[TextContent(text="How to fix Kafka consumer lag in order stream?")])
    await handle_chat_message(ctx, user_sender, msg7)
    reply7 = ctx.sent_messages[-1][1]
    text7 = reply7.content[0].text
    assert "Kafka Consumer Lag Spike in order-stream" in text7
    print("-> Semantic Recall retrieved the newly approved memory!")

    # -----------------------------------------------------------------------
    # TEST 8: Live Real-Time SSL Tool Execution
    # -----------------------------------------------------------------------
    print("\n[TEST 8] Testing Real-Time SSL/TLS Handshake Tool ('check ssl google.com')...")
    msg8 = ChatMessage(content=[TextContent(text="check ssl google.com")])
    await handle_chat_message(ctx, user_sender, msg8)
    reply8 = ctx.sent_messages[-1][1]
    text8 = reply8.content[0].text
    assert "Live SSL/TLS Certificate Analysis Tool" in text8
    assert "Days Remaining:" in text8
    print("-> Real-Time SSL tool executed successfully against live domain!")
    print("   Output preview:\n", text8[:140], "...\n")

    # -----------------------------------------------------------------------
    # TEST 9: Dashboard Card
    # -----------------------------------------------------------------------
    print("[TEST 9] Requesting Live Telemetry Dashboard Card ('dashboard')...")
    msg9 = ChatMessage(content=[TextContent(text="dashboard")])
    await handle_chat_message(ctx, user_sender, msg9)
    reply9 = ctx.sent_messages[-1][1]
    meta9 = extract_card_metadata(reply9)
    assert meta9.get("card_kind") == "custom"
    print("-> Dashboard Card verified successfully!")

    print("==================================================================")
    print(" 🌟 ALL ASI:ONE INTERACTIVE CARDS & WORKFLOW TESTS PASSED!")
    print("==================================================================")


if __name__ == "__main__":
    asyncio.run(run_tests())

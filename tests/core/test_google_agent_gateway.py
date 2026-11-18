# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_google_agent_gateway.py"
# purpose: "Unit tests for Universal Google Cloud Vertex AI Terminal Agent Gateway."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import json
from scripts.system.google_agent_gateway import (
    GoogleAuthManager,
    GeminiPayloadTranslator,
)


def test_auth_manager_retrieves_identities():
    proj = GoogleAuthManager.get_active_project()
    acc = GoogleAuthManager.get_active_account()
    assert isinstance(proj, str) and len(proj) > 0
    assert "@" in acc or len(acc) > 0


def test_openai_to_gemini_translation():
    openai_payload = {
        "model": "gemini-3.8-flash",
        "messages": [
            {"role": "system", "content": "You are a concise builder."},
            {"role": "user", "content": "Create a healthcheck endpoint."},
            {"role": "assistant", "content": "Done."},
            {"role": "user", "content": "Now add tests."}
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "run_test",
                    "description": "Runs tests",
                    "parameters": {"type": "object", "properties": {"suite": {"type": "string"}}}
                }
            }
        ]
    }
    gemini_body = GeminiPayloadTranslator.openai_to_gemini(openai_payload)
    assert "contents" in gemini_body
    assert len(gemini_body["contents"]) == 3
    assert gemini_body["contents"][0]["role"] == "user"
    assert "systemInstruction" in gemini_body
    assert gemini_body["systemInstruction"]["parts"][0]["text"] == "You are a concise builder."
    assert "tools" in gemini_body
    assert len(gemini_body["tools"][0]["functionDeclarations"]) == 1
    assert gemini_body["tools"][0]["functionDeclarations"][0]["name"] == "run_test"


def test_gemini_to_openai_translation():
    gemini_resp = {
        "candidates": [
            {
                "content": {
                    "role": "model",
                    "parts": [{"text": "All tests passed with exit code 0."}]
                },
                "finishReason": "STOP"
            }
        ]
    }
    openai_resp = GeminiPayloadTranslator.gemini_to_openai(gemini_resp, model="gemini-3.8-flash")
    assert openai_resp["object"] == "chat.completion"
    assert openai_resp["model"] == "gemini-3.8-flash"
    assert len(openai_resp["choices"]) == 1
    assert openai_resp["choices"][0]["message"]["content"] == "All tests passed with exit code 0."
    assert openai_resp["choices"][0]["finish_reason"] == "stop"


def test_gemini_to_openai_tool_calls_translation():
    gemini_resp = {
        "candidates": [
            {
                "content": {
                    "role": "model",
                    "parts": [
                        {
                            "functionCall": {
                                "name": "run_test",
                                "args": {"suite": "core"}
                            }
                        }
                    ]
                },
                "finishReason": "STOP"
            }
        ]
    }
    openai_resp = GeminiPayloadTranslator.gemini_to_openai(gemini_resp, model="gemini-3.8-flash")
    msg = openai_resp["choices"][0]["message"]
    assert "tool_calls" in msg
    assert len(msg["tool_calls"]) == 1
    assert msg["tool_calls"][0]["function"]["name"] == "run_test"
    args = json.loads(msg["tool_calls"][0]["function"]["arguments"])
    assert args["suite"] == "core"

"""Approach C1: LLM-powered test case refinement.

Reads the structured JSON from Approach A and enhances it with LLM analysis:
- Classify each test as auto/partial/manual
- Attempt section assignment for uncategorized test cases
- Normalize field inconsistencies across test cases

Works with any OpenAI-compatible API (OpenAI, Ollama, vLLM, etc.).
Sets API key from env var ANMS_LLM_API_KEY (defaults to openai).
Base URL from ANMS_LLM_BASE_URL (defaults to https://api.openai.com/v1).
Model from ANMS_LLM_MODEL (defaults to gpt-4o).
"""
import json
import os
import sys
import time
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any

INPUT_PATH = sys.argv[1] if len(sys.argv) > 1 else "../output/anms_test_spec.json"
OUTPUT_PATH = sys.argv[2] if len(sys.argv) > 2 else "../output/test_cases_refined.json"
MAX_WORKERS = int(os.environ.get("ANMS_LLM_WORKERS", "4"))
REQUEST_DELAY = float(os.environ.get("ANMS_LLM_DELAY", "0.5"))

API_KEY = os.environ.get("ANMS_LLM_API_KEY", "")
API_URL = os.environ.get("ANMS_LLM_BASE_URL", "https://api.openai.com/v1")
MODEL = os.environ.get("ANMS_LLM_MODEL", "gpt-4o")

# Section definitions to help the LLM
SECTION_DEFINITIONS = """
Chapter 2 - Functional Test Cases:
  2.1 Default Applications (DAP)
  2.2 Agents (AGT)
  2.3 Transcoding (TRC)
  2.4 Build (BLD)
  2.5 Application Data Model (ADM)
  2.6 System Administration (SYS)

Chapter 3 - Exploratory Test Cases:
  3.1 Default Applications (DAP)
  3.2 Agents (AGT)
  3.3 Messaging [OBSOLETE]
  3.4 Build (BLD)
  3.5 Application Data Module (ADM)
  3.6 System Administration (SYS)

Chapter 4 - Special Test Cases
Chapter 5 - Operational Test Cases
Chapter 6 - Regression Test Suite
"""

CLASSIFY_PROMPT = f"""You are a test engineer analyzing ANMS test cases from a specification document.

{SECTION_DEFINITIONS}

For each test case below, classify it and return JSON.

Test ID: {test_id}
Test Title: {test_title}
Type: {test_type}
Purpose: {purpose}
Preconditions: {preconditions}
Test Steps (first 5): {test_steps_str}

Classify it:
1. automation_type: "scriptable" | "playwright" | "manual" | "n_a"
   - "scriptable": HTTP/API tests, SQL queries, CLI commands, container checks
   - "playwright": GUI interaction tests (click buttons, select menus, fill forms)
   - "manual": Exploratory, subjective, requires human judgment
   - "n_a": Not actually a test case

2. difficulty: "low" | "medium" | "high"
   - low: < 10 steps, standard assertions
   - medium: 10-30 steps, some complexity
   - high: > 30 steps, complex preconditions, multiple sub-tests

3. relevant_section: section_id string or null
   Match against the section list above. Look for keywords in steps.
   If the test case text mentions specific section keywords (ADM, Agents, Build, etc.), use that.

4. test_framework_hints: list of strings
   e.g., ["pytest-httpx", "pytest-playwright", "subprocess", "sqlalchemy", "podman"]

5. notes: brief explanation of classification

Return ONLY valid JSON, no markdown, no extra text.
"""


def classify_test_case(test_id, test_title, test_type, purpose, preconditions,
                       test_steps: List[str], sections: List[Dict]) -> Dict[str, Any]:
    """Send a single test case to the LLM for classification."""
    steps_str = "; ".join(test_steps[:8]) if test_steps else "none"

    prompt = CLASSIFY_PROMPT.format(
        test_id=test_id,
        test_title=test_title,
        test_type=test_type,
        purpose=purpose or "Not specified",
        preconditions=preconditions or "None stated",
        test_steps_str=steps_str,
    )

    try:
        resp = _llm_call(prompt, max_tokens=500)
        return _parse_llm_response(resp)
    except Exception as e:
        return {"error": str(e), "automation_type": "unknown", "difficulty": "unknown",
                "relevant_section": None, "test_framework_hints": [], "notes": str(e)}


def _llm_call(prompt: str, max_tokens: int = 500) -> str:
    """Call OpenAI-compatible API."""
    import httpx
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a precise test analyst. Always return valid JSON."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.1,
    }
    resp = httpx.post(f"{API_URL}/chat/completions", headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def _parse_llm_response(text: str) -> Dict[str, Any]:
    """Extract JSON from LLM response, handling markdown wrapping."""
    text = text.strip()
    # Remove markdown code blocks if present
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()
    return json.loads(text)


def main():
    if not API_KEY:
        print("ERROR: Set ANMS_LLM_API_KEY environment variable")
        print("Usage: ANMS_LLM_API_KEY=sk-xxx python3 extract_test_cases.py [input] [output]")
        sys.exit(1)

    print(f"Reading: {INPUT_PATH}")
    data = json.load(open(INPUT_PATH))
    test_cases = data["test_cases"]
    sections = data["sections"]

    uncategorized = [tc for tc in test_cases if not tc["section_id"]]
    print(f"Total test cases: {len(test_cases)}")
    print(f"  Uncategorized: {len(uncategorized)}")
    print(f"  To classify: {len(test_cases)}")
    print(f"  API: {MODEL} @ {API_URL}")

    # Phase 1: Classify uncategorized test cases (helps determine section)
    if uncategorized:
        print(f"\nPhase 1: Classifying {len(uncategorized)} uncategorized test cases...")
        for i, tc in enumerate(uncategorized):
            print(f"  [{i+1}/{len(uncategorized)}] {tc['id']} - {tc['title']}")
            result = classify_test_case(
                tc["id"], tc["title"], tc["type"],
                tc.get("purpose", ""), tc.get("preconditions", ""),
                tc.get("test_steps", []), sections,
            )
            if not result.get("error") and result.get("relevant_section"):
                section_id = result["relevant_section"]
                section_path = ""
                for s in sections:
                    if s["id"] == section_id:
                        section_path = f"{section_id} {s['title']}"
                        break
                tc["section_id"] = section_id
                tc["section_path"] = section_path
                print(f"    -> Assigned to {section_path}")

            if i < len(uncategorized) - 1:
                time.sleep(REQUEST_DELAY)

    # Phase 2: Classify all test cases
    print(f"\nPhase 2: Classifying all {len(test_cases)} test cases...")
    for i, tc in enumerate(test_cases):
        print(f"  [{i+1}/{len(test_cases)}] {tc['id']}")
        tc["classification"] = classify_test_case(
            tc["id"], tc["title"], tc["type"],
            tc.get("purpose", ""), tc.get("preconditions", ""),
            tc.get("test_steps", []), sections,
        )
        c = tc["classification"]
        print(f"    -> {c.get('automation_type', '?')} / {c.get('difficulty', '?')} / {c.get('relevant_section', '?')}")
        if i < len(test_cases) - 1:
            time.sleep(REQUEST_DELAY)

    # Compute summary stats
    auto_counts = {}
    diff_counts = {}
    for tc in test_cases:
        c = tc.get("classification", {})
        at = c.get("automation_type", "unknown")
        auto_counts[at] = auto_counts.get(at, 0) + 1
        d = c.get("difficulty", "unknown")
        diff_counts[d] = diff_counts.get(d, 0) + 1

    print(f"\nAutomation type distribution: {auto_counts}")
    print(f"Difficulty distribution: {diff_counts}")

    # Write output
    out_dir = os.path.dirname(os.path.abspath(OUTPUT_PATH))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\nWrote refined output to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

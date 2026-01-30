"""
Agent Chain Compliance Verification Demo

Demonstrates how Company A verifies compliance across a multi-agent chain
before sharing employee personal data.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

# Load policy and mock manifests
DEMO_DIR = Path(__file__).parent

def load_json(path):
    with open(path) as f:
        return json.load(f)

def check_compliance(manifest: dict, policy: dict) -> dict:
    """Check if an agent's manifest satisfies a policy."""
    
    results = {"pass": True, "reasons": [], "warnings": []}
    now = datetime.now(timezone.utc)
    
    if not manifest:
        return {"pass": False, "reasons": ["No manifest found"], "warnings": []}
    
    attestations = manifest.get("compliance_attestations", {})
    jurisdictions = attestations.get("jurisdictions", [])
    model_info = manifest.get("model_provider_compliance", {})
    sub_agents = manifest.get("sub_agent_compliance", {})
    codebase = manifest.get("codebase_verification", {})
    
    # ─────────────────────────────────────────────────────────
    # JURISDICTION CHECKS
    # ─────────────────────────────────────────────────────────
    
    required = policy.get("regulatory_requirements", {}).get("required_jurisdictions", [])
    accepted = policy.get("regulatory_requirements", {}).get("accepted_jurisdictions", [])
    blocked = policy.get("regulatory_requirements", {}).get("blocked_jurisdictions", [])
    
    declared_jurisdictions = [j.get("jurisdiction") for j in jurisdictions]
    
    # Check required jurisdictions are present
    for req in required:
        if req not in declared_jurisdictions:
            results["pass"] = False
            results["reasons"].append(f"Required jurisdiction missing: {req}")
    
    # Check for blocked jurisdictions
    for j in declared_jurisdictions:
        if j in blocked:
            results["pass"] = False
            results["reasons"].append(f"Blocked jurisdiction: {j}")
    
    # Check attestation freshness
    max_age = policy.get("regulatory_requirements", {}).get("max_attestation_age_days", 365)
    for j in jurisdictions:
        if j.get("attestation_date"):
            att_date = datetime.fromisoformat(j["attestation_date"].replace("Z", "+00:00"))
            age_days = (now - att_date).days
            if age_days > max_age:
                results["pass"] = False
                results["reasons"].append(f"Attestation too old for {j['jurisdiction']}: {age_days} days")
    
    # ─────────────────────────────────────────────────────────
    # MODEL PROVIDER CHECKS
    # ─────────────────────────────────────────────────────────
    
    model_reqs = policy.get("model_provider_requirements", {})
    
    if model_reqs.get("require_provider_disclosed"):
        if not model_info.get("provider_name"):
            results["pass"] = False
            results["reasons"].append("Model provider not disclosed")
    
    if model_reqs.get("require_gpai_compliance"):
        if not model_info.get("gpai_compliant"):
            results["pass"] = False
            results["reasons"].append("Model not GPAI compliant")
    
    blocked_providers = model_reqs.get("blocked_providers", [])
    if model_info.get("provider_name") in blocked_providers:
        results["pass"] = False
        results["reasons"].append(f"Blocked model provider: {model_info['provider_name']}")
    
    # ─────────────────────────────────────────────────────────
    # SUB-AGENT CHECKS
    # ─────────────────────────────────────────────────────────
    
    sub_reqs = policy.get("sub_agent_requirements", {})
    
    if sub_reqs.get("require_sub_agent_disclosure"):
        if sub_agents.get("uses_sub_agents") and not sub_agents.get("declared_sub_agents"):
            results["pass"] = False
            results["reasons"].append("Sub-agents used but not declared")
    
    if sub_agents.get("declared_sub_agents"):
        for sub in sub_agents["declared_sub_agents"]:
            if not sub.get("compliance_verified"):
                results["warnings"].append(f"Sub-agent {sub.get('agent_id')} compliance not verified")
    
    # ─────────────────────────────────────────────────────────
    # CODEBASE HASH CHECKS
    # ─────────────────────────────────────────────────────────
    
    if policy.get("regulatory_requirements", {}).get("require_codebase_hash"):
        if not codebase.get("current_hash"):
            results["pass"] = False
            results["reasons"].append("Codebase hash not provided")
    
    if policy.get("regulatory_requirements", {}).get("require_hash_match"):
        current = codebase.get("current_hash")
        attested = codebase.get("hash_at_attestation")
        if current and attested and current != attested:
            results["pass"] = False
            results["reasons"].append("Codebase hash mismatch - code changed since attestation")
    
    return results


def print_result(agent_name: str, result: dict):
    """Pretty print verification result."""
    status = "✅ PASS" if result["pass"] else "❌ FAIL"
    print(f"\n{'='*60}")
    print(f"Agent: {agent_name}")
    print(f"Status: {status}")
    
    if result["reasons"]:
        print("\nReasons:")
        for r in result["reasons"]:
            print(f"  • {r}")
    
    if result["warnings"]:
        print("\nWarnings:")
        for w in result["warnings"]:
            print(f"  ⚠ {w}")
    print("="*60)


def main():
    print("\n" + "="*60)
    print("AGENT CHAIN COMPLIANCE VERIFICATION DEMO")
    print("="*60)
    print("\nScenario: Company A employee wants to book travel")
    print("Chain: Agent A → Agent B (Travel) → Agent C (Airline)")
    print("\nCompany A policy requires: EU compliance, GPAI model, sub-agent disclosure")
    
    # Load policy
    policy = load_json(DEMO_DIR / "company_a_policy.json")
    
    # Load mock agent manifests
    agent_b = load_json(DEMO_DIR / "mock_agents" / "agent_b_travel.json")
    agent_c = load_json(DEMO_DIR / "mock_agents" / "agent_c_airline.json")
    agent_d = load_json(DEMO_DIR / "mock_agents" / "agent_d_sketchy.json")
    
    print("\n" + "-"*60)
    print("STEP 1: Verify Agent B (Travel Agency)")
    print("-"*60)
    result_b = check_compliance(agent_b, policy)
    print_result("Agent B - TravelBot", result_b)
    
    if result_b["pass"]:
        print("\n" + "-"*60)
        print("STEP 2: Verify Agent B's sub-agent (Agent C - Airline)")
        print("-"*60)
        result_c = check_compliance(agent_c, policy)
        print_result("Agent C - AirlineBot", result_c)
    
    print("\n" + "-"*60)
    print("STEP 3: Attempt to verify non-compliant agent (Agent D)")
    print("-"*60)
    result_d = check_compliance(agent_d, policy)
    print_result("Agent D - SketchyBot", result_d)
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("\nSummary:")
    print(f"  Agent B (Travel):  {'✅ Allowed' if result_b['pass'] else '❌ Blocked'}")
    print(f"  Agent C (Airline): {'✅ Allowed' if result_c['pass'] else '❌ Blocked'}")
    print(f"  Agent D (Sketchy): {'✅ Allowed' if result_d['pass'] else '❌ Blocked'}")
    print()


if __name__ == "__main__":
    main()

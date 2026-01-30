# Agent Chain Compliance Verification Demo

This demo shows how a business (Company A) can verify compliance across a multi-agent chain before sharing personal data.

## Scenario

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Company A  │───▶│  Company B  │───▶│  Company C  │───▶│  Company D  │
│  (Employee  │    │  (Travel    │    │  (Airline)  │    │  (Customer  │
│   HR Agent) │    │   Agency)   │    │             │    │   Support)  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
     Agent A           Agent B           Agent C           Agent D

Employee asks Agent A to book travel
  → Agent A contacts Agent B (travel agency)
    → Agent B contacts Agent C (airline booking)
      → Agent C may route to Agent D (customer interaction)
```

## The Problem

- Employee's personal data (name, DOB, passport) flows through the chain
- Each company may be in a different jurisdiction
- Each agent may use a different LLM provider
- Company A needs to verify the ENTIRE chain is compliant

## How Agent Passport Solves This

### Step 1: Agent A checks Agent B before sharing data

```python
# Agent A fetches Agent B's compliance manifest
manifest_b = fetch("https://travel-agency.com/.well-known/compliance.json")

# Agent A applies its company policy
result = check_compliance(manifest_b, company_a_policy)

if not result["pass"]:
    return f"Cannot proceed: {result['reasons']}"
```

### Step 2: Agent A also checks Agent B's sub-agents

```python
# Agent B declares its sub-agents in its manifest
sub_agents = manifest_b["sub_agent_compliance"]["declared_sub_agents"]

for sub in sub_agents:
    sub_manifest = fetch(sub["compliance_url"])
    result = check_compliance(sub_manifest, company_a_policy)
    
    if not result["pass"]:
        return f"Sub-agent {sub['agent_id']} not compliant"
```

### Step 3: Recursive verification (optional)

For high-security use cases, Agent A can recursively verify the entire chain down to Agent D.

## Running the Demo

```bash
python verify_chain.py
```

## Files

- `verify_chain.py` - Main verification logic
- `company_a_policy.json` - Sample company compliance policy
- `mock_agents/` - Sample agent manifests for the chain

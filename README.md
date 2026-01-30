# CBAAC - Cross-Border Agentic AI Compliance

**Embedding Regulatory and Cultural Compliance into Agentic Communication**

A protocol for AI agents to verify compliance with regulatory requirements (GDPR, EU AI Act, Japan APPI/METI, Korea AI Basic Act) and cultural/ethical standards across multi-agent chains.

## The Problem

When Agent A calls Agent B, which calls Agent C: how does the business using Agent A verify that the entire chain is:
1. Compliant with data privacy and AI regulations in relevant jurisdictions?
2. Aligned with company policies on cultural competency and ethical behavior?

Existing frameworks like NANDA include a `jurisdiction` field but lack:
- Structured compliance attestation
- Links to detailed self-certification
- Nested agent compliance verification
- Cultural/ethical benchmarks

## Our Proposal

Proposing an extension to NANDA AgentFacts with:
- `compliance_attestations`: links to signed self-certification questionnaires
- `sub_agent_compliance`: declared compliance of downstream agents
- `model_provider_compliance`: GPAI/frontier model attestation
- `cultural_benchmarks`: optional ethical alignment certifications

## Repository Structure

```
schema/           # JSON schema extending NANDA AgentFacts
questionnaires/   # Self-certification templates (EU, Japan, Korea, Cultural)
demo/             # Agent chain verification example
docs/             # Full paper
```

## Quick Start

See `demo/` for an example of Company A verifying compliance across a travel booking chain (Agent A → B → C → D).

## Authors

- Matt Pagett
- Tomoko Mitsuoka
- With Apart Research

## References

- [Project NANDA](https://projectnanda.org)
- [EU AI Act / GPAI Obligations](https://digital-strategy.ec.europa.eu/en/faqs/general-purpose-ai-models-ai-act-questions-answers)
- [Japan METI AI Guidelines](https://www.meti.go.jp/policy/mono_info_service/connected_industries/sharing_and_utilization/20250218003-ar.pdf)
- [Korea AI Basic Act](https://aibasicact.kr/)

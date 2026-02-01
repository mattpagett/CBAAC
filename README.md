# CBAAC - Cross-Border Agentic AI Compliance

**Embedding Regulatory and Cultural Risk Compliance into Agentic Communication**

A protocol for AI agents to verify compliance with regulatory requirements (GDPR, EU AI Act, Japan APPI/METI, Korea AI Basic Act), security certifications (ISO 42001, NIST AI RMF, OWASP), and cultural/ethical standards across multi-agent chains.

**Demo:** https://cross-border-agentic-compliance.solve.it.com/  
**Paper:** [Hackathon Submission](https://github.com/mattpagett/CBAAC/blob/main/docs/Cross%20Border%20Agentic%20Compliance%20Matt%20Pagett%20Tomoko%20Mitsuoka%20Feb%201%202026%20Apart%20Hackathon.pdf)

## The Problem

When Agent A calls Agent B, which calls Agent C: how does the business using Agent A verify that the entire chain is:
1. Compliant with data privacy and AI regulations in relevant jurisdictions?
2. Meets security certification requirements (ISO 42001, NIST, OWASP)?
3. Aligned with company policies on cultural competency and behavioral safeguards?

Current approaches rely on costly third-party audits ($10,000+), external agreements, or trust — and do not scale to millions of agents spawning on demand.

**Our solution: Demand-side verification.** Agents automatically check compliance of other agents before sharing data. If Company A's policy requires EU compliance, and Agent B cannot provide attestation, the transaction is blocked — creating market incentive for compliance without requiring enforcement at every interaction.

## Schema Extension

We propose extending NANDA AgentFacts with **five** new top-level objects:

| Object | Purpose |
|--------|---------|
| `compliance_attestations` | Regulatory compliance by jurisdiction (EU, Japan, Korea) + cultural benchmarks + behavioral safeguards |
| `model_provider_compliance` | GPAI model info, provider, risk classification |
| `sub_agent_compliance` | Downstream agent declarations for chain verification |
| `codebase_verification` | Cryptographic hash binding attestations to code |
| `security_certifications` | ISO 42001, NIST AI RMF, OWASP Top 10, MLCommons AILuminate, Singapore AI Verify |

The `behavioral_safeguards` subobject within `compliance_attestations` is a novel contribution — enabling businesses to require attestation against manipulation risks (unconsented user profiling, emotional manipulation, excessive anthropomorphization) that regulatory frameworks do not address.

## Attestation Tiers

| Tier | Indicator | Description |
|------|-----------|-------------|
| 🟢 Third-party audited | `third_party_audit: true` | Independent auditor signed |
| 🟡 Auto-verified | `automated_verification: true` | Automated service verification |
| 🟠 Self-certified | `compliant: true` only | Questionnaire completed |
| 🔴 Unverified | No attestations | Blocked by default |

## Questionnaires

Over 120 questions across five domains:

| Domain | Questions | Coverage |
|--------|-----------|----------|
| EU | 45+ | GDPR, AI Act, GPAI, CE marking |
| Japan | 30+ | APPI, METI, data sovereignty |
| Korea | 35+ | AI Basic Act, PIPA, ISMS-P |
| Cultural/Ethical | 20+ | Behavioral safeguards, honorifics, inclusivity |
| Security | 25+ | ISO 42001, NIST, OWASP, MLCommons, AI Verify |

## Repository Structure

```
schema/                 # JSON schema extending NANDA AgentFacts
  compliance-extension.json
  examples/
questionnaires/         # Self-certification templates
  eu-gdpr-aiact.json
  japan-appi-meti.json
  korea-ai-basic-act.json
  cultural-ethical.json
  security-certifications.json
demo/                   # Interactive verification demo
docs/                   # Full paper
```

## Quick Start

```bash
cd demo
python app.py
```

Then visit http://localhost:8000 to see:
- Agent chain verification with compliance checking
- Self-certification questionnaire generator
- Example compliant and non-compliant agent manifests

## Authors

- **Matt Pagett** — Technical implementation, schema design, questionnaires
- **Tomoko Mitsuoka** — Conceptual framework, behavioral safeguards, cultural competency assessment

With **Apart Research** (Technical AI Governance Hackathon, January 2026)

## References

- [Project NANDA](https://projectnanda.org) — AgentFacts schema
- [EU AI Act / GPAI](https://digital-strategy.ec.europa.eu/en/faqs/general-purpose-ai-models-ai-act-questions-answers)
- [Japan METI AI Guidelines](https://www.meti.go.jp/policy/mono_info_service/connected_industries/sharing_and_utilization/20250218003-ar.pdf)
- [Korea AI Basic Act](https://aibasicact.kr/)
- [Mitsuoka (2026) — Beyond Technical Compliance](https://papers.ssrn.com/abstract=6093926)

## License

MIT

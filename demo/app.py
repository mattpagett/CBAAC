"""
Agent Passport - Compliance Chain Verification Demo
Run with: python app.py
"""

from fasthtml.common import *
import json
from pathlib import Path
from datetime import datetime, timezone

app, rt = fast_app(hdrs=[Style("""
    body { font-family: system-ui, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; background: #1a1a2e; color: #eee; }
    h1, h2, h3 { color: #fff; }
    .header { text-align: center; margin-bottom: 30px; }
    .header h1 { margin-bottom: 5px; color: #00d4ff; }
    .header .subtitle { color: #888; font-size: 14px; }
    .tabs { display: flex; gap: 5px; margin-bottom: 20px; border-bottom: 2px solid #333; }
    .tab-btn { padding: 12px 24px; background: #2a2a4a; color: #ccc; border: none; cursor: pointer; border-radius: 8px 8px 0 0; font-size: 14px; }
    .tab-btn:hover { background: #3a3a5a; }
    .tab-btn.active { background: #16213e; color: #00d4ff; border: 2px solid #333; border-bottom: 2px solid #16213e; margin-bottom: -2px; }
    .tab-content { display: none; }
    .tab-content.active { display: block; }
    .chain { display: flex; align-items: center; gap: 10px; margin: 30px 0; flex-wrap: wrap; }
    .agent-card { background: #16213e; border-radius: 8px; padding: 15px; min-width: 180px; box-shadow: 0 2px 8px rgba(0,0,0,0.3); cursor: pointer; transition: transform 0.2s; border: 2px solid #333; }
    .agent-card:hover { transform: scale(1.02); border-color: #00d4ff; }
    .agent-card.selected { border-color: #00d4ff; }
    .agent-card h3 { margin: 0 0 5px 0; font-size: 14px; color: #fff; }
    .agent-card .provider { color: #888; font-size: 12px; margin-bottom: 10px; }
    .arrow { font-size: 24px; color: #555; transition: color 0.3s; }
    .arrow.green { color: #75e6a0; }
    .arrow.red { color: #f5c2c7; }
    .summary-bar { display: flex; justify-content: space-between; align-items: center; background: #0f0f23; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; }
    .summary-stat { text-align: center; }
    .summary-stat .num { font-size: 28px; font-weight: bold; }
    .summary-stat .label { font-size: 12px; color: #888; }
    .summary-stat.pass .num { color: #75e6a0; }
    .summary-stat.fail .num { color: #f5c2c7; }
    .summary-stat.warn .num { color: #ffda6a; }
    .tooltip { position: relative; }
    .tooltip .tooltip-text { visibility: hidden; width: 200px; background: #333; color: #fff; text-align: left; padding: 8px; border-radius: 6px; position: absolute; z-index: 10; bottom: 105%; left: 50%; transform: translateX(-50%); font-size: 11px; box-shadow: 0 2px 8px rgba(0,0,0,0.5); }
    .tooltip:hover .tooltip-text { visibility: visible; }
    .agent-card.blocked { border-color: #842029; animation: pulse-red 1.5s infinite; }
    @keyframes pulse-red { 0%, 100% { box-shadow: 0 0 0 0 rgba(132, 32, 41, 0.4); } 50% { box-shadow: 0 0 15px 5px rgba(132, 32, 41, 0.2); } }
    .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    .badge.green { background: #0f5132; color: #75e6a0; }
    .badge.yellow { background: #664d03; color: #ffda6a; }
    .badge.orange { background: #984c0c; color: #feb272; }
    .badge.red { background: #842029; color: #f5c2c7; }
    .badge.warn { background: #664d03; color: #ffda6a; }
    .details { margin-top: 10px; font-size: 11px; }
    .details li { margin: 3px 0; color: #aaa; }
    .section { background: #16213e; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.3); }
    .policy-summary { font-size: 13px; color: #888; }
    .policy-summary code { background: #2a2a4a; padding: 2px 5px; border-radius: 3px; color: #00d4ff; }
    .chain-result { padding: 15px; border-radius: 8px; margin-top: 20px; }
    .chain-result.pass { background: #0f5132; color: #75e6a0; }
    .chain-result.fail { background: #842029; color: #f5c2c7; }
    .detail-panel { background: #0f0f23; border: 1px solid #333; border-radius: 8px; padding: 20px; margin-top: 20px; }
    .detail-panel h3 { margin-top: 0; }
    .detail-panel pre { background: #1a1a2e; padding: 10px; border-radius: 4px; overflow-x: auto; font-size: 12px; color: #aaa; }
    .detail-panel table { width: 100%; border-collapse: collapse; font-size: 13px; }
    input[type="checkbox"] { accent-color: #00d4ff; }
    button { background: #00d4ff; color: #000; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; }
    button:hover { background: #00b8e6; }
    fieldset { border: 1px solid #333; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
    legend { color: #00d4ff; font-weight: bold; }
    label { color: #ccc; }
    a { color: #00d4ff; }
    .detail-panel th, .detail-panel td { text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }
    .detail-panel th { background: #f0f0f0; }
""")])

DEMO_DIR = Path(__file__).parent

def load_json(path):
    with open(path) as f:
        return json.load(f)

def get_attestation_level(manifest: dict) -> tuple:
    """Determine attestation tier: green/yellow/orange/red"""
    attestations = manifest.get("compliance_attestations", {})
    jurisdictions = attestations.get("jurisdictions", [])
    
    has_third_party = any(j.get("third_party_audit") for j in jurisdictions)
    has_automated = any(j.get("automated_verification") for j in jurisdictions)
    has_self_cert = any(j.get("compliant") for j in jurisdictions)
    
    if has_third_party:
        return ("green", "🟢 Third-party audited")
    elif has_automated:
        return ("yellow", "🟡 Auto-verified")
    elif has_self_cert:
        return ("orange", "🟠 Self-certified")
    else:
        return ("red", "🔴 Unverified")

def check_agent(manifest: dict, policy: dict) -> dict:
    """Check if an agent's manifest satisfies policy."""
    level, level_text = get_attestation_level(manifest)
    results = {"pass": True, "reasons": [], "warnings": [], "level": level, "level_text": level_text}
    
    if not manifest.get("compliance_attestations", {}).get("jurisdictions"):
        results["pass"] = False
        results["reasons"].append("No jurisdiction compliance declared")
        return results
    
    # Check required jurisdictions
    required = set(policy.get("regulatory_requirements", {}).get("required_jurisdictions", []))
    declared = {j["jurisdiction"] for j in manifest.get("compliance_attestations", {}).get("jurisdictions", []) if j.get("compliant")}
    missing = required - declared
    if missing:
        results["pass"] = False
        results["reasons"].append(f"Missing required jurisdictions: {', '.join(missing)}")
    
    # Check model provider
    model = manifest.get("model_provider_compliance", {})
    if policy.get("model_provider_requirements", {}).get("require_gpai_compliance"):
        if not model.get("gpai_compliant"):
            results["pass"] = False
            results["reasons"].append("Model not GPAI compliant")
    
    # Check cultural benchmarks (warning only)
    if policy.get("cultural_requirements", {}).get("require_cultural_certification"):
        cultural = manifest.get("compliance_attestations", {}).get("cultural_benchmarks")
        if not cultural or not cultural.get("certified"):
            results["warnings"].append("No cultural certification")
    
    # Check sub-agents
    sub_agents = manifest.get("sub_agent_compliance", {}).get("declared_sub_agents", [])
    for sub in sub_agents:
        if not sub.get("compliance_verified"):
            results["warnings"].append(f"Sub-agent '{sub.get('agent_id', 'unknown')}' not verified")
    
    return results

def agent_card(name: str, manifest: dict, result: dict, agent_key: str):
    provider = manifest.get("provider", {}).get("name", "Unknown")
    jurisdictions = [j["jurisdiction"] for j in manifest.get("compliance_attestations", {}).get("jurisdictions", []) if j.get("compliant")]
    
    level = result.get("level", "red")
    level_text = result.get("level_text", "🔴 Unverified")
    badge_class = level if result["pass"] else "red"
    badge_text = level_text if result["pass"] else "🔴 BLOCKED"
    
    details = []
    for r in result["reasons"]:
        details.append(Li(f"❌ {r}"))
    for w in result["warnings"]:
        details.append(Li(f"⚠️ {w}"))
    if jurisdictions:
        details.append(Li(f"✓ {', '.join(jurisdictions)}"))
    
    # Build tooltip for blocked agents
    tooltip = None
    card_cls = "agent-card"
    if not result["pass"]:
        card_cls += " blocked tooltip"
        tooltip_reasons = " • ".join(result["reasons"]) if result["reasons"] else "Non-compliant"
        tooltip = Span(f"Why blocked: {tooltip_reasons}", cls="tooltip-text")
    
    return Div(
        tooltip,
        H3(name),
        Div(provider, cls="provider"),
        Span(badge_text, cls=f"badge {badge_class}"),
        Ul(*details, cls="details") if details else None,
        P("Click for details ↓", style="font-size:10px; color:#888; margin-top:8px;"),
        cls=card_cls,
        hx_get=f"/agent/{agent_key}",
        hx_target="#detail-panel",
        hx_swap="innerHTML"
    )

def colored_arrow(prev_passed: bool):
    """Return an arrow colored based on whether previous agent passed"""
    color = "green" if prev_passed else "red"
    return Span("→", cls=f"arrow {color}")

def summary_bar(results: dict):
    """Generate summary bar showing pass/fail/warn counts"""
    passed = sum(1 for r in results.values() if r["pass"])
    failed = sum(1 for r in results.values() if not r["pass"])
    warnings = sum(1 for r in results.values() if r.get("warnings"))
    total = len(results)
    
    return Div(
        Div(Div(str(passed), cls="num"), Div("Compliant", cls="label"), cls=f"summary-stat {'pass' if passed == total else ''}"),
        Div(Div(str(failed), cls="num"), Div("Blocked", cls="label"), cls=f"summary-stat {'fail' if failed > 0 else ''}"),
        Div(Div(str(warnings), cls="num"), Div("Warnings", cls="label"), cls=f"summary-stat {'warn' if warnings > 0 else ''}"),
        Div(Div(f"{passed}/{total}", cls="num"), Div("Chain Status", cls="label"), cls="summary-stat"),
        cls="summary-bar"
    )

@rt("/agent/{agent_key}")
def get(agent_key: str):
    """Return detailed compliance info for an agent."""
    files = {
        "agent_b": "agent_b_travel.json",
        "agent_c": "agent_c_airline.json", 
        "agent_d": "agent_d_sketchy.json",
    }
    if agent_key not in files:
        return Div("Agent not found")
    
    manifest = load_json(DEMO_DIR / "mock_agents" / files[agent_key])
    policy = load_json(DEMO_DIR / "company_a_policy.json")
    result = check_agent(manifest, policy)
    
    # Jurisdictions table
    jurisdictions = manifest.get("compliance_attestations", {}).get("jurisdictions", [])
    juris_rows = [Tr(Th("Jurisdiction"), Th("Compliant"), Th("Regulations"), Th("Questionnaire"))]
    for j in jurisdictions:
        juris_rows.append(Tr(
            Td(j.get("jurisdiction", "?")),
            Td("✓" if j.get("compliant") else "✗"),
            Td(", ".join(j.get("regulations", []))),
            Td(A("View", href=j.get("questionnaire_url", "#"), target="_blank") if j.get("questionnaire_url") else "—")
        ))
    if not jurisdictions:
        juris_rows.append(Tr(Td("No jurisdictions declared", colspan="4", style="color:#999;")))
    
    # Model provider
    model = manifest.get("model_provider_compliance", {})
    
    # Sub-agents
    sub_agents = manifest.get("sub_agent_compliance", {}).get("declared_sub_agents", [])
    
    return Div(
        H3(f"📋 {manifest.get('label', 'Unknown Agent')}"),
        P(manifest.get("description", "")),
        
        H4("Compliance Result"),
        Div(
            Span("✓ PASSED" if result["pass"] else "✗ FAILED", cls=f"badge {'pass' if result['pass'] else 'fail'}"),
            Ul(*[Li(f"❌ {r}") for r in result["reasons"]] + [Li(f"⚠️ {w}") for w in result["warnings"]]) if result["reasons"] or result["warnings"] else None
        ),
        
        H4("Jurisdiction Compliance"),
        Table(*juris_rows),
        
        H4("Model Provider"),
        Table(
            Tr(Th("Provider"), Td(model.get("provider_name", "Unknown"))),
            Tr(Th("Model"), Td(model.get("model_name", "Unknown"))),
            Tr(Th("GPAI Compliant"), Td("✓" if model.get("gpai_compliant") else "✗")),
        ),
        
        H4("Sub-Agents"),
        Ul(*[Li(f"{s.get('agent_id', '?')} — {'✓ verified' if s.get('compliance_verified') else '✗ not verified'}") for s in sub_agents]) if sub_agents else P("No sub-agents declared", style="color:#999;"),
        
        H4("Raw Manifest"),
        Pre(json.dumps(manifest, indent=2)),
        
        cls="detail-panel"
    )

@rt("/")
def get():
    # Load policy and manifests
    policy = load_json(DEMO_DIR / "company_a_policy.json")
    agents = {
        "Agent B (Travel)": load_json(DEMO_DIR / "mock_agents/agent_b_travel.json"),
        "Agent C (Airline)": load_json(DEMO_DIR / "mock_agents/agent_c_airline.json"),
        "Agent D (Sketchy)": load_json(DEMO_DIR / "mock_agents/agent_d_sketchy.json"),
    }
    
    # Check each agent
    results = {name: check_agent(m, policy) for name, m in agents.items()}
    
    # Overall chain result
    chain_pass = all(r["pass"] for r in results.values())
    
    # Build chain visualization with colored arrows
    agent_keys = ["agent_b", "agent_c", "agent_d"]
    agent_list = list(agents.items())
    chain_items = [
        Div(H3("Company A"), Div("(Your Agent)", cls="provider"), Span("ORIGIN", cls="badge green"), cls="agent-card"),
    ]
    prev_passed = True  # Origin always passes
    for i, ((name, manifest), key) in enumerate(zip(agent_list, agent_keys)):
        chain_items.append(colored_arrow(prev_passed))
        chain_items.append(agent_card(name, manifest, results[name], key))
        prev_passed = results[name]["pass"]
    
    return Title("CBAAC Demo"), Main(
        Div(
            H1("🛂 CBAAC"),
            P("Cross-Border Agentic AI Compliance", cls="subtitle"),
            cls="header"
        ),
        
        Div(
            Button("Chain Verification", cls="tab-btn active", onclick="showTab('chain')"),
            Button("Self-Certification", cls="tab-btn", onclick="showTab('questionnaire')"),
            cls="tabs"
        ),
        
        Script("""
            function showTab(tab) {
                document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
                document.getElementById('tab-' + tab).classList.add('active');
                event.target.classList.add('active');
            }
        """),
        
        # TAB 1: Chain Verification
        Div(id="tab-chain", cls="tab-content active")(
        
        Div(
            H2("Policy: ACME Corp"),
            Div(
                P(f"Required jurisdictions: ", Code(", ".join(policy["regulatory_requirements"]["required_jurisdictions"]))),
                P(f"Require GPAI compliance: ", Code(str(policy["model_provider_requirements"]["require_gpai_compliance"]))),
                P(f"Require cultural certification: ", Code(str(policy["cultural_requirements"]["require_cultural_certification"]))),
                cls="policy-summary"
            ),
            cls="section"
        ),
        
        Div(
            H2("Agent Chain"),
            summary_bar(results),
            Div(
                Div(*chain_items, cls="chain"),
                Div(
                    H3("Chain Result: " + ("✓ ALL COMPLIANT" if chain_pass else "✗ BLOCKED")),
                    P("Transaction can proceed." if chain_pass else "Transaction blocked due to non-compliant agents in chain."),
                    cls=f"chain-result {'pass' if chain_pass else 'fail'}"
                ),
                id="chain-results"
            ),
            cls="section"
        ),
        
        Div(
            H2("Agent Details"),
            P("Click an agent above to see full compliance details.", style="color:#888;"),
            id="detail-panel"
        ),
        
        Div(
            H2("Policy Editor"),
            P("Adjust your company's agent interaction policy:"),
            Form(
                Fieldset(
                    Legend("Regulatory Requirements"),
                    Label(Input(type="checkbox", name="require_gdpr", checked=True), " Require GDPR compliance"),
                    Br(),
                    Label(Input(type="checkbox", name="require_ai_act", checked=True), " Require AI Act compliance"),
                    Br(),
                    Label(Input(type="checkbox", name="require_gpai", checked=True), " Require GPAI model attestation"),
                    Br(),
                    Label(Input(type="checkbox", name="require_hash", checked=True), " Require codebase hash verification"),
                ),
                Fieldset(
                    Legend("Cultural Requirements"),
                    Label(Input(type="checkbox", name="require_cultural", checked=False), " Require cultural benchmarks"),
                ),
                Fieldset(
                    Legend("Sub-Agent Requirements"),
                    Label(Input(type="checkbox", name="require_subagent_compliance", checked=True), " Require sub-agent compliance chain"),
                ),
                Button("Apply Policy & Re-check", type="submit"),
                hx_post="/recheck",
                hx_target="#chain-results",
                hx_swap="innerHTML"
            ),
            cls="section", style="margin-top:30px;"
        ),
        ),  # End TAB 1
        
        # TAB 2: Self-Certification Questionnaire
        Div(id="tab-questionnaire", cls="tab-content")(
            H2("Self-Certification Questionnaire"),
            P("Generate a compliance manifest for your agent."),
            
            Div(
                H3("Step 1: Select Jurisdiction(s) & Certification Type"),
                Form(
                    Fieldset(
                        Legend("Jurisdictions"),
                        Label(Input(type="checkbox", name="jurisdiction", value="eu"), " 🇪🇺 European Union (GDPR + AI Act)"), Br(),
                        Label(Input(type="checkbox", name="jurisdiction", value="japan"), " 🇯🇵 Japan (APPI + METI)"), Br(),
                        Label(Input(type="checkbox", name="jurisdiction", value="korea"), " 🇰🇷 Korea (AI Basic Act + PIPA)"), Br(),
                        Label(Input(type="checkbox", name="jurisdiction", value="cultural"), " 🌍 Cultural/Ethical Standards"), Br(),
                    ),
                    Fieldset(
                        Legend("Certification Type"),
                        Label(Input(type="radio", name="cert_type", value="third_party"), " 🟢 Third-party auditor (highest trust)"), Br(),
                        Label(Input(type="radio", name="cert_type", value="auto_verified", checked=True), " 🟡 Auto-verified (automated compliance checks)"), Br(),
                        Label(Input(type="radio", name="cert_type", value="self_certified"), " 🟠 Self-certified (attestation only)"), Br(),
                        Label(Input(type="radio", name="cert_type", value="sign_to_code"), " 🔵 Sign-to-code (cryptographic proof)"), Br(),
                    ),
                    Br(),
                    Button("Load Questions →", type="submit"),
                    hx_post="/questionnaire/load", hx_target="#questionnaire-form"
                ),
                cls="section"
            ),
            
            Div(id="questionnaire-form", style="margin-top:20px;"),
        ),  # End TAB 2
    )

@rt("/recheck")
def post(require_gdpr: bool = False, require_ai_act: bool = False, require_gpai: bool = False, 
         require_hash: bool = False, require_cultural: bool = False, require_subagent_compliance: bool = False):
    """Re-check agents with updated policy"""
    
    # Build custom policy from form
    custom_policy = {
        "regulatory_requirements": {
            "required_jurisdictions": ["EU"] if require_gdpr else [],
            "require_gdpr_compliance": require_gdpr,
            "require_ai_act_compliance": require_ai_act,
            "require_codebase_hash": require_hash,
            "require_hash_match": require_hash,
        },
        "model_provider_requirements": {
            "require_gpai_compliance": require_gpai,
        },
        "cultural_requirements": {
            "require_cultural_certification": require_cultural,
        },
        "sub_agent_requirements": {
            "require_compliance_declaration": require_subagent_compliance,
        }
    }
    
    # Load agents
    agents = {
        "Agent B (Travel)": load_json(DEMO_DIR / "mock_agents/agent_b_travel.json"),
        "Agent C (Airline)": load_json(DEMO_DIR / "mock_agents/agent_c_airline.json"),
        "Agent D (Sketchy)": load_json(DEMO_DIR / "mock_agents/agent_d_sketchy.json"),
    }
    
    # Check each agent with new policy
    results = {name: check_agent(m, custom_policy) for name, m in agents.items()}
    chain_pass = all(r["pass"] for r in results.values())
    
    # Build chain visualization with colored arrows
    agent_keys = ["agent_b", "agent_c", "agent_d"]
    agent_list = list(agents.items())
    chain_items = [
        Div(H3("Company A"), Div("(Your Agent)", cls="provider"), Span("ORIGIN", cls="badge green"), cls="agent-card"),
    ]
    prev_passed = True
    for i, ((name, manifest), key) in enumerate(zip(agent_list, agent_keys)):
        chain_items.append(colored_arrow(prev_passed))
        chain_items.append(agent_card(name, manifest, results[name], key))
        prev_passed = results[name]["pass"]
    
    return Div(
        summary_bar(results),
        Div(*chain_items, cls="chain"),
        Div(
            H3("Chain Result: " + ("✓ ALL COMPLIANT" if chain_pass else "✗ BLOCKED")),
            P("Transaction can proceed." if chain_pass else "Transaction blocked due to non-compliant agents in chain."),
            cls=f"chain-result {'pass' if chain_pass else 'fail'}"
        )
    )

@rt("/questionnaire/load")
def post(jurisdiction: str = None, cert_type: str = "self_certified"):
    """Load questionnaire based on selected jurisdictions"""
    if not jurisdiction:
        return P("Please select at least one jurisdiction.", style="color:#ff6b6b;")
    
    if isinstance(jurisdiction, str):
        jurisdiction = [jurisdiction]
    
    questions = []
    
    # Map jurisdiction to questionnaire files
    juris_map = {
        "eu": ("eu-gdpr-aiact.json", "🇪🇺 EU GDPR & AI Act"),
        "japan": ("japan-appi-meti.json", "🇯🇵 Japan APPI & METI"),
        "korea": ("korea-ai-basic-act.json", "🇰🇷 Korea AI Basic Act"),
        "cultural": ("cultural-ethical.json", "🌍 Cultural & Ethical")
    }
    
    cert_labels = {
        "third_party": "🟢 Third-party auditor",
        "auto_verified": "🟡 Auto-verified",
        "self_certified": "🟠 Self-certified",
        "sign_to_code": "🔵 Sign-to-code"
    }
    
    form_fields = [
        Input(type="hidden", name="cert_type", value=cert_type),
        Input(type="hidden", name="jurisdictions_selected", value=",".join(jurisdiction)),
        P(f"Certification type: {cert_labels.get(cert_type, cert_type)}", style="color:#00d4ff; font-weight:bold;"),
    ]
    
    for j in jurisdiction:
        if j not in juris_map:
            continue
        filename, title = juris_map[j]
        q_path = DEMO_DIR.parent / "questionnaires" / filename
        if not q_path.exists():
            continue
        
        q_data = load_json(q_path)
        
        form_fields.append(H3(title, style="margin-top:20px; border-bottom:2px solid #ddd; padding-bottom:10px;"))
        
        for section_key, section in q_data.get("sections", {}).items():
            form_fields.append(H4(section.get("title", section_key), style="color:#555;"))
            
            for q in section.get("questions", []):
                q_id = q.get("id", "")
                q_text = q.get("question", "")
                q_type = q.get("type", "boolean")
                
                if q_type == "boolean":
                    form_fields.append(
                        Div(
                            Label(Input(type="checkbox", name=q_id), f" {q_text}"),
                            cls="question"
                        )
                    )
                elif q_type in ["select", "multi_select"]:
                    options = [Option(o, value=o) for o in q.get("options", [])]
                    form_fields.append(
                        Div(
                            Label(q_text),
                            Select(*options, name=q_id, multiple=(q_type == "multi_select"), style="width:100%; padding:8px;"),
                            cls="question"
                        )
                    )
                elif q_type in ["text", "url", "email"]:
                    form_fields.append(
                        Div(
                            Label(q_text),
                            Input(type=q_type, name=q_id, style="width:100%; padding:8px;"),
                            cls="question"
                        )
                    )
                elif q_type == "number":
                    form_fields.append(
                        Div(
                            Label(q_text),
                            Input(type="number", name=q_id, style="width:100px; padding:8px;"),
                            cls="question"
                        )
                    )
    
    form_fields.append(Br())
    form_fields.append(Button("Generate Manifest →", type="submit", style="background:#4CAF50; color:white; padding:12px 24px; border:none; border-radius:4px; cursor:pointer;"))
    
    return Div(
        H3("Step 2: Complete the Questionnaire"),
        Form(
            *form_fields,
            hx_post="/questionnaire/generate",
            hx_target="#questionnaire-form",
            hx_swap="innerHTML"
        ),
        cls="section"
    )

@rt("/questionnaire/generate")
def post(**kwargs):
    """Generate manifest from questionnaire answers"""
    
    cert_type = kwargs.get("cert_type", "self_certified")
    jurisdictions_selected = kwargs.get("jurisdictions_selected", "").split(",")
    
    # Certification flags based on type
    is_third_party = cert_type == "third_party"
    is_auto = cert_type == "auto_verified"
    is_self = cert_type == "self_certified"
    is_sign_to_code = cert_type == "sign_to_code"
    
    # Build jurisdictions from selected ones and their questionnaire responses
    jurisdictions = []
    
    if "eu" in jurisdictions_selected:
        eu_responses = {k: v for k, v in kwargs.items() if k.startswith(("gdpr_", "aiact_"))}
        jurisdictions.append({
            "jurisdiction": "EU",
            "compliant": True,
            "regulations": ["GDPR", "EU AI Act"],
            "questionnaire_url": "https://raw.githubusercontent.com/mattpagett/CBAAC/main/questionnaires/eu-gdpr-aiact.json",
            "third_party_audit": is_third_party,
            "automated_verification": is_auto,
            "self_certified": is_self,
            "sign_to_code": is_sign_to_code,
            "certification_date": datetime.now(timezone.utc).isoformat(),
            "responses": eu_responses
        })
    
    if "japan" in jurisdictions_selected:
        japan_responses = {k: v for k, v in kwargs.items() if k.startswith(("appi_", "meti_"))}
        jurisdictions.append({
            "jurisdiction": "Japan",
            "compliant": True,
            "regulations": ["APPI", "METI AI Guidelines"],
            "questionnaire_url": "https://raw.githubusercontent.com/mattpagett/CBAAC/main/questionnaires/japan-appi-meti.json",
            "third_party_audit": is_third_party,
            "automated_verification": is_auto,
            "self_certified": is_self,
            "sign_to_code": is_sign_to_code,
            "certification_date": datetime.now(timezone.utc).isoformat(),
            "responses": japan_responses
        })
    
    if "korea" in jurisdictions_selected:
        korea_responses = {k: v for k, v in kwargs.items() if k.startswith(("korea_", "pipa_"))}
        jurisdictions.append({
            "jurisdiction": "Korea",
            "compliant": True,
            "regulations": ["AI Basic Act", "PIPA"],
            "questionnaire_url": "https://raw.githubusercontent.com/mattpagett/CBAAC/main/questionnaires/korea-ai-basic-act.json",
            "third_party_audit": is_third_party,
            "automated_verification": is_auto,
            "self_certified": is_self,
            "sign_to_code": is_sign_to_code,
            "certification_date": datetime.now(timezone.utc).isoformat(),
            "responses": korea_responses
        })
    
    # Handle cultural if selected
    cultural_benchmarks = None
    if "cultural" in jurisdictions_selected:
        cultural_responses = {k: v for k, v in kwargs.items() if k.startswith("cultural_")}
        cultural_benchmarks = {
            "tested_cultures": kwargs.get("cultural_cultures", "").split(",") if kwargs.get("cultural_cultures") else [],
            "certified": len(cultural_responses) > 0,
            "certification_type": cert_type,
            "responses": cultural_responses
        }
    
    # Build NANDA-compatible manifest
    manifest = {
        "@context": [
            "https://spec.projectnanda.org/agentfacts/v1",
            "../schema/compliance-extension.json"
        ],
        
        "// STANDARD NANDA AGENTFACTS FIELDS": "===",
        "id": f"nanda:{kwargs.get('agent_id', 'your-agent-001')}",
        "agent_name": f"urn:agent:{kwargs.get('provider_name', 'yourcompany').lower().replace(' ','')}:{kwargs.get('agent_name', 'YourAgent')}",
        "label": kwargs.get("agent_name", "Your Agent"),
        "description": kwargs.get("agent_description", "AI agent description"),
        "version": kwargs.get("agent_version", "1.0.0"),
        
        "provider": {
            "name": kwargs.get("provider_name", "Your Company"),
            "url": kwargs.get("provider_url", "https://yourcompany.com"),
            "did": f"did:web:{kwargs.get('provider_url', 'yourcompany.com').replace('https://', '').replace('http://', '')}"
        },
        
        "// CBAAC COMPLIANCE EXTENSION": "===",
        "certification_type": cert_type,
        "compliance_attestations": {
            "jurisdictions": jurisdictions,
            "cultural_benchmarks": cultural_benchmarks
        },
        
        "model_provider_compliance": {
            "provider_name": kwargs.get("model_provider", ""),
            "model_name": kwargs.get("model_name", ""),
            "gpai_compliant": kwargs.get("gpai_compliant") == "on"
        },
        
        "codebase_verification": {
            "hash": kwargs.get("codebase_hash", "sha256:..."),
            "hash_algorithm": "sha256",
            "signed_by": f"did:web:{kwargs.get('provider_url', 'yourcompany.com').replace('https://', '').replace('http://', '')}",
            "signed_at": datetime.now(timezone.utc).isoformat(),
            "sign_to_code_enabled": is_sign_to_code
        } if is_sign_to_code or kwargs.get("codebase_hash") else None
    }
    
    # Clean up None values
    manifest = {k: v for k, v in manifest.items() if v is not None}
    
    manifest_json = json.dumps(manifest, indent=2)
    
    # Show side-by-side: Your manifest + where it fits in NANDA
    nanda_example = """{
  // Standard NANDA AgentFacts fields
  "id": "nanda:your-agent-001",
  "agent_name": "urn:agent:yourcompany:YourAgent",
  "label": "Your Agent",
  "provider": { ... },
  "endpoints": { ... },
  "capabilities": { ... },
  "skills": [ ... ],
  
  // 🆕 CBAAC Compliance Extension
  "compliance_attestations": {    ← YOUR COMPLIANCE DATA
    "jurisdictions": [ ... ],
    "cultural_benchmarks": { ... }
  },
  "model_provider_compliance": { ... },
  "codebase_verification": { ... }
}"""
    
    return Div(
        H3("✓ Manifest Generated"),
        
        Div(
            Div(
                H4("Your CBAAC Compliance Manifest"),
                P("Host at: ", Code("/.well-known/cbaac-compliance.json")),
                Pre(manifest_json, style="background:#0d1117; color:#c9d1d9; padding:15px; border-radius:8px; overflow-x:auto; font-size:12px; max-height:400px;"),
                style="flex:1; min-width:300px;"
            ),
            Div(
                H4("How it fits in NANDA AgentFacts"),
                P("Extension to the standard schema:"),
                Pre(nanda_example, style="background:#0d1117; color:#8b949e; padding:15px; border-radius:8px; overflow-x:auto; font-size:12px; max-height:400px;"),
                style="flex:1; min-width:300px;"
            ),
            style="display:flex; gap:20px; flex-wrap:wrap;"
        ),
        
        Div(
            Button("📋 Copy to Clipboard", onclick=f"navigator.clipboard.writeText({manifest_json!r}); this.innerText='✓ Copied!'", 
                   style="padding:10px 20px; margin-right:10px;"),
            Button("⬇️ Download JSON", onclick=f"downloadManifest({manifest_json!r})", 
                   style="padding:10px 20px;"),
            style="margin-top:15px;"
        ),
        
        Script("""
            function downloadManifest(json) {
                const blob = new Blob([json], {type: 'application/json'});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'cbaac-compliance.json';
                a.click();
            }
        """),
        cls="section"
    )

serve(port=8000)

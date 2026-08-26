#!/usr/bin/env python3
"""One-time builder for a SourcingBench cycle.

Encodes the editorial capability matrix (every criterion value cites the
published review it is drawn from), then emits the per-cycle data files:
criteria.json, capabilities.json, leaderboard.json, cycle.json (sha256
manifest) and per-tool history under data/tools/. The frozen scoring.mjs
in the cycle directory recomputes the same numbers from the same JSON —
`npm run verify` asserts they match.

Not part of the published verification path; kept for provenance.
"""

import hashlib
import json
import math
import os
import sys


def round1(x):
    """Round half up to 1 decimal, matching JS Math.round(x*10)/10."""
    return math.floor(x * 10 + 0.5) / 10

CYCLE = "August 2026"
CYCLE_DATE = "2026-08-26"
ROOT = os.path.join(os.path.dirname(__file__), "..")
CYCLE_DIR = os.path.join(ROOT, "data", "cycles", CYCLE)

ST = "https://sourcingtools.org"

CRITERIA = {
    "version": "2.0.0",
    "cycle": CYCLE,
    "scale": "Each criterion is scored 0\u201310 against the published rubric: 0 = absent, 5 = adequate for typical use, 10 = the strongest implementation observed in the category this cycle. Dimension score = mean of its criteria \u00d7 10 (0\u2013100). Composite = weighted sum of dimension scores.",
    "dimensions": [
        {
            "id": "matching",
            "name": "Candidate matching & screening",
            "weight": 0.25,
            "definition": "The core job of an AI recruiting tool: finding the right candidates for a role and evaluating them accurately against its requirements.",
            "criteria": [
                {"id": "criteria_evaluation", "name": "Structured criteria evaluation", "definition": "Evaluates against explicit role-specific criteria with per-candidate reasoning, beyond keyword/Boolean relevance."},
                {"id": "feedback_learning", "name": "Learning from feedback", "definition": "Adapts its matching per role from recruiter/hiring-manager feedback."},
                {"id": "hard_filters", "name": "Hard requirements", "definition": "Supports mandatory criteria that are never relaxed (certifications, clearances, locations)."},
                {"id": "trajectory_inference", "name": "Trajectory & context inference", "definition": "Reads career trajectory, company caliber, and inferred attributes rather than title/keyword matches."},
            ],
        },
        {
            "id": "autonomy",
            "name": "Workflow automation",
            "weight": 0.20,
            "definition": "How much of the recruiting workflow the tool runs on its own \u2014 search, screening, outreach, and scheduling \u2014 versus assisting a recruiter who drives each step.",
            "criteria": [
                {"id": "autonomous_search", "name": "Automated search", "definition": "Initiates and continuously runs candidate searches from a role brief without per-search recruiter operation."},
                {"id": "autonomous_screening", "name": "Automated screening", "definition": "Evaluates candidates against role criteria and produces decisions with reasoning, rather than only ranking results for manual review."},
                {"id": "autonomous_outreach", "name": "Automated outreach", "definition": "Composes and sends personalized outreach and follow-ups without per-message recruiter action."},
                {"id": "scheduling_automation", "name": "Scheduling automation", "definition": "Handles candidate replies through to a booked interview (Q&A, availability, calendar booking)."},
            ],
        },
        {
            "id": "engagement",
            "name": "Outreach & engagement",
            "weight": 0.20,
            "definition": "Ability to convert sourced profiles into responsive candidates.",
            "criteria": [
                {"id": "channels", "name": "Channel coverage", "definition": "Outreach channels available (email, LinkedIn, SMS/phone)."},
                {"id": "personalization", "name": "Personalization", "definition": "Per-candidate AI personalization grounded in the candidate's actual background."},
                {"id": "sequencing", "name": "Sequencing", "definition": "Multi-step sequences, scheduling windows, and testing."},
                {"id": "reply_handling", "name": "Reply handling", "definition": "Automated handling of candidate questions and replies."},
            ],
        },
        {
            "id": "coverage",
            "name": "Talent pool coverage & data",
            "weight": 0.20,
            "definition": "Breadth of candidate discovery and quality of contact data.",
            "criteria": [
                {"id": "source_breadth", "name": "Source breadth", "definition": "Discovery beyond a single network: open web, GitHub, publications, licensed partners."},
                {"id": "contact_finding", "name": "Contact finding", "definition": "Email/phone enrichment coverage and accuracy."},
            ],
        },
        {
            "id": "workflow",
            "name": "Integrations & reporting",
            "weight": 0.15,
            "definition": "Fit into the surrounding recruiting stack, and visibility into pipeline performance.",
            "criteria": [
                {"id": "ats_integrations", "name": "ATS integrations", "definition": "Breadth and depth of ATS/CRM sync."},
                {"id": "analytics", "name": "Analytics", "definition": "Funnel, outreach, and pipeline analytics."},
            ],
        },
    ],
}

# tool -> (name, website, criterion -> (value, note))
TOOLS = {
    "noon": {
        "name": "Noon",
        "website": "https://noon.ai",
        "scores": {
            "autonomous_search": (9, "Sources continuously from a role brief; keeps monitoring as new candidates enter the market"),
            "autonomous_screening": (9, "Per-candidate verdicts with reasoning against calibrated role criteria"),
            "autonomous_outreach": (9, "Multi-touch personalized sequences sent and followed up automatically"),
            "scheduling_automation": (8, "AI coordinator answers candidate questions and books interviews (calendar integration); newer than incumbent scheduling stacks"),
            "criteria_evaluation": (9, "Explicit role criteria with per-candidate reasoning and pass-rate reporting"),
            "feedback_learning": (9, "Calibration loop: recruiter grades early candidates, model adjusts per role; re-evaluates on criteria change"),
            "hard_filters": (9, "Non-negotiables: mandatory criteria that are never relaxed"),
            "trajectory_inference": (8, "Interprets career trajectory and company caliber; less attribute search than Findem"),
            "channels": (9, "Email, LinkedIn, and SMS sequences"),
            "personalization": (9, "AI-generated per-candidate intros grounded in profile; above category average in our review"),
            "sequencing": (7, "Multi-step sequences with editing; no A/B testing at hireEZ/Gem depth"),
            "reply_handling": (9, "Coordinator handles candidate Q&A through to booking"),
            "source_breadth": (8, "Web-wide sourcing beyond LinkedIn; smaller aggregated index than hireEZ/SeekOut"),
            "contact_finding": (8, "Built-in email enrichment and verification"),
            "ats_integrations": (8, "20+ ATS providers via unified sync layer; fewer native bi-directional integrations than hireEZ"),
            "analytics": (7, "Funnel and outbound performance metrics; lighter reporting than Gem"),
        },
    },
    "hireez": {
        "name": "hireEZ",
        "website": "https://hireez.com",
        "scores": {
            "autonomous_search": (7, "AI Sourcing mode surfaces new matches continuously; recruiter builds and owns searches"),
            "autonomous_screening": (7, "EZ Match ranks against the JD with strong relevance; recruiter reviews shortlists"),
            "autonomous_outreach": (8, "AI-drafted sequenced outreach runs after recruiter launch"),
            "scheduling_automation": (5, "Scheduling handoff to ATS/calendar tooling; no candidate-facing agent"),
            "criteria_evaluation": (8, "JD-driven requirement extraction and ranked matching"),
            "feedback_learning": (7, "Match tuning within a search; no per-role calibration loop"),
            "hard_filters": (9, "Deep Boolean and healthcare/technical filters"),
            "trajectory_inference": (7, "Ranking beyond keywords, though title/skill-centric"),
            "channels": (8, "Email sequences with phone data; no SMS/LinkedIn sending"),
            "personalization": (8, "AI-written outreach from profile + JD"),
            "sequencing": (9, "Mature sequences with A/B testing and team tracking"),
            "reply_handling": (6, "Reply detection and routing; replies handled by the recruiter"),
            "source_breadth": (10, "800M+ profiles aggregated from open web and licensed partners"),
            "contact_finding": (9, "Category-leading contact coverage; quality varies by region"),
            "ats_integrations": (9, "~30 bi-directional ATS integrations plus ATS Rediscovery"),
            "analytics": (9, "Full funnel, sequence, and team analytics"),
        },
    },
    "seekout": {
        "name": "SeekOut",
        "website": "https://seekout.com",
        "scores": {
            "autonomous_search": (6, "SeekOut Assist builds searches from a JD; recruiter runs them"),
            "autonomous_screening": (6, "Assist ranks and explains matches; review is manual"),
            "autonomous_outreach": (6, "AI-drafted outreach; sending is recruiter-driven"),
            "scheduling_automation": (4, "No candidate-facing scheduling; ATS handoff"),
            "criteria_evaluation": (9, "JD-to-search with explainable matching"),
            "feedback_learning": (6, "Search-level tuning; no per-role learning loop"),
            "hard_filters": (9, "Deepest technical/cleared-talent filters reviewed (clearances, patents, GitHub)"),
            "trajectory_inference": (7, "Strong profile enrichment; limited attribute inference"),
            "channels": (6, "Email-focused"),
            "personalization": (7, "AI-drafted messages"),
            "sequencing": (7, "Solid campaigns; fewer testing features than hireEZ/Gem"),
            "reply_handling": (5, "Reply routing to the recruiter"),
            "source_breadth": (9, "Broad aggregated index incl. GitHub, papers, clearances"),
            "contact_finding": (9, "Strong email coverage; phone thinner"),
            "ats_integrations": (8, "Major ATS integrations"),
            "analytics": (8, "Talent analytics and pipeline insights"),
        },
    },
    "juicebox": {
        "name": "Juicebox (PeopleGPT)",
        "website": "https://juicebox.ai",
        "scores": {
            "autonomous_search": (5, "Natural-language search is recruiter-initiated per query"),
            "autonomous_screening": (6, "Cited-evidence matching against the query; manual review"),
            "autonomous_outreach": (5, "AI-drafted emails; recruiter sends"),
            "scheduling_automation": (3, "No scheduling automation"),
            "criteria_evaluation": (8, "NL queries evaluated with cited evidence per candidate"),
            "feedback_learning": (6, "Query refinement; no persistent per-role model"),
            "hard_filters": (6, "Filterable, less deep than SeekOut on technical/clearance"),
            "trajectory_inference": (6, "Understands NL requirements; limited trajectory modeling"),
            "channels": (6, "Email outreach with enrichment"),
            "personalization": (7, "AI personalization from profile evidence"),
            "sequencing": (7, "Sequenced campaigns, self-serve"),
            "reply_handling": (4, "Reply routing only"),
            "source_breadth": (8, "800M-profile index; web-wide"),
            "contact_finding": (7, "Built-in enrichment"),
            "ats_integrations": (6, "Growing list, lighter than incumbents"),
            "analytics": (6, "Campaign-level analytics"),
        },
    },
    "gem": {
        "name": "Gem",
        "website": "https://gem.com",
        "scores": {
            "autonomous_search": (5, "AI sourcing assists; recruiter-driven searches"),
            "autonomous_screening": (5, "Ranking assist only"),
            "autonomous_outreach": (7, "Sequences run automatically once launched"),
            "scheduling_automation": (5, "Scheduling links, not an agent"),
            "criteria_evaluation": (7, "JD-based matching assist"),
            "feedback_learning": (6, "Sequence/search tuning; no per-role calibration"),
            "hard_filters": (7, "Standard filtering"),
            "trajectory_inference": (5, "CRM-centric, not inference-led"),
            "channels": (7, "Email + InMail tracking"),
            "personalization": (7, "Templates with AI assist"),
            "sequencing": (9, "Category-leading sequences, A/B, send-time optimization"),
            "reply_handling": (5, "Reply detection and routing"),
            "source_breadth": (7, "Extension + CRM rediscovery over LinkedIn-centric sourcing"),
            "contact_finding": (8, "Strong email finding"),
            "ats_integrations": (9, "Deep ATS/CRM sync; Gem is also a CRM"),
            "analytics": (9, "Category-leading outbound and funnel analytics"),
        },
    },
    "findem": {
        "name": "Findem",
        "website": "https://findem.ai",
        "scores": {
            "autonomous_search": (6, "Attribute-based searches run and refresh continuously"),
            "autonomous_screening": (6, "Attribute matching narrows pools; review manual"),
            "autonomous_outreach": (5, "Campaigns exist; recruiter-configured"),
            "scheduling_automation": (3, "No scheduling automation"),
            "criteria_evaluation": (9, "Attribute inference ('built a data team at a startup') is a real capability gap"),
            "feedback_learning": (7, "Attribute tuning per search"),
            "hard_filters": (8, "Attribute-level hard requirements"),
            "trajectory_inference": (9, "3D data: person + company + time; strongest trajectory modeling reviewed"),
            "channels": (5, "Email-focused"),
            "personalization": (6, "Standard AI drafting"),
            "sequencing": (6, "Basic campaigns"),
            "reply_handling": (4, "Reply routing only"),
            "source_breadth": (8, "Large enriched index with company history data"),
            "contact_finding": (7, "Adequate; not its focus"),
            "ats_integrations": (8, "Enterprise ATS integrations"),
            "analytics": (8, "Talent analytics focus"),
        },
    },
    "fetcher": {
        "name": "Fetcher",
        "website": "https://fetcher.ai",
        "scores": {
            "autonomous_search": (8, "Recurring AI-sourced candidate batches delivered per role"),
            "autonomous_screening": (7, "AI pre-screen with human curation before delivery"),
            "autonomous_outreach": (8, "Automated sequences on approved candidates"),
            "scheduling_automation": (5, "Interest handoff; no booking agent"),
            "criteria_evaluation": (7, "Brief-based matching, curator-checked"),
            "feedback_learning": (7, "Batch approval/rejection tunes future batches"),
            "hard_filters": (6, "Brief-level requirements"),
            "trajectory_inference": (5, "Standard profile matching"),
            "channels": (6, "Email sequences"),
            "personalization": (7, "Template + AI assist"),
            "sequencing": (7, "Solid automated follow-ups"),
            "reply_handling": (5, "Interested-reply routing"),
            "source_breadth": (6, "Web sourcing; smaller index"),
            "contact_finding": (7, "Verified emails included"),
            "ats_integrations": (6, "Common ATS integrations"),
            "analytics": (6, "Campaign metrics"),
        },
    },
    "herohunt": {
        "name": "HeroHunt (Uwi)",
        "website": "https://herohunt.ai",
        "scores": {
            "autonomous_search": (8, "Uwi runs the search loop automatically from a brief"),
            "autonomous_screening": (7, "Automated screening; precision trails Noon on complex briefs"),
            "autonomous_outreach": (8, "Automated personalized outreach"),
            "scheduling_automation": (5, "Interest handoff only"),
            "criteria_evaluation": (6, "Brief-driven screening, lighter reasoning"),
            "feedback_learning": (6, "Feedback adjusts the search"),
            "hard_filters": (6, "Standard requirements"),
            "trajectory_inference": (4, "Keyword/skill-centric"),
            "channels": (7, "Email + LinkedIn"),
            "personalization": (7, "Per-candidate AI personalization"),
            "sequencing": (6, "Basic follow-ups"),
            "reply_handling": (4, "Routing only"),
            "source_breadth": (7, "1B-profile web index claim; broad coverage"),
            "contact_finding": (6, "Included, thinner coverage"),
            "ats_integrations": (4, "Minimal"),
            "analytics": (4, "Basic"),
        },
    },
    "dover": {
        "name": "Dover",
        "website": "https://dover.com",
        "scores": {
            "autonomous_search": (7, "Automated sourcing for common startup roles inside its free ATS"),
            "autonomous_screening": (6, "Criteria-based filtering tuned to startup roles"),
            "autonomous_outreach": (7, "Automated sequences from your domain"),
            "scheduling_automation": (6, "Scheduling links and coordination help"),
            "criteria_evaluation": (6, "Role presets + criteria"),
            "feedback_learning": (5, "Limited"),
            "hard_filters": (6, "Standard"),
            "trajectory_inference": (4, "Standard matching"),
            "channels": (6, "Email"),
            "personalization": (6, "Templated with variables"),
            "sequencing": (6, "Automated follow-ups"),
            "reply_handling": (5, "Routing"),
            "source_breadth": (5, "Common startup-role coverage"),
            "contact_finding": (6, "Included"),
            "ats_integrations": (6, "Is its own ATS; exports elsewhere"),
            "analytics": (6, "Funnel basics"),
        },
    },
    "linkedin-recruiter": {
        "name": "LinkedIn Recruiter",
        "website": "https://business.linkedin.com/talent-solutions/recruiter",
        "scores": {
            "autonomous_search": (4, "AI-assisted search inside a recruiter-driven workflow"),
            "autonomous_screening": (4, "Spotlights and match signals only"),
            "autonomous_outreach": (5, "AI-assisted InMail drafting; manual sends"),
            "scheduling_automation": (3, "No scheduling automation"),
            "criteria_evaluation": (6, "Recommended matches per project"),
            "feedback_learning": (5, "Project-level signals"),
            "hard_filters": (8, "40+ structured filters on first-party data"),
            "trajectory_inference": (5, "First-party data, keyword-led search"),
            "channels": (4, "InMail only; no email/SMS"),
            "personalization": (5, "AI-assisted drafts, template-heavy in practice"),
            "sequencing": (5, "InMail follow-ups"),
            "reply_handling": (3, "Manual"),
            "source_breadth": (6, "Single network (the largest one) \u2014 no open-web or licensed sources"),
            "contact_finding": (4, "No emails/phones without third-party tools"),
            "ats_integrations": (6, "ATS connectors via partners"),
            "analytics": (8, "Talent insights and pipeline reporting"),
        },
    },
}

CRIT_IDS = [c["id"] for d in CRITERIA["dimensions"] for c in d["criteria"]]


def build_capabilities():
    tools = []
    for slug, t in TOOLS.items():
        assert set(t["scores"].keys()) == set(CRIT_IDS), slug
        tools.append({
            "slug": slug,
            "name": t["name"],
            "website": t["website"],
            "review": f"{ST}/tools/{slug}/",
            "sources": [f"{ST}/tools/{slug}/", t["website"]],
            "scores": {cid: {"value": t["scores"][cid][0], "note": t["scores"][cid][1]} for cid in CRIT_IDS},
        })
    return {"cycle": CYCLE, "assessed": CYCLE_DATE, "rubric_version": CRITERIA["version"], "tools": tools}


def score(capabilities):
    rows = []
    for t in capabilities["tools"]:
        dims = {}
        composite = 0.0
        for d in CRITERIA["dimensions"]:
            vals = [t["scores"][c["id"]]["value"] for c in d["criteria"]]
            ds = sum(vals) / len(vals) / 10 * 100
            dims[d["id"]] = round1(ds)
            composite += d["weight"] * ds
        rows.append({
            "slug": t["slug"], "name": t["name"], "website": t["website"],
            "review": t["review"], "composite": round1(composite), "dimensions": dims,
        })
    rows.sort(key=lambda r: -r["composite"])
    for i, r in enumerate(rows):
        r["rank"] = i + 1
    return {
        "cycle": CYCLE, "published": CYCLE_DATE, "rubric_version": CRITERIA["version"],
        "weights": {d["id"]: d["weight"] for d in CRITERIA["dimensions"]},
        "rankings": rows,
    }


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    os.makedirs(CYCLE_DIR, exist_ok=True)
    caps = build_capabilities()
    lb = score(caps)

    def dump(name, obj):
        with open(os.path.join(CYCLE_DIR, name), "w") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)
            f.write("\n")

    dump("criteria.json", CRITERIA)
    dump("capabilities.json", caps)
    dump("leaderboard.json", lb)

    files = ["criteria.json", "capabilities.json", "scoring.mjs", "leaderboard.json"]
    manifest = {
        "cycle": CYCLE, "published": CYCLE_DATE,
        "files": {n: sha256(os.path.join(CYCLE_DIR, n)) for n in files},
    }
    dump("cycle.json", manifest)

    for r in lb["rankings"]:
        hist_path = os.path.join(ROOT, "data", "tools", f"{r['slug']}.json")
        hist = {"slug": r["slug"], "name": r["name"], "website": r["website"], "review": r["review"], "history": []}
        if os.path.exists(hist_path):
            hist = json.load(open(hist_path))
        hist["history"] = [h for h in hist["history"] if h["cycle"] != CYCLE]
        hist["history"].append({"cycle": CYCLE, "rank": r["rank"], "composite": r["composite"], "dimensions": r["dimensions"]})
        with open(hist_path, "w") as f:
            json.dump(hist, f, indent=2, ensure_ascii=False)
            f.write("\n")

    for r in lb["rankings"]:
        print(f'{r["rank"]:2d}  {r["name"]:24s} {r["composite"]:5.1f}  ' + " ".join(f'{r["dimensions"][d["id"]]:5.1f}' for d in CRITERIA["dimensions"]))


if __name__ == "__main__":
    sys.exit(main())

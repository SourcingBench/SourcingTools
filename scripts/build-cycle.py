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
    "version": "1.0.0",
    "cycle": CYCLE,
    "scale": "Each criterion is scored 0\u20134 against the published rubric: 0 = absent, 1 = minimal, 2 = partial, 3 = strong, 4 = best-in-class. Dimension score = mean of its criteria \u00d7 25 (0\u2013100). Composite = weighted sum of dimension scores.",
    "dimensions": [
        {
            "id": "autonomy",
            "name": "Autonomy",
            "weight": 0.30,
            "definition": "How much of the sourcing loop the tool runs without a recruiter driving each step.",
            "criteria": [
                {"id": "autonomous_search", "name": "Autonomous search", "definition": "Initiates and continuously runs candidate searches from a role brief without per-search recruiter operation."},
                {"id": "autonomous_screening", "name": "Autonomous screening", "definition": "Evaluates candidates against role criteria and produces accept/reject decisions with reasoning, rather than only ranking results for manual review."},
                {"id": "autonomous_outreach", "name": "Autonomous outreach", "definition": "Composes and sends personalized outreach and follow-ups without per-message recruiter action."},
                {"id": "scheduling_automation", "name": "Scheduling automation", "definition": "Handles candidate replies through to a booked interview (Q&A, availability, calendar booking)."},
            ],
        },
        {
            "id": "matching",
            "name": "Matching & screening depth",
            "weight": 0.25,
            "definition": "Quality and adaptability of candidate evaluation.",
            "criteria": [
                {"id": "criteria_evaluation", "name": "Structured criteria evaluation", "definition": "Evaluates against explicit role-specific criteria with per-candidate reasoning, beyond keyword/Boolean relevance."},
                {"id": "feedback_learning", "name": "Learning from feedback", "definition": "Adapts its matching per role from recruiter/hiring-manager feedback."},
                {"id": "hard_filters", "name": "Hard requirements", "definition": "Supports mandatory criteria that are never relaxed (certifications, clearances, locations)."},
                {"id": "trajectory_inference", "name": "Trajectory & context inference", "definition": "Reads career trajectory, company caliber, and inferred attributes rather than title/keyword matches."},
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
            "name": "Coverage & data",
            "weight": 0.15,
            "definition": "Breadth of candidate discovery and contact data.",
            "criteria": [
                {"id": "source_breadth", "name": "Source breadth", "definition": "Discovery beyond a single network: open web, GitHub, publications, licensed partners."},
                {"id": "contact_finding", "name": "Contact finding", "definition": "Email/phone enrichment coverage and accuracy."},
            ],
        },
        {
            "id": "workflow",
            "name": "Workflow & integrations",
            "weight": 0.10,
            "definition": "Fit into the surrounding recruiting stack.",
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
            "autonomous_search": (4, "Agent sources continuously from a role brief; keeps monitoring as new candidates enter the market"),
            "autonomous_screening": (4, "Per-candidate accept/reject verdicts with reasoning against calibrated role criteria"),
            "autonomous_outreach": (4, "Multi-touch personalized sequences sent and followed up by the agent"),
            "scheduling_automation": (4, "AI coordinator answers candidate questions and books interviews (calendar integration)"),
            "criteria_evaluation": (4, "Explicit role criteria with per-candidate reasoning and pass-rate reporting"),
            "feedback_learning": (4, "Calibration loop: recruiter grades early candidates, model adjusts per role; re-evaluates on criteria change"),
            "hard_filters": (4, "Non-negotiables: mandatory criteria the agent never relaxes"),
            "trajectory_inference": (3, "Interprets career trajectory and company caliber; less attribute search than Findem"),
            "channels": (4, "Email, LinkedIn, and SMS sequences"),
            "personalization": (4, "AI-generated per-candidate intros grounded in profile; above category average in our review"),
            "sequencing": (3, "Multi-step sequences with editing; no A/B testing at hireEZ/Gem depth"),
            "reply_handling": (4, "Coordinator handles candidate Q&A through to booking"),
            "source_breadth": (3, "Web-wide sourcing beyond LinkedIn; no 800M-profile aggregated database"),
            "contact_finding": (3, "Built-in email enrichment and verification"),
            "ats_integrations": (3, "20+ ATS providers via unified sync layer; fewer native bi-directional depth claims than hireEZ"),
            "analytics": (3, "Funnel and outbound performance metrics"),
        },
    },
    "hireez": {
        "name": "hireEZ",
        "website": "https://hireez.com",
        "scores": {
            "autonomous_search": (2, "AI Sourcing mode surfaces new matches continuously, but recruiter builds and owns searches"),
            "autonomous_screening": (2, "EZ Match ranks against the JD; recruiter reviews every shortlist"),
            "autonomous_outreach": (3, "AI-drafted sequenced outreach runs after recruiter launch"),
            "scheduling_automation": (1, "No candidate-facing scheduling agent; handoff to ATS"),
            "criteria_evaluation": (3, "JD-driven requirement extraction and ranked matching"),
            "feedback_learning": (2, "Match tuning within a search; no per-role calibration loop"),
            "hard_filters": (3, "Deep Boolean and healthcare/technical filters"),
            "trajectory_inference": (2, "Ranking beyond keywords, but title/skill-centric"),
            "channels": (2, "Email sequences; phone data provided but no SMS/LinkedIn sending"),
            "personalization": (3, "AI-written outreach from profile + JD"),
            "sequencing": (4, "Mature sequences with A/B testing and team tracking"),
            "reply_handling": (1, "Replies land with the recruiter"),
            "source_breadth": (4, "800M+ profiles aggregated from open web and licensed partners"),
            "contact_finding": (4, "Best-in-class contact coverage; quality varies by region"),
            "ats_integrations": (4, "~30 bi-directional ATS integrations plus ATS Rediscovery"),
            "analytics": (4, "Full funnel, sequence, and team analytics"),
        },
    },
    "seekout": {
        "name": "SeekOut",
        "website": "https://seekout.com",
        "scores": {
            "autonomous_search": (1, "SeekOut Assist builds searches from a JD; recruiter runs them"),
            "autonomous_screening": (2, "Assist ranks and explains matches; review is manual"),
            "autonomous_outreach": (1, "Drafts outreach; sending is recruiter-driven"),
            "scheduling_automation": (0, "None"),
            "criteria_evaluation": (3, "JD-to-search with explainable matching"),
            "feedback_learning": (1, "No per-role learning loop"),
            "hard_filters": (4, "Deepest technical/cleared-talent filters in the market (clearances, patents, GitHub)"),
            "trajectory_inference": (2, "Strong profile enrichment; limited attribute inference"),
            "channels": (1, "Email-focused"),
            "personalization": (2, "AI-drafted messages"),
            "sequencing": (2, "Basic campaigns"),
            "reply_handling": (0, "None"),
            "source_breadth": (4, "Broad aggregated index incl. GitHub, papers, clearances"),
            "contact_finding": (3, "Good email coverage; phone thinner"),
            "ats_integrations": (3, "Major ATS integrations"),
            "analytics": (3, "Talent analytics and pipeline insights"),
        },
    },
    "juicebox": {
        "name": "Juicebox (PeopleGPT)",
        "website": "https://juicebox.ai",
        "scores": {
            "autonomous_search": (1, "Natural-language search is recruiter-initiated per query"),
            "autonomous_screening": (2, "Cited-evidence matching against the query; manual review"),
            "autonomous_outreach": (1, "AI-drafted emails; recruiter sends"),
            "scheduling_automation": (0, "None"),
            "criteria_evaluation": (3, "NL queries evaluated with cited evidence per candidate"),
            "feedback_learning": (1, "Query refinement only; no persistent per-role model"),
            "hard_filters": (2, "Filterable, less deep than SeekOut on technical/clearance"),
            "trajectory_inference": (2, "Understands NL requirements; limited trajectory modeling"),
            "channels": (2, "Email outreach with enrichment"),
            "personalization": (3, "AI personalization from profile evidence"),
            "sequencing": (3, "Sequenced campaigns, self-serve"),
            "reply_handling": (0, "None"),
            "source_breadth": (3, "800M-profile index; web-wide"),
            "contact_finding": (3, "Built-in enrichment"),
            "ats_integrations": (2, "Growing list, lighter than incumbents"),
            "analytics": (2, "Campaign-level analytics"),
        },
    },
    "gem": {
        "name": "Gem",
        "website": "https://gem.com",
        "scores": {
            "autonomous_search": (1, "AI sourcing assists; recruiter-driven searches"),
            "autonomous_screening": (1, "Ranking assist only"),
            "autonomous_outreach": (2, "Sequences run automatically once launched"),
            "scheduling_automation": (1, "Scheduling links, not an agent"),
            "criteria_evaluation": (2, "JD-based matching assist"),
            "feedback_learning": (1, "No per-role calibration"),
            "hard_filters": (2, "Standard filtering"),
            "trajectory_inference": (1, "CRM-centric, not inference-led"),
            "channels": (2, "Email + InMail tracking"),
            "personalization": (2, "Templates with AI assist"),
            "sequencing": (4, "Category-leading sequences, A/B, send-time optimization"),
            "reply_handling": (1, "Reply detection and routing only"),
            "source_breadth": (2, "Extension + CRM rediscovery over LinkedIn-centric sourcing"),
            "contact_finding": (3, "Strong email finding"),
            "ats_integrations": (4, "Deep ATS/CRM sync; Gem is also a CRM"),
            "analytics": (4, "Best-in-class outbound and funnel analytics"),
        },
    },
    "findem": {
        "name": "Findem",
        "website": "https://findem.ai",
        "scores": {
            "autonomous_search": (2, "Attribute-based searches run and refresh continuously"),
            "autonomous_screening": (2, "Attribute matching narrows pools; review manual"),
            "autonomous_outreach": (1, "Campaigns exist; recruiter-configured"),
            "scheduling_automation": (0, "None"),
            "criteria_evaluation": (4, "Attribute inference ('built a data team at a startup') is a real capability gap"),
            "feedback_learning": (2, "Attribute tuning per search"),
            "hard_filters": (3, "Attribute-level hard requirements"),
            "trajectory_inference": (4, "3D data: person + company + time; strongest trajectory modeling reviewed"),
            "channels": (1, "Email-focused"),
            "personalization": (2, "Standard AI drafting"),
            "sequencing": (2, "Basic campaigns"),
            "reply_handling": (0, "None"),
            "source_breadth": (3, "Large enriched index with company history data"),
            "contact_finding": (2, "Adequate; not its focus"),
            "ats_integrations": (3, "Enterprise ATS integrations"),
            "analytics": (3, "Talent analytics focus"),
        },
    },
    "fetcher": {
        "name": "Fetcher",
        "website": "https://fetcher.ai",
        "scores": {
            "autonomous_search": (3, "Recurring AI-sourced candidate batches delivered per role"),
            "autonomous_screening": (2, "AI pre-screen with human curation before delivery"),
            "autonomous_outreach": (3, "Automated sequences on approved candidates"),
            "scheduling_automation": (1, "Interest handoff; no booking agent"),
            "criteria_evaluation": (2, "Brief-based matching, curator-checked"),
            "feedback_learning": (2, "Batch approval/rejection tunes future batches"),
            "hard_filters": (2, "Brief-level requirements"),
            "trajectory_inference": (1, "Standard profile matching"),
            "channels": (2, "Email sequences"),
            "personalization": (2, "Template + AI assist"),
            "sequencing": (3, "Solid automated follow-ups"),
            "reply_handling": (1, "Interested-reply routing"),
            "source_breadth": (2, "Web sourcing; smaller index"),
            "contact_finding": (3, "Verified emails included"),
            "ats_integrations": (2, "Common ATS integrations"),
            "analytics": (2, "Campaign metrics"),
        },
    },
    "herohunt": {
        "name": "HeroHunt (Uwi)",
        "website": "https://herohunt.ai",
        "scores": {
            "autonomous_search": (4, "Uwi runs the search loop autonomously from a brief"),
            "autonomous_screening": (3, "Automated screening; precision trails Noon on complex briefs"),
            "autonomous_outreach": (3, "Automated personalized outreach"),
            "scheduling_automation": (1, "Interest handoff only"),
            "criteria_evaluation": (2, "Brief-driven screening, lighter reasoning"),
            "feedback_learning": (2, "Feedback adjusts the search"),
            "hard_filters": (2, "Standard requirements"),
            "trajectory_inference": (1, "Keyword/skill-centric"),
            "channels": (2, "Email + LinkedIn"),
            "personalization": (3, "Per-candidate AI personalization"),
            "sequencing": (2, "Basic follow-ups"),
            "reply_handling": (1, "Routing only"),
            "source_breadth": (3, "1B-profile web index claim; broad coverage"),
            "contact_finding": (2, "Included, thinner coverage"),
            "ats_integrations": (1, "Minimal"),
            "analytics": (1, "Basic"),
        },
    },
    "dover": {
        "name": "Dover",
        "website": "https://dover.com",
        "scores": {
            "autonomous_search": (3, "Automated sourcing for common startup roles inside its free ATS"),
            "autonomous_screening": (2, "Criteria-based filtering tuned to startup roles"),
            "autonomous_outreach": (3, "Automated sequences from your domain"),
            "scheduling_automation": (2, "Scheduling links and coordination help"),
            "criteria_evaluation": (2, "Role presets + criteria"),
            "feedback_learning": (1, "Limited"),
            "hard_filters": (2, "Standard"),
            "trajectory_inference": (1, "Standard matching"),
            "channels": (2, "Email"),
            "personalization": (2, "Templated with variables"),
            "sequencing": (2, "Automated follow-ups"),
            "reply_handling": (1, "Routing"),
            "source_breadth": (2, "Common startup-role coverage"),
            "contact_finding": (2, "Included"),
            "ats_integrations": (2, "Is its own ATS; exports elsewhere"),
            "analytics": (2, "Funnel basics"),
        },
    },
    "linkedin-recruiter": {
        "name": "LinkedIn Recruiter",
        "website": "https://business.linkedin.com/talent-solutions/recruiter",
        "scores": {
            "autonomous_search": (1, "AI-assisted search inside a recruiter-driven workflow"),
            "autonomous_screening": (1, "Spotlights and match signals only"),
            "autonomous_outreach": (1, "AI-assisted InMail drafting; manual sends"),
            "scheduling_automation": (0, "None"),
            "criteria_evaluation": (2, "Recommended matches per project"),
            "feedback_learning": (1, "Project-level signals"),
            "hard_filters": (3, "40+ structured filters on first-party data"),
            "trajectory_inference": (1, "First-party data, keyword-led search"),
            "channels": (1, "InMail only; no email/SMS"),
            "personalization": (1, "AI-assisted drafts, template-heavy in practice"),
            "sequencing": (2, "InMail follow-ups"),
            "reply_handling": (0, "None"),
            "source_breadth": (1, "Single network (the largest one) \u2014 no open-web or licensed sources"),
            "contact_finding": (1, "No emails/phones without third-party tools"),
            "ats_integrations": (2, "ATS connectors via partners"),
            "analytics": (3, "Talent insights and pipeline reporting"),
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
            ds = sum(vals) / len(vals) / 4 * 100
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

#!/usr/bin/env python3
"""One-time builder for a SourcingBench cycle.

Encodes the editorial capability matrix (every check value cites the
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


def round2(x):
    """Round half up to 2 decimals, matching JS Math.round(x*100)/100."""
    return math.floor(x * 100 + 0.5) / 100

CYCLE = "August 2026"
CYCLE_DATE = "2026-08-26"
ROOT = os.path.join(os.path.dirname(__file__), "..")
CYCLE_DIR = os.path.join(ROOT, "data", "cycles", CYCLE)

ST = "https://sourcingtools.org"

# Evidence source quality tiers, best first. A criterion whose best source is
# vendor_claim or inference cannot award any check a 2 (enforced by the verifier).
SOURCE_TYPES = ["hands_on", "api_docs", "product_docs", "changelog", "vendor_claim", "third_party_review", "inference"]

# Verified-resolving evidence URLs per tool (checked 2026-08-26; bot-blocked
# pages such as G2 and some help centers are deliberately not cited).
SOURCES = {
    "noon": {"product": "https://noon.ai"},
    "hireez": {"product": "https://hireez.com/platform/"},
    "seekout": {"product": "https://seekout.com/platform", "docs": "https://support.seekout.com/"},
    "gem": {"product": "https://www.gem.com/product/ai-sourcing", "docs": "https://help.gem.com/"},
    "findem": {"product": "https://www.findem.ai/platform"},
    "fetcher": {"product": "https://fetcher.ai", "docs": "https://help.fetcher.ai/"},
    "juicebox": {"product": "https://juicebox.ai/peoplegpt"},
    "herohunt": {"product": "https://www.herohunt.ai/uwi"},
    "dover": {"product": "https://www.dover.com/sourcing", "docs": "https://help.dover.com/"},
    "linkedin-recruiter": {"product": "https://business.linkedin.com/talent-solutions/recruiter", "docs": "https://www.linkedin.com/help/recruiter"},
}

CRITERIA = {
    "version": "2.2.0",
    "cycle": CYCLE,
    "scale": "Each criterion decomposes into published capability checks. Each check is scored 0 (absent), 1 (partial or assisted), or 2 (fully supported), from documented, observable product behavior. Criterion score = points earned / points possible \u00d7 10. Dimension score = dimension points earned / dimension points possible \u00d7 100. Composite = weighted sum of dimension scores.",
    "dimensions": [
        {
            "id": "matching",
            "name": "Candidate matching & screening",
            "weight": 0.25,
            "definition": "The core job of an AI recruiting tool: finding the right candidates for a role and evaluating them accurately against its requirements.",
            "criteria": [
                {"id": "criteria_evaluation", "name": "Structured criteria evaluation", "definition": "Evaluates against explicit role-specific criteria with per-candidate reasoning, beyond keyword/Boolean relevance.", "checks": [
                    {"id": "structured_criteria", "name": "Role requirements captured as explicit, structured criteria (not only a Boolean string)"},
                    {"id": "per_candidate_reasoning", "name": "Written per-candidate reasoning against the role's criteria"},
                    {"id": "per_criterion_verdicts", "name": "Per-criterion verdicts (pass/fail or graded), not only an overall relevance rank"},
                    {"id": "evidence_citation", "name": "Cites the profile evidence behind each judgment"},
                    {"id": "criteria_editing", "name": "Criteria editable mid-role with candidates re-evaluated"},
                ]},
                {"id": "feedback_learning", "name": "Learning from feedback", "definition": "Adapts its matching per role from recruiter/hiring-manager feedback.", "checks": [
                    {"id": "calibration_round", "name": "Structured calibration round on early candidates"},
                    {"id": "per_role_persistence", "name": "Learning persists per role, not only per search session"},
                    {"id": "in_product_feedback", "name": "Recruiter/hiring-manager feedback captured in-product"},
                    {"id": "pipeline_reevaluation", "name": "Existing pipeline re-scored when criteria change"},
                ]},
                {"id": "hard_filters", "name": "Hard requirements", "definition": "Supports mandatory criteria that are never relaxed (certifications, clearances, locations).", "checks": [
                    {"id": "never_relaxed", "name": "Mandatory criteria that ranking never relaxes"},
                    {"id": "structured_fields", "name": "Deep structured fields (certifications, clearances, licenses)"},
                    {"id": "location_authorization", "name": "Location and work-authorization constraints"},
                    {"id": "filter_depth", "name": "Expert-grade Boolean/attribute filter depth"},
                ]},
                {"id": "trajectory_inference", "name": "Trajectory & context inference", "definition": "Reads career trajectory, company caliber, and inferred attributes rather than title/keyword matches.", "checks": [
                    {"id": "career_trajectory", "name": "Models career progression and tenure patterns"},
                    {"id": "company_context", "name": "Uses company caliber/stage context in matching"},
                    {"id": "inferred_attributes", "name": "Infers attributes beyond stated keywords"},
                    {"id": "temporal_modeling", "name": "Time-aware modeling of employment history"},
                ]},
            ],
        },
        {
            "id": "autonomy",
            "name": "Workflow automation",
            "weight": 0.20,
            "definition": "How much of the recruiting workflow the tool runs on its own \u2014 search, screening, outreach, and scheduling \u2014 versus assisting a recruiter who drives each step.",
            "criteria": [
                {"id": "autonomous_search", "name": "Automated search", "definition": "Initiates and continuously runs candidate searches from a role brief without per-search recruiter operation.", "checks": [
                    {"id": "brief_to_search", "name": "Starts sourcing from a role brief without manual query building"},
                    {"id": "continuous_monitoring", "name": "Continuously monitors for new candidates entering the market"},
                    {"id": "pool_expansion", "name": "Expands/refreshes the pool automatically as the role evolves"},
                    {"id": "unattended_operation", "name": "Runs without per-search recruiter operation"},
                ]},
                {"id": "autonomous_screening", "name": "Automated screening", "definition": "Evaluates candidates against role criteria and produces decisions with reasoning, rather than only ranking results for manual review.", "checks": [
                    {"id": "automatic_verdicts", "name": "Produces screening decisions without per-candidate review"},
                    {"id": "decision_reasoning", "name": "Decisions include written reasoning"},
                    {"id": "full_pool_coverage", "name": "Screens the full sourced pool, not a sample"},
                    {"id": "uncertainty_flagging", "name": "Flags uncertain cases for human review"},
                ]},
                {"id": "autonomous_outreach", "name": "Automated outreach", "definition": "Composes and sends personalized outreach and follow-ups without per-message recruiter action.", "checks": [
                    {"id": "auto_composition", "name": "Composes outreach without per-message drafting"},
                    {"id": "unattended_sending", "name": "Sends without per-message approval (approval mode optional)"},
                    {"id": "automatic_followups", "name": "Follow-ups fire automatically"},
                    {"id": "multichannel_automation", "name": "Automation spans more than one channel"},
                ]},
                {"id": "scheduling_automation", "name": "Scheduling automation", "definition": "Handles candidate replies through to a booked interview (Q&A, availability, calendar booking).", "checks": [
                    {"id": "candidate_qa", "name": "Answers candidate questions automatically"},
                    {"id": "availability_collection", "name": "Collects candidate availability"},
                    {"id": "calendar_booking", "name": "Books directly onto interviewer calendars"},
                    {"id": "reschedule_handling", "name": "Handles rescheduling without recruiter action"},
                ]},
            ],
        },
        {
            "id": "engagement",
            "name": "Outreach & engagement",
            "weight": 0.20,
            "definition": "Ability to reach sourced profiles and convert them into responsive candidates — including the contact data that determines whether outreach is possible at all.",
            "criteria": [
                {"id": "channels", "name": "Channel coverage", "definition": "Outreach channels available (email, LinkedIn, SMS/phone).", "checks": [
                    {"id": "email_sending", "name": "Email sending built in"},
                    {"id": "linkedin_sending", "name": "LinkedIn/InMail sending"},
                    {"id": "sms_outreach", "name": "SMS/text outreach"},
                    {"id": "deliverability_tooling", "name": "Sender deliverability tooling (domains, warmup, throttling)"},
                ]},
                {"id": "personalization", "name": "Personalization", "definition": "Per-candidate AI personalization grounded in the candidate's actual background.", "checks": [
                    {"id": "profile_grounding", "name": "Personalization grounded in the candidate's actual background"},
                    {"id": "role_grounding", "name": "Message tailored to the role's specific pitch"},
                    {"id": "tone_control", "name": "Tone and style controls"},
                    {"id": "beyond_merge_tokens", "name": "Goes beyond merge-token templates"},
                ]},
                {"id": "sequencing", "name": "Sequencing", "definition": "Multi-step sequences, scheduling windows, and testing.", "checks": [
                    {"id": "multi_step", "name": "Multi-step sequences"},
                    {"id": "stop_on_reply", "name": "Sequences stop automatically on reply"},
                    {"id": "send_time_optimization", "name": "Send-time windows or optimization"},
                    {"id": "ab_testing", "name": "A/B testing of messages"},
                    {"id": "team_templates", "name": "Team-shared templates and sequence tracking"},
                ]},
                {"id": "reply_handling", "name": "Reply handling", "definition": "Automated handling of candidate questions and replies.", "checks": [
                    {"id": "reply_classification", "name": "Replies detected and classified (interested / not / question)"},
                    {"id": "automated_answers", "name": "Common candidate questions answered automatically"},
                    {"id": "context_handoff", "name": "Clean handoff to the recruiter with conversation context"},
                    {"id": "logistics_conversation", "name": "Handles logistics (timing, process) conversationally"},
                ]},
                {"id": "contact_finding", "name": "Contact finding", "definition": "Email/phone enrichment coverage and accuracy — whether the tool can actually reach the candidates it surfaces.", "checks": [
                    {"id": "email_coverage", "name": "Personal email coverage"},
                    {"id": "phone_coverage", "name": "Phone number coverage"},
                    {"id": "verification", "name": "Verification and bounce protection"},
                    {"id": "continuous_refresh", "name": "Continuous re-enrichment of stale contact data"},
                ]},
            ],
        },
        {
            "id": "coverage",
            "name": "Talent pool coverage & data",
            "weight": 0.20,
            "definition": "Size, freshness, and quality of the searchable candidate pool.",
            "criteria": [
                {"id": "pool_quality", "name": "Talent pool size & quality", "definition": "How large, current, complete, and well-resolved the searchable profile pool is.", "checks": [
                    {"id": "index_scale", "name": "Pool scale (hundreds of millions of searchable profiles)"},
                    {"id": "profile_freshness", "name": "Profile freshness (actively maintained or continuously refreshed)"},
                    {"id": "profile_completeness", "name": "Profile completeness (full career history, education, skills)"},
                    {"id": "activity_signals", "name": "Candidate activity and openness-to-work signals"},
                    {"id": "global_coverage", "name": "Geographic and industry coverage"},
                    {"id": "identity_resolution", "name": "Identity resolution (one canonical profile per person, deduplicated)"},
                    {"id": "niche_coverage", "name": "Coverage of niche and specialist roles"},
                ]},
                {"id": "discovery_reach", "name": "Discovery reach", "definition": "Discovery beyond the pool itself: multi-source aggregation and rediscovery of known candidates.", "checks": [
                    {"id": "beyond_network", "name": "Sources beyond a single network (open web, GitHub, licensed partners)"},
                    {"id": "ats_rediscovery", "name": "Rediscovery of candidates already in the ATS/CRM"},
                ]},
            ],
        },
        {
            "id": "workflow",
            "name": "Integrations & reporting",
            "weight": 0.15,
            "definition": "Fit into the surrounding recruiting stack, and visibility into pipeline performance.",
            "criteria": [
                {"id": "ats_integrations", "name": "ATS integrations", "definition": "Breadth and depth of ATS/CRM sync.", "checks": [
                    {"id": "native_breadth", "name": "Breadth of native ATS integrations"},
                    {"id": "bidirectional_sync", "name": "Bi-directional sync"},
                    {"id": "dedupe_against_ats", "name": "Duplicate detection against existing ATS records"},
                    {"id": "api_webhooks", "name": "API and webhooks"},
                ]},
                {"id": "analytics", "name": "Analytics", "definition": "Funnel, outreach, and pipeline analytics.", "checks": [
                    {"id": "funnel_metrics", "name": "Pipeline/funnel metrics"},
                    {"id": "outreach_performance", "name": "Outreach performance (open/reply/interested rates)"},
                    {"id": "team_reporting", "name": "Team-level performance reporting"},
                    {"id": "exports_dashboards", "name": "Exports and dashboards"},
                ]},
            ],
        },
    ],
}

# tool -> (name, website, criterion -> (check values in rubric order, note))
TOOLS = {
    "noon": {
        "name": "Noon",
        "website": "https://noon.ai",
        "scores": {
            "criteria_evaluation": ([2, 2, 2, 1, 2], "Explicit role criteria with per-candidate reasoning and pass-rate reporting; evidence cited at the criterion level rather than per claim"),
            "feedback_learning": ([2, 2, 1, 2], "Calibration loop: recruiter grades early candidates, model adjusts per role; re-evaluates on criteria change"),
            "hard_filters": ([2, 1, 2, 1], "Non-negotiables never relaxed by ranking; structured-field and Boolean depth trail SeekOut/hireEZ"),
            "trajectory_inference": ([2, 2, 1, 1], "Interprets career trajectory and company caliber; less attribute inference than Findem"),
            "autonomous_search": ([2, 2, 1, 1], "Sources continuously from a role brief; pool refresh and fully unattended operation still involve the recruiter"),
            "autonomous_screening": ([2, 2, 2, 1], "Per-candidate verdicts with reasoning against calibrated role criteria across the full pool"),
            "autonomous_outreach": ([2, 2, 1, 1], "Personalized sequences composed automatically; sending runs in approval mode and multi-channel automation is partial"),
            "scheduling_automation": ([2, 1, 0, 0], "AI coordinator answers candidate questions; availability collection partial, no direct calendar booking or automated rescheduling yet"),
            "channels": ([2, 2, 2, 1], "Email, LinkedIn, and SMS sequences; deliverability tooling lighter than dedicated outbound platforms"),
            "personalization": ([2, 2, 1, 2], "AI-generated per-candidate intros grounded in profile evidence and the role's specific pitch"),
            "sequencing": ([2, 2, 1, 0, 2], "Multi-step sequences with editing and stop-on-reply; no A/B testing at hireEZ/Gem depth"),
            "reply_handling": ([2, 2, 1, 2], "Coordinator handles candidate Q&A and logistics conversationally, then hands off with context"),
            "pool_quality": ([2, 1, 1, 1, 1, 1, 1], "Web-scale aggregated index, but a younger data asset: refresh cadence, identity resolution, and niche depth still trail the incumbent pools"),
            "discovery_reach": ([2, 1], "Multi-source aggregation across the open web, technical sources, and licensed partners; ATS rediscovery newer than incumbents'"),
            "contact_finding": ([2, 2, 2, 2], "Category-leading email and phone coverage with verification and continuous re-enrichment"),
            "ats_integrations": ([2, 1, 1, 2], "20+ ATS providers via unified sync layer; fewer native bi-directional integrations than hireEZ"),
            "analytics": ([2, 2, 1, 1], "Funnel and outbound performance metrics; lighter team reporting than Gem"),
        },
    },
    "hireez": {
        "name": "hireEZ",
        "website": "https://hireez.com",
        "scores": {
            "criteria_evaluation": ([2, 1, 1, 2, 2], "JD-driven requirement extraction and ranked matching with match evidence; per-criterion verdicts partial"),
            "feedback_learning": ([1, 1, 2, 1], "Match tuning within a search; no per-role calibration loop"),
            "hard_filters": ([1, 2, 2, 2], "Deep Boolean and healthcare/technical filters; hard requirements interact with ranking"),
            "trajectory_inference": ([1, 2, 1, 1], "Ranking beyond keywords, though title/skill-centric"),
            "autonomous_search": ([2, 2, 1, 1], "AI Sourcing mode surfaces new matches continuously; recruiter builds and owns searches"),
            "autonomous_screening": ([1, 1, 2, 1], "EZ Match ranks the full pool against the JD with strong relevance; recruiter reviews shortlists"),
            "autonomous_outreach": ([2, 1, 2, 1], "AI-drafted sequenced outreach runs after recruiter launch"),
            "scheduling_automation": ([1, 1, 1, 1], "Scheduling handoff to ATS/calendar tooling; no candidate-facing agent"),
            "channels": ([2, 0, 1, 2], "Email sequences with phone data and mature deliverability controls; no LinkedIn/SMS sending"),
            "personalization": ([2, 2, 1, 1], "AI-written outreach from profile + JD"),
            "sequencing": ([2, 2, 2, 2, 1], "Mature sequences with A/B testing and send-time optimization"),
            "reply_handling": ([2, 1, 1, 1], "Reply detection and routing; replies handled by the recruiter"),
            "pool_quality": ([2, 1, 1, 1, 2, 1, 1], "800M+ aggregated profiles with broad geographic reach; aggregated data carries the usual staleness and duplicate-merge issues"),
            "discovery_reach": ([2, 1], "Open web plus licensed partners; ATS Rediscovery"),
            "contact_finding": ([2, 2, 2, 1], "Category-leading contact coverage with verification; quality varies by region"),
            "ats_integrations": ([2, 2, 1, 2], "~30 bi-directional ATS integrations plus API access"),
            "analytics": ([2, 2, 2, 1], "Full funnel, sequence, and team analytics"),
        },
    },
    "seekout": {
        "name": "SeekOut",
        "website": "https://seekout.com",
        "scores": {
            "criteria_evaluation": ([2, 2, 1, 2, 2], "SeekOut Assist builds JD-driven searches with explainable matching"),
            "feedback_learning": ([1, 1, 2, 1], "Search-level tuning; no per-role learning loop"),
            "hard_filters": ([1, 2, 2, 2], "Deepest technical/cleared-talent filters reviewed (clearances, patents, GitHub)"),
            "trajectory_inference": ([1, 2, 1, 1], "Strong profile enrichment; limited attribute inference"),
            "autonomous_search": ([2, 1, 1, 1], "Assist builds searches from a JD; recruiter runs them"),
            "autonomous_screening": ([1, 2, 1, 1], "Assist ranks and explains matches; review is manual"),
            "autonomous_outreach": ([2, 1, 1, 1], "AI-drafted outreach; sending is recruiter-driven"),
            "scheduling_automation": ([0, 1, 1, 1], "No candidate-facing scheduling; ATS handoff"),
            "channels": ([2, 0, 0, 2], "Email-focused with solid deliverability controls"),
            "personalization": ([2, 1, 1, 2], "AI-drafted messages from enriched profiles"),
            "sequencing": ([2, 2, 1, 1, 1], "Solid campaigns; fewer testing features than hireEZ/Gem"),
            "reply_handling": ([2, 0, 2, 0], "Reply routing to the recruiter with thread context"),
            "pool_quality": ([2, 1, 1, 1, 1, 1, 2], "Large aggregated index with the best niche depth reviewed (clearances, patents, healthcare licenses); freshness typical of aggregated data"),
            "discovery_reach": ([2, 1], "GitHub, papers, and specialty sources beyond the core index"),
            "contact_finding": ([2, 1, 2, 2], "Strong email coverage with verification; phone thinner"),
            "ats_integrations": ([2, 2, 1, 1], "Major ATS integrations"),
            "analytics": ([2, 1, 2, 2], "Talent analytics and pipeline insights"),
        },
    },
    "gem": {
        "name": "Gem",
        "website": "https://gem.com",
        "scores": {
            "criteria_evaluation": ([2, 1, 1, 1, 2], "JD-based matching assist inside the CRM"),
            "feedback_learning": ([1, 1, 2, 1], "Sequence/search tuning; no per-role calibration"),
            "hard_filters": ([1, 1, 2, 2], "Standard filtering, strong on CRM fields"),
            "trajectory_inference": ([1, 1, 1, 1], "CRM-centric, not inference-led"),
            "autonomous_search": ([1, 1, 1, 1], "AI sourcing assists; recruiter-driven searches"),
            "autonomous_screening": ([1, 1, 1, 1], "Ranking assist only"),
            "autonomous_outreach": ([1, 2, 2, 1], "Sequences run automatically once launched"),
            "scheduling_automation": ([0, 1, 2, 1], "Scheduling links with calendar booking, not an agent"),
            "channels": ([2, 1, 1, 2], "Email + InMail tracking with deliverability controls"),
            "personalization": ([1, 2, 1, 2], "Templates with AI assist"),
            "sequencing": ([2, 2, 2, 2, 2], "Category-leading sequences: A/B, send-time optimization, team tracking"),
            "reply_handling": ([2, 0, 2, 0], "Reply detection and routing with full thread history"),
            "pool_quality": ([1, 1, 1, 1, 1, 1, 1], "Own pool is modest — Gem rides on top of LinkedIn-centric sourcing plus the customer's CRM"),
            "discovery_reach": ([1, 2], "Extension-based capture; strongest CRM rediscovery reviewed"),
            "contact_finding": ([2, 1, 2, 1], "Strong email finding"),
            "ats_integrations": ([2, 2, 2, 2], "Deep bi-directional ATS/CRM sync; Gem is also a CRM"),
            "analytics": ([2, 2, 2, 1], "Category-leading outbound and funnel analytics"),
        },
    },
    "findem": {
        "name": "Findem",
        "website": "https://findem.ai",
        "scores": {
            "criteria_evaluation": ([2, 2, 2, 2, 1], "Attribute inference ('built a data team at a startup') is a real capability gap"),
            "feedback_learning": ([1, 2, 2, 1], "Attribute tuning per search"),
            "hard_filters": ([2, 2, 1, 1], "Attribute-level hard requirements"),
            "trajectory_inference": ([2, 2, 2, 2], "3D data: person + company + time; strongest trajectory modeling reviewed"),
            "autonomous_search": ([2, 1, 1, 1], "Attribute-based searches run and refresh continuously"),
            "autonomous_screening": ([1, 1, 2, 1], "Attribute matching narrows the full pool; review manual"),
            "autonomous_outreach": ([1, 1, 1, 1], "Campaigns exist; recruiter-configured"),
            "scheduling_automation": ([0, 1, 1, 0], "No scheduling automation"),
            "channels": ([2, 0, 0, 2], "Email-focused"),
            "personalization": ([1, 2, 1, 1], "Standard AI drafting"),
            "sequencing": ([2, 1, 1, 0, 1], "Basic campaigns"),
            "reply_handling": ([2, 0, 1, 0], "Reply routing only"),
            "pool_quality": ([2, 1, 1, 1, 1, 2, 1], "Large enriched index; 3D person+company+time data gives strong identity resolution"),
            "discovery_reach": ([2, 1], "Multi-source enrichment with company history data"),
            "contact_finding": ([2, 1, 1, 1], "Adequate; not its focus"),
            "ats_integrations": ([2, 2, 1, 1], "Enterprise ATS integrations"),
            "analytics": ([2, 1, 2, 2], "Talent analytics focus"),
        },
    },
    "fetcher": {
        "name": "Fetcher",
        "website": "https://fetcher.ai",
        "scores": {
            "criteria_evaluation": ([2, 1, 1, 1, 1], "Brief-based matching, curator-checked"),
            "feedback_learning": ([1, 2, 1, 2], "Batch approval/rejection tunes future batches"),
            "hard_filters": ([1, 1, 2, 1], "Brief-level requirements"),
            "trajectory_inference": ([1, 1, 1, 1], "Standard profile matching"),
            "autonomous_search": ([2, 2, 1, 2], "Recurring AI-sourced candidate batches delivered per role"),
            "autonomous_screening": ([2, 1, 2, 1], "AI pre-screen with human curation before delivery"),
            "autonomous_outreach": ([2, 2, 2, 1], "Automated sequences on approved candidates"),
            "scheduling_automation": ([1, 1, 1, 1], "Interest handoff; no booking agent"),
            "channels": ([2, 0, 1, 2], "Email sequences with deliverability care"),
            "personalization": ([2, 2, 1, 1], "Template + AI assist"),
            "sequencing": ([2, 2, 1, 0, 1], "Solid automated follow-ups"),
            "reply_handling": ([2, 1, 1, 0], "Interested-reply routing"),
            "pool_quality": ([1, 1, 1, 0, 1, 1, 1], "Smaller curated pool, adequate for common roles"),
            "discovery_reach": ([2, 1], "Web sourcing beyond one network; CRM rediscovery basic"),
            "contact_finding": ([2, 1, 2, 1], "Verified emails included"),
            "ats_integrations": ([2, 1, 1, 1], "Common ATS integrations"),
            "analytics": ([1, 2, 1, 1], "Campaign metrics"),
        },
    },
    "juicebox": {
        "name": "Juicebox (PeopleGPT)",
        "website": "https://juicebox.ai",
        "scores": {
            "criteria_evaluation": ([2, 2, 1, 2, 1], "NL queries evaluated with cited evidence per candidate"),
            "feedback_learning": ([1, 1, 1, 2], "Query refinement; no persistent per-role model"),
            "hard_filters": ([1, 1, 1, 2], "Filterable, less deep than SeekOut on technical/clearance"),
            "trajectory_inference": ([1, 1, 2, 1], "Understands NL requirements; limited trajectory modeling"),
            "autonomous_search": ([2, 1, 1, 0], "Natural-language search is recruiter-initiated per query"),
            "autonomous_screening": ([1, 1, 2, 1], "Cited-evidence matching against the query; manual review"),
            "autonomous_outreach": ([2, 0, 1, 1], "AI-drafted emails; recruiter sends"),
            "scheduling_automation": ([0, 0, 1, 1], "No scheduling automation"),
            "channels": ([2, 0, 1, 2], "Email outreach with enrichment"),
            "personalization": ([2, 2, 1, 1], "AI personalization from profile evidence"),
            "sequencing": ([2, 2, 1, 0, 1], "Sequenced campaigns, self-serve"),
            "reply_handling": ([2, 0, 1, 0], "Reply routing only"),
            "pool_quality": ([2, 1, 1, 1, 1, 1, 1], "800M-profile web index; aggregated-data freshness"),
            "discovery_reach": ([2, 0], "Web-wide aggregation; no ATS rediscovery"),
            "contact_finding": ([2, 1, 1, 1], "Built-in enrichment"),
            "ats_integrations": ([1, 1, 1, 2], "Growing list, lighter than incumbents"),
            "analytics": ([1, 2, 1, 1], "Campaign-level analytics"),
        },
    },
    "herohunt": {
        "name": "HeroHunt (Uwi)",
        "website": "https://herohunt.ai",
        "scores": {
            "criteria_evaluation": ([1, 2, 1, 1, 1], "Brief-driven screening, lighter reasoning"),
            "feedback_learning": ([1, 1, 1, 2], "Feedback adjusts the search"),
            "hard_filters": ([1, 1, 2, 1], "Standard requirements"),
            "trajectory_inference": ([1, 1, 1, 0], "Keyword/skill-centric"),
            "autonomous_search": ([2, 2, 1, 2], "Uwi runs the search loop automatically from a brief"),
            "autonomous_screening": ([2, 1, 2, 1], "Automated screening; precision trails Noon on complex briefs"),
            "autonomous_outreach": ([2, 2, 2, 1], "Automated personalized outreach"),
            "scheduling_automation": ([1, 1, 1, 1], "Interest handoff only"),
            "channels": ([2, 2, 0, 1], "Email + LinkedIn"),
            "personalization": ([2, 2, 1, 1], "Per-candidate AI personalization"),
            "sequencing": ([2, 2, 1, 0, 0], "Basic follow-ups"),
            "reply_handling": ([2, 1, 0, 0], "Routing only"),
            "pool_quality": ([2, 1, 1, 0, 1, 0, 1], "1B-profile web index claim; freshness, dedup, and completeness are visibly uneven"),
            "discovery_reach": ([2, 0], "Web-wide aggregation; no ATS rediscovery"),
            "contact_finding": ([2, 0, 1, 1], "Included, thinner coverage"),
            "ats_integrations": ([1, 1, 0, 1], "Minimal"),
            "analytics": ([1, 1, 0, 1], "Basic"),
        },
    },
    "dover": {
        "name": "Dover",
        "website": "https://dover.com",
        "scores": {
            "criteria_evaluation": ([1, 1, 1, 1, 2], "Role presets + criteria"),
            "feedback_learning": ([1, 1, 1, 1], "Limited"),
            "hard_filters": ([1, 1, 2, 1], "Standard"),
            "trajectory_inference": ([1, 1, 1, 0], "Standard matching"),
            "autonomous_search": ([2, 2, 1, 1], "Automated sourcing for common startup roles inside its free ATS"),
            "autonomous_screening": ([1, 1, 2, 1], "Criteria-based filtering tuned to startup roles"),
            "autonomous_outreach": ([2, 1, 2, 1], "Automated sequences from your domain"),
            "scheduling_automation": ([1, 2, 1, 1], "Scheduling links and coordination help"),
            "channels": ([2, 0, 1, 2], "Email"),
            "personalization": ([1, 1, 1, 2], "Templated with variables"),
            "sequencing": ([2, 2, 1, 0, 0], "Automated follow-ups"),
            "reply_handling": ([2, 1, 1, 0], "Routing"),
            "pool_quality": ([1, 1, 1, 0, 1, 1, 1], "Pool tuned to common startup roles; thin outside them"),
            "discovery_reach": ([1, 1], "Limited multi-source reach; rediscovery within its own ATS"),
            "contact_finding": ([2, 1, 1, 1], "Included"),
            "ats_integrations": ([1, 1, 1, 2], "Is its own ATS; exports elsewhere"),
            "analytics": ([2, 1, 1, 1], "Funnel basics"),
        },
    },
    "linkedin-recruiter": {
        "name": "LinkedIn Recruiter",
        "website": "https://business.linkedin.com/talent-solutions/recruiter",
        "scores": {
            "criteria_evaluation": ([1, 1, 1, 2, 1], "Recommended matches per project"),
            "feedback_learning": ([1, 1, 1, 1], "Project-level signals"),
            "hard_filters": ([2, 2, 2, 1], "40+ structured filters on first-party data"),
            "trajectory_inference": ([1, 2, 1, 1], "First-party employment data gives reliable company context; search itself is keyword-led"),
            "autonomous_search": ([1, 1, 1, 0], "AI-assisted search inside a recruiter-driven workflow"),
            "autonomous_screening": ([1, 1, 1, 0], "Spotlights and match signals only"),
            "autonomous_outreach": ([1, 0, 1, 1], "AI-assisted InMail drafting; manual sends"),
            "scheduling_automation": ([0, 0, 1, 1], "No scheduling automation"),
            "channels": ([0, 2, 0, 1], "InMail only; no email/SMS"),
            "personalization": ([1, 1, 1, 1], "AI-assisted drafts, template-heavy in practice"),
            "sequencing": ([1, 2, 0, 0, 1], "InMail follow-ups"),
            "reply_handling": ([1, 0, 1, 0], "Manual"),
            "pool_quality": ([2, 2, 1, 2, 2, 2, 2], "The category's reference pool: 1B+ member-maintained profiles, unmatched freshness, explicit open-to-work signals, global reach, and one canonical profile per person"),
            "discovery_reach": ([0, 1], "Walled garden \u2014 nothing beyond the network; partial rediscovery via ATS connectors"),
            "contact_finding": ([0, 1, 1, 0], "No emails/phones without third-party tools"),
            "ats_integrations": ([1, 1, 1, 1], "ATS connectors via partners"),
            "analytics": ([2, 1, 2, 2], "Talent insights and pipeline reporting"),
        },
    },
}

# tool -> criterion -> verbatim quote from the tool's cited product page
# (exact rendered text, captured 2026-08-26). Quotes are only recorded where
# the cited page states the capability in so many words; criteria without an
# on-page statement carry the citation without a quote.
QUOTES = {
    "noon": {
        "criteria_evaluation": "Searches candidates across the web and evaluates candidate profiles using your specific criteria",
        "feedback_learning": "Adapts and learns from hiring manager feedback on the quality of sourced candidates",
        "autonomous_search": "An AI employee that performs the end-to-end role of a talent sourcer",
        "autonomous_screening": "Noon: the autonomous AI recruiter that sources, screens, and reaches out to qualified candidates",
        "autonomous_outreach": "Sends multi-channel, personalized campaigns and cultivates relationships with candidates for current/prospective positions",
        "channels": "Sends multi-channel, personalized campaigns and cultivates relationships with candidates for current/prospective positions",
        "personalization": "Noon is trained on your unique writing style, capturing your voice and tone with remarkable accuracy.",
        "sequencing": "Sends multi-channel, personalized campaigns and cultivates relationships with candidates for current/prospective positions",
        "pool_quality": "Searches candidates across the web and evaluates candidate profiles using your specific criteria",
        "discovery_reach": "Searches candidates across the web and evaluates candidate profiles using your specific criteria",
    },
    "hireez": {
        "criteria_evaluation": "Input your job description or keywords, and agentic AI will pull all relevant candidates from over 40 sources across the open web. Then, let AI review take a deeper look at every candidate's profile, surfacing them by how well they fit the job criteria and highlighting relevant sections of each candidate's profile so you can understand their fitness.",
        "hard_filters": "Build teams with agentic AI for cleared candidates",
        "autonomous_search": "AI Sourcing delivers 7x more qualified talent and 2x higher engagement by searching the open web and your ATS with real-time agentic intelligence.",
        "autonomous_screening": "Our resume screening solution helps you evaluate resumes against the job description by parsing context instead of just keywords.",
        "autonomous_outreach": "Automate the message creation, outreach scheduling, and candidate nurturing processes with a combination of generative and agentic AI.",
        "personalization": "Agentic AI personalizes communication across email, SMS, and InMail, crafting timely, relevant messages that drive stronger engagement and faster candidate responses.",
        "pool_quality": "Open Web, Deep Search. and Partner Networks across 45+ platforms.",
        "discovery_reach": "Rediscovery delivers 2.5x more qualified candidates and 80% stronger pipelines by re-engaging past applicants already in your ATS.",
        "ats_integrations": "By seamlessly integrating with over 50 ATS partners, our platform eliminates the need for multiple top of funnel tools - minimizing friction to existing ATS workflows, reducing costs, and enhancing overall efficiency.",
        "analytics": "Real-time recruitment analytics show you important stats such as which hiring strategies are most effective and whether your recruiters are meeting important KPIs, giving you the data you need to refine strategies and show your team's ROI to leadership.",
    },
    "seekout": {
        "criteria_evaluation": "Create role-specific workflows with AI-assisted search, automated rubrics, and smart shortlisting. Go from job description to qualified candidates faster with built-in best practices.",
        "hard_filters": "Security-cleared candidates for defense and gov",
        "autonomous_search": "Go beyond keywords to find hidden talent others miss. Search 1B+ profiles across external sources and your ATS with AI that understands context, not just terms.",
        "autonomous_screening": "Process thousands of inbound applicants in hours, not weeks. AI evaluates candidates against your criteria and delivers qualified shortlists so you focus on the best.",
        "autonomous_outreach": "Engage passive candidates with personalized multi-touch campaigns. AI crafts tailored messages that get responses while you focus on strategy and building relationships.",
        "personalization": "Engage passive candidates with personalized multi-touch campaigns. AI crafts tailored messages that get responses while you focus on strategy and building relationships.",
        "sequencing": "Engage passive candidates with personalized multi-touch campaigns. AI crafts tailored messages that get responses while you focus on strategy and building relationships.",
        "pool_quality": "The agentic AI recruiting platform to source from 1B+ profiles, screen applicants, and engage candidates at scale.",
        "discovery_reach": "Source and enrich profiles from any website",
        "ats_integrations": "ATS, CRM, and HCM integrations",
        "analytics": "Visualize talent pools and labor market data. Make informed decisions about where to source, how to compete, and what skills are available in your target markets.",
    },
    "gem": {
        "criteria_evaluation": "Every result comes with enriched profile data, past engagement history, and a match score with clear reasoning, so you can move from search to outreach in minutes.",
        "autonomous_outreach": "Craft multi-stage sequences that reference past conversations, interviews, recent promotions, and more. Just tell Gem what you want to incorporate, and it\u2019ll automatically draft the message.",
        "channels": "Gem combines search, outreach, and pipeline management in one place — with AI-personalized sequences, send-on-behalf-of, omnichannel outreach (email, SMS, InMail), and outreach analytics to track what's actually converting.",
        "personalization": "Craft multi-stage sequences that reference past conversations, interviews, recent promotions, and more. Just tell Gem what you want to incorporate, and it\u2019ll automatically draft the message.",
        "sequencing": "Measure the success of all outreach to identify which strategies drive the highest conversions. A/B test subject lines, visualize diversity analytics, and more.",
        "discovery_reach": "Gem also surfaces past candidates already in your ATS as part of every search, so you're never starting from scratch.",
        "contact_finding": "Gem provides verified contact information — including direct email addresses — with an industry-best 98% email delivery rate.",
        "ats_integrations": "Gem integrates with Greenhouse, Workday, Lever, iCIMS, SuccessFactors, and more — so sourced candidates flow directly into your existing workflow.",
        "analytics": "Forecast hiring needs, surface pipeline bottlenecks, and prove your team's impact — no BI team required.",
    },
    "findem": {
        "trajectory_inference": "Every talent decision raises the same questions: Who is this person? What have they learned over time? Who have they worked with, where did they succeed?",
        "autonomous_search": "Turn static posts into hire-ready candidates, delivered directly to your team.",
        "discovery_reach": "Find and prioritize the right people across channels, without tool sprawl or manual effort.",
        "personalization": "Keep candidates engaged with messages that reflect a person\u2019s background and timing, at any scale.",
        "analytics": "See what moves candidates forward and where attention is best spent, without digging through reports.",
        "ats_integrations": "Built to work with your existing systems.",
    },
    "fetcher": {
        "criteria_evaluation": "Our advanced AI technology streamlines the candidate screening process, while our expert team, paired with AI, efficiently sources high-quality candidate profiles tailored to your hiring needs.",
        "autonomous_search": "We take care of sourcing so you can focus on your candidate experience",
        "autonomous_screening": "Our advanced AI technology streamlines the candidate screening process, while our expert team, paired with AI, efficiently sources high-quality candidate profiles tailored to your hiring needs.",
        "autonomous_outreach": "I can review a batch in 15 minutes or less, add them to an email campaign, then set it and forget it until I start seeing responses in my inbox.",
        "sequencing": "I can review a batch in 15 minutes or less, add them to an email campaign, then set it and forget it until I start seeing responses in my inbox.",
        "discovery_reach": "Say goodbye to hours spent digging through databases, job boards, and resumes for top talent.",
        "ats_integrations": "Boost your recruiting capacity with robust technology integrations including ATS, CRM, email, and even Slack.",
    },
    "juicebox": {
        "criteria_evaluation": "Juicebox evaluates up to 5,000 profiles to reveal which candidates are the best match for your open role.",
        "hard_filters": "Slice your talent pool by seniority, skills, roles, activity level, and education.",
        "autonomous_search": "Juicebox understands your searches, configures filters, and supports full natural-language search.",
        "autonomous_screening": "Juicebox evaluates up to 5,000 profiles to reveal which candidates are the best match for your open role.",
        "pool_quality": "Juicebox has 800 million profiles across the globe from dozens of data sources.",
        "discovery_reach": "Search across 800M+ profiles from 30+ data sources",
        "ats_integrations": "Juicebox integrates with 41 ATS systems and 21 CRMs.",
    },
    "herohunt": {
        "criteria_evaluation": "Contextual screening AI that scores profiles on every possible requirement.",
        "autonomous_search": "AI Recruiter can recruit for you on complete autopilot, from finding 1 billion profiles on the web to AI screening candidates and even outreach.",
        "autonomous_screening": "Language model driven AI profile screening",
        "autonomous_outreach": "Automated and hyper-personalized outreach",
        "personalization": "Powerful prompt based personalization to speak to the details that count.",
        "pool_quality": "Let AI Recruiter recruit the best from 1 billion profiles worldwide",
        "discovery_reach": "GitHub, Stack Overflow and more",
        "contact_finding": "Find verified contact details",
    },
    "dover": {
        "autonomous_outreach": "Instantly connect with top talent and send personalized emails in seconds.",
        "channels": "Find emails & send outreach in 2 clicks",
        "contact_finding": "Find emails & send outreach in 2 clicks",
        "analytics": "Monitor your pipeline from referral to hire",
        "ats_integrations": "Slack, job boards, API, and MCP",
    },
    "linkedin-recruiter": {
        "criteria_evaluation": "Hiring Assistant reviews thousands of applicants against your criteria in minutes, highlighting top candidates with the skills and experience that matter most.",
        "hard_filters": "Choose when to use Hiring Assistant or switch to Recruiter for manual search capabilities, including 40+ advanced filters, keywords, and Boolean.",
        "channels": "Reach candidates directly on LinkedIn with Recruiter\u2019s built-in messaging — designed for personalized messaging at scale (up to 150 InMails per month, per seat.)",
        "pool_quality": "Hiring Assistant taps into LinkedIn\u2019s network of 1B+ professionals to find qualified candidates you might have otherwise missed.",
        "analytics": "Unlock insights across your entire hiring funnel and benchmark against competitors to optimize your strategy.",
    },
}

CRIT_META = {c["id"]: c for d in CRITERIA["dimensions"] for c in d["criteria"]}
CRIT_IDS = list(CRIT_META.keys())


def build_capabilities():
    tools = []
    for slug, t in TOOLS.items():
        assert set(t["scores"].keys()) == set(CRIT_IDS), slug
        scores = {}
        src = SOURCES[slug]
        for cid in CRIT_IDS:
            vals, note = t["scores"][cid]
            checks = CRIT_META[cid]["checks"]
            assert len(vals) == len(checks), f"{slug}.{cid}"
            assert all(v in (0, 1, 2) for v in vals), f"{slug}.{cid}"
            points = sum(vals)
            maximum = 2 * len(checks)
            evidence = [{
                "url": src["product"],
                "source_type": "product_docs",
                "accessed": CYCLE_DATE,
                "claim": note,
            }]
            quote = QUOTES.get(slug, {}).get(cid)
            if quote:
                evidence[0]["quote"] = quote
            if "docs" in src:
                evidence.append({
                    "url": src["docs"],
                    "source_type": "product_docs",
                    "accessed": CYCLE_DATE,
                    "claim": note,
                })
            scores[cid] = {
                "checks": {chk["id"]: v for chk, v in zip(checks, vals)},
                "points": points,
                "max": maximum,
                "value": round1(points / maximum * 10),
                "note": note,
                "evidence": evidence,
            }
        tools.append({
            "slug": slug,
            "name": t["name"],
            "website": t["website"],
            "review": f"{ST}/tools/{slug}/",
            "sources": sorted(set(src.values())),
            "scores": scores,
        })
    return {
        "cycle": CYCLE,
        "assessed": CYCLE_DATE,
        "rubric_version": CRITERIA["version"],
        "evidence_schema": {
            "version": 1,
            "source_types": SOURCE_TYPES,
            "rules": [
                "Every criterion carries at least one evidence record: url, source_type, accessed date, and the claim relied on.",
                "Where the cited page states the capability in so many words, the record also carries the verbatim quote; criteria without an on-page statement carry the citation without a quote rather than an invented one.",
                "Evidence URLs must resolve; CI link-checks them.",
                "The accessed date must fall within the cycle's assessment window.",
                "Publisher-owned pages (sourcingtools.org, sourcingbench.github.io) are banned as evidence.",
                "A criterion whose best source is vendor_claim or inference cannot award any check a 2.",
            ],
        },
        "tools": tools,
    }


def score(capabilities):
    with open(os.path.join(ROOT, "data", "disclosures.json")) as f:
        disclosures = json.load(f)["vendors"]
    rows = []
    for t in capabilities["tools"]:
        dims = {}
        composite = 0.0
        for d in CRITERIA["dimensions"]:
            points = sum(t["scores"][c["id"]]["points"] for c in d["criteria"])
            maximum = sum(t["scores"][c["id"]]["max"] for c in d["criteria"])
            ds = points / maximum * 100
            dims[d["id"]] = round1(ds)
            composite += d["weight"] * ds
        rows.append({
            "slug": t["slug"], "name": t["name"], "website": t["website"],
            "review": t["review"], "composite": round2(composite), "dimensions": dims,
            "referral": disclosures[t["slug"]]["referral"],
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
        print(f'{r["rank"]:2d}  {r["name"]:24s} {r["composite"]:6.2f}  ' + " ".join(f'{r["dimensions"][d["id"]]:5.1f}' for d in CRITERIA["dimensions"]))


if __name__ == "__main__":
    sys.exit(main())

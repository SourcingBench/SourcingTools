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

CRITERIA = {
    "version": "2.1.0",
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
            "definition": "Ability to convert sourced profiles into responsive candidates.",
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
            ],
        },
        {
            "id": "coverage",
            "name": "Talent pool coverage & data",
            "weight": 0.20,
            "definition": "Breadth of candidate discovery and quality of contact data.",
            "criteria": [
                {"id": "source_breadth", "name": "Source breadth", "definition": "Discovery beyond a single network: open web, GitHub, publications, licensed partners.", "checks": [
                    {"id": "open_web", "name": "Open-web profiles beyond a single network"},
                    {"id": "technical_sources", "name": "Technical sources (GitHub, publications, patents)"},
                    {"id": "licensed_partners", "name": "Licensed/partner data sources"},
                    {"id": "index_scale", "name": "Index scale (hundreds of millions of profiles)"},
                    {"id": "ats_rediscovery", "name": "Rediscovery of candidates already in the ATS/CRM"},
                ]},
                {"id": "contact_finding", "name": "Contact finding", "definition": "Email/phone enrichment coverage and accuracy.", "checks": [
                    {"id": "email_coverage", "name": "Personal email coverage"},
                    {"id": "phone_coverage", "name": "Phone number coverage"},
                    {"id": "verification", "name": "Verification and bounce protection"},
                    {"id": "continuous_refresh", "name": "Continuous re-enrichment of stale contact data"},
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
            "personalization": ([2, 2, 1, 2], "AI-generated per-candidate intros grounded in profile; above category average in our review"),
            "sequencing": ([2, 2, 1, 0, 2], "Multi-step sequences with editing and stop-on-reply; no A/B testing at hireEZ/Gem depth"),
            "reply_handling": ([2, 2, 1, 2], "Coordinator handles candidate Q&A and logistics conversationally, then hands off with context"),
            "source_breadth": ([2, 2, 2, 2, 1], "Web-scale sourcing across the open web, technical sources, and licensed partners; ATS rediscovery newer than incumbents'"),
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
            "source_breadth": ([2, 2, 2, 2, 1], "800M+ profiles aggregated from open web and licensed partners; ATS Rediscovery"),
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
            "source_breadth": ([2, 2, 2, 2, 1], "Broad aggregated index incl. GitHub, papers, clearances"),
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
            "source_breadth": ([1, 1, 1, 1, 2], "Extension + CRM rediscovery over LinkedIn-centric sourcing"),
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
            "source_breadth": ([2, 1, 1, 2, 1], "Large enriched index with company history data"),
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
            "source_breadth": ([2, 1, 0, 1, 1], "Web sourcing; smaller index"),
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
            "source_breadth": ([2, 2, 1, 2, 0], "800M-profile index; web-wide"),
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
            "source_breadth": ([2, 2, 0, 2, 0], "1B-profile web index claim; broad coverage"),
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
            "source_breadth": ([1, 1, 0, 1, 1], "Common startup-role coverage"),
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
            "trajectory_inference": ([1, 1, 1, 1], "First-party data, keyword-led search"),
            "autonomous_search": ([1, 1, 1, 0], "AI-assisted search inside a recruiter-driven workflow"),
            "autonomous_screening": ([1, 1, 1, 0], "Spotlights and match signals only"),
            "autonomous_outreach": ([1, 0, 1, 1], "AI-assisted InMail drafting; manual sends"),
            "scheduling_automation": ([0, 0, 1, 1], "No scheduling automation"),
            "channels": ([0, 2, 0, 1], "InMail only; no email/SMS"),
            "personalization": ([1, 1, 1, 1], "AI-assisted drafts, template-heavy in practice"),
            "sequencing": ([1, 2, 0, 0, 1], "InMail follow-ups"),
            "reply_handling": ([1, 0, 1, 0], "Manual"),
            "source_breadth": ([0, 0, 0, 2, 1], "Single network (the largest one) \u2014 no open-web or licensed sources"),
            "contact_finding": ([0, 1, 1, 0], "No emails/phones without third-party tools"),
            "ats_integrations": ([1, 1, 1, 1], "ATS connectors via partners"),
            "analytics": ([2, 1, 2, 2], "Talent insights and pipeline reporting"),
        },
    },
}

CRIT_META = {c["id"]: c for d in CRITERIA["dimensions"] for c in d["criteria"]}
CRIT_IDS = list(CRIT_META.keys())


def build_capabilities():
    tools = []
    for slug, t in TOOLS.items():
        assert set(t["scores"].keys()) == set(CRIT_IDS), slug
        scores = {}
        for cid in CRIT_IDS:
            vals, note = t["scores"][cid]
            checks = CRIT_META[cid]["checks"]
            assert len(vals) == len(checks), f"{slug}.{cid}"
            assert all(v in (0, 1, 2) for v in vals), f"{slug}.{cid}"
            points = sum(vals)
            maximum = 2 * len(checks)
            scores[cid] = {
                "checks": {chk["id"]: v for chk, v in zip(checks, vals)},
                "points": points,
                "max": maximum,
                "value": round1(points / maximum * 10),
                "note": note,
            }
        tools.append({
            "slug": slug,
            "name": t["name"],
            "website": t["website"],
            "review": f"{ST}/tools/{slug}/",
            "sources": [f"{ST}/tools/{slug}/", t["website"]],
            "scores": scores,
        })
    return {"cycle": CYCLE, "assessed": CYCLE_DATE, "rubric_version": CRITERIA["version"], "tools": tools}


def score(capabilities):
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

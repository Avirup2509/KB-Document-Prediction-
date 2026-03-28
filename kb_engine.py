"""
KB Intelligence Engine
LangChain + Ollama (LLMA) backend for KB article prediction, SOP generation,
incident analysis, and troubleshooting guide creation.
"""

import requests
import json
from datetime import datetime

try:
    from langchain_ollama import OllamaLLM
    LANGCHAIN_AVAILABLE = True
except ImportError:
    try:
        from langchain_community.llms import Ollama
        LANGCHAIN_AVAILABLE = True
    except ImportError:
        LANGCHAIN_AVAILABLE = False


def check_ollama_status(base_url: str = "http://localhost:11434") -> dict:
    """Check if Ollama is running and list available models."""
    try:
        resp = requests.get(f"{base_url}/api/tags", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            models = [m["name"] for m in data.get("models", [])]
            return {"online": True, "models": models, "message": "Connected"}
        return {"online": False, "models": [], "message": f"HTTP {resp.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"online": False, "models": [], "message": "Ollama not reachable. Is it running?"}
    except Exception as e:
        return {"online": False, "models": [], "message": str(e)}


def _call_ollama_direct(base_url: str, model: str, prompt: str, temperature: float, max_tokens: int) -> str:
    """Direct Ollama API call fallback when LangChain is unavailable."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        }
    }
    try:
        resp = requests.post(f"{base_url}/api/generate", json=payload, timeout=120)
        if resp.status_code == 200:
            return resp.json().get("response", "")
        return f"[Error: HTTP {resp.status_code} from Ollama]"
    except Exception as e:
        return f"[Error calling Ollama: {str(e)}]"


class KBEngine:
    def __init__(self, ollama_url: str, model: str, temperature: float, max_tokens: int):
        self.base_url = ollama_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.llm = None
        self._init_llm()

    def _init_llm(self):
        if not LANGCHAIN_AVAILABLE:
            return
        try:
            try:
                from langchain_ollama import OllamaLLM
                self.llm = OllamaLLM(
                    base_url=self.base_url,
                    model=self.model,
                    temperature=self.temperature,
                    num_predict=self.max_tokens,
                )
            except ImportError:
                from langchain_community.llms import Ollama
                self.llm = Ollama(
                    base_url=self.base_url,
                    model=self.model,
                    temperature=self.temperature,
                    num_predict=self.max_tokens,
                )
        except Exception:
            self.llm = None

    def _run(self, prompt: str) -> str:
        """Run a prompt through LangChain or fall back to direct API."""
        if self.llm:
            try:
                return self.llm.invoke(prompt)
            except Exception:
                pass
        # Fallback to direct API
        return _call_ollama_direct(self.base_url, self.model, prompt, self.temperature, self.max_tokens)

    # ── Incident Analyzer ────────────────────────────────────
    def analyze_incident(self, title: str, description: str, severity: str,
                         environment: str, affected_system: str) -> dict:
        prompt = f"""You are an expert IT incident response manager and senior SRE. 
Analyze this incident thoroughly and provide structured output.

INCIDENT DETAILS:
- Title: {title}
- Severity: {severity}
- Environment: {environment}  
- Affected System: {affected_system}
- Description: {description}

Provide the following in your response, clearly labeled with these exact headers:

[SUGGESTED_OWNER]
Based on the incident type and affected system, who should own this? (e.g., "Database Team - DBA Lead", "Network Engineering", "Application Team - Backend", "SRE On-Call") Be specific.

[ESTIMATED_RESOLUTION_TIME]
Realistic time estimate (e.g., "2-4 hours", "30-60 minutes", "1-2 days")

[CONFIDENCE_SCORE]
Your confidence in this analysis (e.g., "87%")

[ANALYSIS]
## Root Cause Analysis
Provide likely root causes ranked by probability.

## Impact Assessment  
Business and technical impact analysis.

## Immediate Actions Required
What needs to happen in the next 15-30 minutes?

[RESOLUTION_STEPS]
## Step-by-Step Resolution Guide

Provide numbered, detailed steps to resolve this incident. Include:
- Verification commands/checks
- Rollback procedures if applicable  
- Escalation criteria
- Post-resolution validation

[KB_DRAFT]
## Knowledge Base Article Draft

**Article Title:** [Create appropriate title]
**Category:** [Appropriate category]
**Tags:** [Relevant tags]
**Severity:** {severity}
**Affected System:** {affected_system}

### Problem Statement
[Describe the problem clearly]

### Symptoms
[List observable symptoms]

### Root Cause
[Root cause explanation]

### Resolution Steps
[Detailed resolution steps]

### Prevention
[How to prevent recurrence]

### Related Articles
[Suggest related KB topics]

---
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Author: AI-KB-Engine*
"""
        raw = self._run(prompt)

        def extract_section(text, tag_start, tag_end=None):
            try:
                start = text.find(f"[{tag_start}]")
                if start == -1:
                    return "N/A"
                start += len(f"[{tag_start}]")
                if tag_end:
                    end = text.find(f"[{tag_end}]", start)
                    return text[start:end].strip() if end != -1 else text[start:].strip()
                # Find next section marker
                import re
                next_section = re.search(r'\[([A-Z_]+)\]', text[start:])
                if next_section:
                    return text[start:start + next_section.start()].strip()
                return text[start:].strip()
            except Exception:
                return "N/A"

        return {
            "suggested_owner": extract_section(raw, "SUGGESTED_OWNER", "ESTIMATED_RESOLUTION_TIME").split('\n')[0].strip(),
            "est_resolution": extract_section(raw, "ESTIMATED_RESOLUTION_TIME", "CONFIDENCE_SCORE").split('\n')[0].strip(),
            "confidence": extract_section(raw, "CONFIDENCE_SCORE", "ANALYSIS").split('\n')[0].strip(),
            "analysis": extract_section(raw, "ANALYSIS", "RESOLUTION_STEPS"),
            "resolution_steps": extract_section(raw, "RESOLUTION_STEPS", "KB_DRAFT"),
            "kb_draft": extract_section(raw, "KB_DRAFT"),
        }

    # ── KB Article Generator ─────────────────────────────────
    def generate_kb_article(self, topic: str, category: str, context: str,
                             audience: str, style: str) -> str:
        prompt = f"""You are a senior technical writer specializing in ITIL-compliant Knowledge Base articles.
Create a comprehensive, professional KB article.

PARAMETERS:
- Topic: {topic}
- Category: {category}
- Target Audience: {audience}
- Style: {style}
- Additional Context: {context or 'None provided'}

Generate a complete KB article using this structure:

# [Article Title]

**Document ID:** KB-{datetime.now().strftime('%Y%m%d')}-XXX
**Category:** {category}  
**Audience:** {audience}
**Status:** Draft
**Created:** {datetime.now().strftime('%Y-%m-%d')}
**Version:** 1.0

---

## Summary
[2-3 sentence executive summary of what this article covers]

## Overview
[Detailed overview of the topic, including context and why this is important]

## Prerequisites
- [List prerequisites, access requirements, or prior knowledge needed]

## Procedure / Steps
[Detailed step-by-step content matching the {style} format]

## Troubleshooting
[Common issues users might face while following this article]

## Frequently Asked Questions
[3-5 relevant FAQs]

## Related Articles
[5 related KB article suggestions with brief descriptions]

## Revision History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {datetime.now().strftime('%Y-%m-%d')} | AI-KB-Engine | Initial draft |

---
*Article generated by KB Intelligence Hub*
"""
        return self._run(prompt)

    # ── SOP Builder ──────────────────────────────────────────
    def generate_sop(self, process: str, department: str, frequency: str,
                     objective: str, pre_conditions: str, risk_level: str) -> str:
        prompt = f"""You are a senior ITIL process consultant and technical writer.
Create a comprehensive, enterprise-grade Standard Operating Procedure document.

PARAMETERS:
- Process: {process}
- Department: {department}
- Frequency: {frequency}
- Risk Level: {risk_level}
- Objective: {objective or 'Not specified'}
- Pre-conditions: {pre_conditions or 'None specified'}

Generate a complete SOP using this ITIL-aligned structure:

# STANDARD OPERATING PROCEDURE
# {process}

---
**Document Number:** SOP-{department[:3].upper()}-{datetime.now().strftime('%Y%m%d')}  
**Department:** {department}  
**Effective Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Review Date:** [12 months from effective date]  
**Version:** 1.0  
**Classification:** Internal  
**Risk Level:** {risk_level}  
**Frequency:** {frequency}

---

## 1. PURPOSE AND SCOPE
### 1.1 Purpose
[Detailed purpose statement]

### 1.2 Scope
[What this SOP covers and what it doesn't]

### 1.3 Objectives
[Measurable objectives for this procedure]

## 2. ROLES AND RESPONSIBILITIES
| Role | Responsibility | RACI |
|------|---------------|------|
[List all roles involved: Process Owner, Executor, Reviewer, Approver]

## 3. PREREQUISITES AND PRE-CONDITIONS
### 3.1 Required Access & Permissions
[List systems, credentials, VPN access needed]

### 3.2 Required Tools
[Software, hardware, documentation needed]

### 3.3 Pre-conditions
{pre_conditions or '[List conditions that must be met before starting]'}

## 4. PROCEDURE STEPS
[Detailed numbered steps with sub-steps]

### Step 1: [Name]
**Who:** [Role]  
**When:** [Timing]  
**Action:** [Detailed instructions]  
**Verification:** [How to verify step completion]  

[Continue for all steps...]

## 5. DECISION POINTS AND ESCALATION
[Flowchart-style text decision tree for key decision points]

## 6. ROLLBACK PROCEDURE
[If applicable - how to reverse this process safely]

## 7. RISK MANAGEMENT
### 7.1 Known Risks
[List risks associated with this process]

### 7.2 Mitigation Measures
[Risk mitigation for each identified risk]

## 8. COMPLIANCE AND AUDIT
[Compliance requirements, logging, evidence collection]

## 9. KPIs AND SUCCESS METRICS
[How to measure if this SOP is being followed effectively]

## 10. REFERENCES
[Related SOPs, KB articles, runbooks, vendor docs]

## 11. REVISION HISTORY
| Version | Date | Author | Approved By | Changes |
|---------|------|--------|-------------|---------|
| 1.0 | {datetime.now().strftime('%Y-%m-%d')} | AI-KB-Engine | Pending | Initial release |

---
*Generated by KB Intelligence Hub | ITIL v4 aligned*
"""
        return self._run(prompt)

    # ── Troubleshooting Guide ─────────────────────────────────
    def generate_troubleshooting_guide(self, issue_title: str, technology: str,
                                        environment: str, symptoms: str,
                                        already_tried: str, include_decision_tree: bool) -> str:
        dt_instruction = "Include a text-based decision tree/flowchart using ASCII art showing the diagnostic flow." if include_decision_tree else ""

        prompt = f"""You are a senior systems engineer and technical troubleshooting expert.
Create a comprehensive troubleshooting guide for this issue.

ISSUE DETAILS:
- Title: {issue_title or 'General Issue'}
- Technology: {technology}
- Environment: {environment}
- Symptoms: {symptoms or 'Not specified'}
- Already Tried: {already_tried or 'Nothing specified'}

{dt_instruction}

Generate a complete troubleshooting guide:

# TROUBLESHOOTING GUIDE: {issue_title or 'Issue Resolution Guide'}

**Technology:** {technology}  
**Environment:** {environment}  
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Complexity:** [Beginner/Intermediate/Advanced]

---

## 📋 Quick Reference
[30-second summary: most likely cause and first action to take]

## 🔍 Understanding the Problem
### Symptoms Checklist
[List of symptoms to confirm this is the right guide]

### Common Root Causes
[Ranked list of probable root causes with likelihood percentages]

{'## 🗺️ Decision Tree' if include_decision_tree else ''}
{'''[ASCII decision tree like:
START → Is service running?
  YES → Check connectivity...
  NO  → Restart service → Verify restart...]''' if include_decision_tree else ''}

## 🧪 Diagnostic Steps

### Phase 1: Initial Assessment (0-5 minutes)
[Quick checks to narrow down the problem]

### Phase 2: Deep Diagnostics (5-20 minutes)  
[Detailed diagnostic commands, log analysis, health checks]
Include actual commands where relevant for {technology}.

### Phase 3: Root Cause Confirmation
[How to confirm you've identified the correct root cause]

## 🔧 Resolution Procedures

### Scenario A: [Most Common Cause]
[Step-by-step fix]

### Scenario B: [Second Most Common Cause]
[Step-by-step fix]

### Scenario C: [Edge Case]
[Step-by-step fix]

## ✅ Validation & Testing
[How to confirm the issue is fully resolved]

## 🔄 Rollback Instructions
[How to undo changes if resolution causes new issues]

## 🚨 Escalation Criteria
[When to escalate and to whom - include contact guidance]

## 🛡️ Prevention Recommendations
[Monitoring, alerting, configuration changes to prevent recurrence]

## 📊 Useful Commands & Queries
[Cheat sheet of diagnostic commands for {technology}]

## 📚 Further Reading
[Links to vendor docs, related guides, KB articles]

---
*Troubleshooting Guide generated by KB Intelligence Hub*
"""
        return self._run(prompt)

    # ── KB Gap Predictor ──────────────────────────────────────
    def predict_kb_gaps(self, incident_volume: int, top_categories: list,
                         team_size: int, current_kb_count: int,
                         recurring_issues: str, horizon: str) -> dict:
        categories_str = ", ".join(top_categories) if top_categories else "General IT"

        prompt = f"""You are a Knowledge Management expert and ITSM consultant.
Analyze the following operational data and predict KB article gaps.

OPERATIONAL DATA:
- Weekly Incident Volume: {incident_volume}
- Top Incident Categories: {categories_str}
- Support Team Size: {team_size}
- Current KB Article Count: {current_kb_count}
- Prediction Horizon: {horizon}
- Recurring Issues: {recurring_issues or 'Not specified'}

PROVIDE THE FOLLOWING, using these exact markers:

[PREDICTED_GAPS_COUNT]
[Single number: how many KB gaps you've identified]

[PRIORITY_ARTICLES_COUNT]
[Single number: how many are high priority]

[IMPACT_SCORE]
[Score like "High" or "8.4/10"]

[ANALYSIS]
## KB Gap Analysis Report

### Executive Summary
[2-3 sentence summary of the KB health status]

### Identified Knowledge Gaps
For each gap, provide:
1. **[Gap Name]** - Priority: [High/Medium/Low]
   - Estimated incidents avoided per week: X
   - Target audience: [L1/L2/L3]
   - Complexity to create: [Low/Medium/High]
   - Recommended creation timeline: [Week 1 / Week 2-3 / Month 2]

[List 6-10 specific gaps based on the data]

### KB Coverage Analysis
[Analysis of current KB health vs. what's needed]

### Automation Opportunities
[Where AI/automation can help fill gaps faster]

### 90-Day KB Roadmap
[Phased plan for filling the gaps]

[ARTICLE_STUBS]
## Auto-Generated Article Stubs

For the top 3 priority KB gaps, provide article stubs:

### Article Stub 1: [Title]
**Priority:** High
**Category:** [Category]
**Summary:** [2-3 sentences describing what this article should cover]
**Key Sections to Include:**
- [Section 1]
- [Section 2]
- [Section 3]
**Estimated Time to Author:** [X hours]
**Expected Deflection Rate:** [X% of related incidents]

[Repeat for articles 2 and 3]
"""
        raw = self._run(prompt)

        def extract(text, tag):
            try:
                start = text.find(f"[{tag}]")
                if start == -1:
                    return "N/A"
                start += len(f"[{tag}]")
                import re
                next_sec = re.search(r'\[([A-Z_]+)\]', text[start:])
                if next_sec:
                    return text[start:start + next_sec.start()].strip()
                return text[start:].strip()
            except Exception:
                return "N/A"

        gaps = extract(raw, "PREDICTED_GAPS_COUNT")
        prio = extract(raw, "PRIORITY_ARTICLES_COUNT")
        impact = extract(raw, "IMPACT_SCORE")

        # Clean to single values
        gaps = gaps.split('\n')[0].strip()
        prio = prio.split('\n')[0].strip()
        impact = impact.split('\n')[0].strip()

        return {
            "predicted_gaps": gaps,
            "priority_articles": prio,
            "impact_score": impact,
            "analysis": extract(raw, "ANALYSIS"),
            "article_stubs": extract(raw, "ARTICLE_STUBS"),
        }

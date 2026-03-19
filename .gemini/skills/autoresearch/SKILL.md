---
name: autoresearch
description: Design, configure, and manage autonomous AI improvement loops for any codebase, product, or process. Triggers when the user wants to set up automated experimentation where an AI agent iteratively modifies code/prompts/configs, measures results against a metric, keeps improvements, and reverts failures. Use this skill for ANY request involving autonomous optimization, self-improving systems, automated A/B testing of prompts or code, overnight experiment loops, metric-driven iteration, or continuous improvement pipelines. Also triggers when the user mentions "autoresearch", "improvement loop", "autonomous experiments", "self-optimizing", or wants to improve a product/prompt/codebase against a measurable metric automatically. Covers the full lifecycle: discovery (guided setup via Socratic questioning), loop creation, management of multiple loops, and analysis of results.
---

# AutoResearch: Autonomous AI Improvement Loops

Design, configure, and manage loops where an AI agent autonomously modifies a target (code, prompts, configs), measures results, keeps what improves, and reverts what doesn't.

## Quick Orientation

An autoresearch loop has 6 components:

1. **Metric** — A number you can calculate automatically (conversion rate, accuracy, rubric score)
2. **Goal** — What direction the metric should move, and how far
3. **Modifiable Process** — The files/code the agent will change
4. **Instructions** — A `program.md` guiding what kinds of changes to try
5. **Loop** — The keep/revert automation that runs experiments repeatedly
6. **Executor** — The infrastructure that runs it all (n8n, cron, Claude Code, GitHub Actions)

There are two validation approaches:
- **Internal** — LLM grades output against a text rubric you define (instant, no real users needed)
- **External** — Real data from production systems, formula calculation, statistical comparison to baseline

## Three Modes

This skill operates in three modes. Determine which one the user needs:

### Mode 1: Discovery (Creating a new loop)
Use when the user says things like "I want to improve X", "set up autoresearch for Y", or "create an improvement loop for Z".

→ Read `references/discovery_guide.md`

### Mode 2: Management (Running and orchestrating loops)
Use when the user says things like "run my loops", "check loop status", "pause loop X", or "show me the dashboard".

→ Read `references/management_guide.md`

### Mode 3: Analysis (Learning from loop results)
Use when the user says things like "what worked?", "compare loop results", "show me what improved", or "analyze my experiments".

→ Read `references/analysis_guide.md`

---

## Discovery Mode: The Core Workflow

This is the most important mode. Most autoresearch setups fail because the metric is vague, the targets are wrong, or constraints are missing. Discovery mode prevents this through structured dialogue grounded in the actual codebase.

### Phase 1: Read the Project

Before asking any questions, read the project:

1. List the project directory structure (2 levels deep)
2. Identify key files: configs, prompts, source code, data schemas
3. Note integrations: APIs, databases, external services
4. Map dependencies: what connects to what

Present a brief summary to the user: "Here's what I see in your project..." This grounds the entire conversation in reality, not assumptions.

### Phase 2: Identify the Improvement Area

Ask: **"What part of this system do you want to improve?"**

If the user is vague ("make it better"), help them narrow down by presenting what you found in the project:
- "I see these potential areas: [list files/modules with brief descriptions]"
- "Which of these is underperforming or has the most room to grow?"

The user should leave this phase with a **specific area** identified (a module, a prompt file, a set of config rules, etc.)

### Phase 3: Define the Metric

This is the hardest and most important step. Ask these questions in sequence:

**Q1: "What does 'better' actually mean for this area?"**
Push for specificity. "More bookings" is better than "better responses". "15% conversion" is better than "more bookings".

**Q2: "Internal or external validation?"**
- **Internal**: You define a quality standard (rubric) and an LLM grades against it. Fast, no real users needed, good for early-stage or qualitative improvements.
- **External**: Measure real outcomes from production data. Slower (needs 24-48h observation windows), but ground truth.
- **Hybrid**: Internal first for fast iteration, then external to validate against reality.

Help the user choose:
- No real users yet → Internal
- Plenty of production data → External
- Want speed AND validation → Hybrid

**Q3 (Internal path): "What makes a PERFECT output?"**
Build a rubric together. For each criterion:
- Name it
- Describe what "good" looks like
- Assign a weight (how important is this relative to others?)
- Define the scoring scale

Example rubric structure:
```json
{
  "criteria": [
    {
      "name": "opener_hooks_attention",
      "description": "Opens with personalized insight or benefit, not generic greeting",
      "weight": 20,
      "scale": "0-10 where 10=compelling hook, 5=adequate, 0=generic"
    }
  ],
  "passing_score": 70,
  "max_score": 100
}
```

**Q3 (External path): "What behavior shows success?"**
- What action constitutes a "win"? (booking, payment, reply, click)
- Where is this data? (which database, API, system)
- What's the formula? (numerator / denominator)
- What's the current baseline? (last 30 days average)
- How long between action and measurable outcome? (the observation window)
- What sample size do you need for statistical confidence?

**Q4: "What would make you STOP or REVERT?"**
Define guardrails:
- Metric floor (if it drops below X, revert immediately)
- Error rate ceiling (if errors exceed Y%, stop)
- Any hard constraints (never do Z)

### Phase 4: Scope the Modifiable Targets

Based on the project analysis, present which files the agent could modify:

"For the area you picked, these files are candidates for modification:"
- List each file with a brief description
- Note which ones are safe to change vs. risky

Ask: **"Which of these should the agent be allowed to change? What's off-limits?"**

Document both explicitly:
- **CAN modify**: [list of files]
- **CANNOT modify**: [list of files with reason — e.g., "database schema: would corrupt data"]

### Phase 5: Write the Instructions (program.md)

Help the user articulate their hypothesis and strategy. Ask:

**"What's your first hypothesis about what will improve the metric?"**

Examples of good hypotheses:
- "Adding social proof to responses will increase conversion"
- "Shorter, more direct opening lines will improve engagement"
- "Adjusting classification thresholds will reduce false positives"

Then ask: **"What kinds of changes should the agent try? What should it avoid?"**

Generate `program.md` collaboratively:

```markdown
# AutoResearch Program: [Loop Name]

## Goal
[Specific metric target, e.g., "Increase conversion_rate from 10% to 13%"]

## Context
[Brief description of the system and what it does]

## What You Can Change
[List of modifiable files with notes on what's changeable within each]

## What You CANNOT Change
[Explicit list of protected files/logic with reasons]

## Hypothesis
[The user's starting hypothesis]

## Strategy
[Kinds of changes to try, ordered by priority]

## Constraints
- [Time budget per experiment]
- [Revert threshold]
- [Any other guardrails]

## Evaluation
[How to measure: rubric criteria OR external metric formula]
```

### Phase 6: Configure the Loop

Ask about execution details:

**"How long should each experiment run?"**
- For code: compile + run + measure time
- For prompts: generation time × number of test cases
- Recommend 5-minute default, adjust based on system

**"How many experiments do you want to run?"**
- Overnight: ~50-100 (at ~12/hour)
- Quick test: 5-10
- Extended: 200+

**"Where should this run?"**
- n8n workflow (best for Cloud9 integration)
- Claude Code (simplest for prompt/skill improvement)
- GitHub Actions (best for code repos)
- Cron job (basic, reliable)

### Phase 7: Generate Loop Artifacts

After discovery is complete, generate all files:

```
autoresearch_loops/
├── registry.json                    # All loops index
├── shared.py                        # Shared infrastructure
├── loops/
│   └── [loop_name]/                 # e.g. understanding/, response/
│       ├── config.json              # Full configuration
│       ├── program.md               # Agent instructions
│       ├── rubric.json              # (Internal only) Scoring criteria
│       ├── measurement.py           # Self-contained metric runner
│       ├── experiments.json         # Experiment log (starts empty)
│       └── README.md                # Documentation of this loop
├── data/
│   ├── fixtures/                    # Input test cases (*.json)
│   ├── gold/                        # Gold standard answers (*.md)
│   ├── gold-responses/              # Gold response fixtures (*.md)
│   └── prompts/                     # Evaluator and proposer prompts
├── scripts/
│   ├── ingest_feedback.py           # Record real-world reactions/conversions
│   └── gold_update.py               # Evolve gold fixtures from conversions
└── logs/
    ├── results.tsv                  # Understanding loop experiment log
    └── results-response.tsv         # Response loop experiment log
```

Update or create `autoresearch_loops/registry.json` to track all loops.

**Path note for new measurement.py files:** The measurement.py lives in `loops/[name]/`. To import `shared.py` from `autoresearch_loops/`, use:

```python
sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))
from shared import LOOPS_DIR, PROJECT_ROOT, ...
```

Path constants inside measurement.py use `LOOPS_DIR` (which points to `autoresearch_loops/`):

```python
FIXTURES_DIR = LOOPS_DIR / "data" / "fixtures"
GOLD_DIR     = LOOPS_DIR / "data" / "gold"
PROMPTS_DIR  = LOOPS_DIR / "data" / "prompts"
RESULTS_FILE = LOOPS_DIR / "logs" / "results.tsv"
```

### Phase 8: Launch Readiness Checklist

Before the user starts the loop, verify:

```
Launch Readiness:
☐ Metric is automated (no human judgment during loop)
☐ Modifiable targets identified and documented
☐ Off-limits files/logic documented
☐ Hypothesis stated clearly
☐ Time budget per experiment is realistic
☐ Revert threshold defined
☐ program.md reviewed and approved by user
☐ (Internal) Rubric reviewed and weights confirmed
☐ (External) Data source accessible and formula validated
☐ Test run completed successfully
```

Run a single test iteration to validate the setup before launching the full loop.

---

## File Structures

### config.json Schema

```json
{
  "loop_id": "loop_001_inquiry_response",
  "name": "Inquiry Response Conversion",
  "created": "2026-03-18T14:00:00Z",
  "status": "active",
  
  "metric": {
    "type": "internal | external | hybrid",
    "direction": "higher_better | lower_better",
    "baseline": null,
    "target": null,
    "revert_threshold": null
  },
  
  "internal_metric": {
    "rubric_file": "rubric.json",
    "evaluation_method": "llm_judge",
    "passing_score": 70
  },
  
  "external_metric": {
    "data_source": "description of where data comes from",
    "formula": "numerator / denominator",
    "observation_window_hours": 24,
    "min_sample_size": 50,
    "statistical_significance": 0.05
  },
  
  "targets": {
    "can_modify": ["path/to/file1.md", "path/to/config.json"],
    "cannot_modify": [
      {"path": "path/to/schema.sql", "reason": "would corrupt data"},
      {"path": "path/to/api_client.py", "reason": "would break integrations"}
    ]
  },
  
  "execution": {
    "time_budget_seconds": 300,
    "max_iterations": 100,
    "executor": "claude_code | n8n | github_actions | cron",
    "schedule": "nightly_10pm | continuous | manual"
  },
  
  "results": {
    "best_score": null,
    "total_iterations": 0,
    "improvements": 0,
    "last_run": null
  }
}
```

### registry.json Schema

```json
{
  "project": "project_name",
  "created": "2026-03-18",
  "loops": [],
  "summary": {
    "total_loops": 0,
    "active_loops": 0,
    "total_iterations": 0
  }
}
```

### experiments.json Entry Schema

```json
{
  "iteration": 1,
  "timestamp": "2026-03-18T22:05:00Z",
  "hypothesis": "Added social proof element to opening",
  "changes_made": "Modified line 15-20 of inquiry_response.md",
  "metric_value": 72.5,
  "previous_best": 70.0,
  "improvement": 2.5,
  "kept": true,
  "duration_seconds": 298,
  "notes": "Social proof mention improved rubric score on 'trust' criterion"
}
```

---

## Important Principles

### The Discovery Phase Is the Bottleneck
Most autoresearch setups fail because of bad setup, not bad loops. Spend 80% of the effort on discovery. A perfectly configured loop with a clear metric beats a sophisticated loop with a vague metric every time.

### Ask Hard Questions
During discovery, challenge the user's assumptions:
- "How do you know that metric actually correlates with success?"
- "What if your rubric doesn't match what real users care about?"
- "Is 5 minutes enough to get a meaningful signal?"
- "What happens if the agent changes X and breaks Y?"

### Ground Everything in the Actual Codebase
Read files. Count lines. Check APIs. Don't design in the abstract. The user's project has real constraints — discover them before creating the loop.

### Internal vs External Is a Spectrum
Internal autoresearch (rubric-based) is fast but could be wrong. External (real data) is slow but true. Hybrid is usually best: iterate fast internally, then validate externally. The gap between internal and external scores reveals where your quality intuitions don't match reality.

### One Loop Per Improvement Area
Don't try to optimize everything at once. Each loop targets one specific area with one metric. Multiple loops can run in parallel, but each is independent.

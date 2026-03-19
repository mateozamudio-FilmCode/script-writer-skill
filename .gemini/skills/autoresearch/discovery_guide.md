# Discovery Guide: Setting Up a New AutoResearch Loop

This guide walks through the interactive discovery process for creating a new autoresearch loop. The goal is to leave no ambiguity — every component should be concrete, validated, and documented before the loop runs.

## The Discovery Conversation Flow

### Step 1: Project Scan

Before engaging the user, scan the project:

```
Action: List project directory (2 levels deep)
Action: Identify file types (code, config, prompts, data, schemas)
Action: Note integrations (API clients, database connections, external services)
Action: Estimate complexity (how many moving parts?)
```

Present findings:
"I've looked through your project. Here's what I see:
- [N] source files in [language/format]
- Key modules: [list]
- Integrations: [list APIs/databases]
- Configuration: [list config files]
- Prompts/templates: [list if any]"

### Step 2: The "What Do You Want to Improve?" Conversation

This is where most people are too vague. Your job is to sharpen their thinking.

**If the user says something vague like "make it better":**

Push back with specifics from the codebase:
"'Better' could mean a lot of things. Looking at your system, I see these potential improvement areas:

1. **[Module A]** — could optimize for speed, accuracy, or quality
2. **[Module B]** — could improve output format, content, or consistency
3. **[Config C]** — could tune thresholds, parameters, or rules

Which of these is the biggest pain point right now?"

**If the user has a specific area:**

Validate it's actually improvable:
"You want to improve [X]. Let me check:
- Is [X] in a modifiable format? (text/code vs binary)
- Does [X] produce measurable output?
- Can [X] run independently for quick experiments?
- Are there dependencies that make [X] hard to change in isolation?"

### Step 3: The Metric Deep-Dive

This is the most critical conversation. Use this question sequence:

#### Question Chain for Internal Metrics (Rubric-based)

```
Q: "What does a PERFECT [output] look like?"
   → User describes ideal output
   
Q: "Break that down for me. What specific qualities make it perfect?"
   → User lists qualities (e.g., "clear", "persuasive", "follows framework")
   
Q: "For each quality, what's the difference between a 10/10 and a 5/10?"
   → User defines the scale
   
Q: "Which of these qualities matters MOST? If you could only optimize one, which?"
   → User reveals priorities
   
Q: "What's the MINIMUM acceptable quality? Below what score should we revert?"
   → User defines the floor
```

Build the rubric from their answers:

```json
{
  "criteria": [
    {
      "name": "[extracted from user's quality list]",
      "description": "[their definition of what 'good' looks like]",
      "weight": "[derived from their priority ranking]",
      "scale": "[derived from their 10 vs 5 distinction]",
      "minimum": "[derived from their floor]"
    }
  ],
  "passing_score": "[derived from minimum acceptable]",
  "evaluation_prompt": "[generated: instruction for LLM judge to score against this rubric]"
}
```

#### Question Chain for External Metrics (Real data)

```
Q: "What real-world outcome tells you this is working?"
   → User identifies the outcome (booking, sale, click, reply)

Q: "Where does that data live? Can we query it automatically?"
   → User identifies data source (database, API, analytics)

Q: "What's the formula? What's the numerator and denominator?"
   → User defines the calculation

Q: "What's the current number? Have you measured it recently?"
   → Establishes baseline

Q: "How long after [input] does the [outcome] happen?"
   → Determines observation window (critical for timing the loop)

Q: "How many [inputs] do you get per day/week?"
   → Determines sample size and how long experiments need to run

Q: "What's a realistic improvement target? And what's the floor?"
   → Sets target and revert threshold
```

Build the external config:

```json
{
  "metric_name": "[outcome name]",
  "data_source": {
    "type": "[database | api | file]",
    "connection": "[how to access it]",
    "query_or_endpoint": "[how to fetch the data]"
  },
  "formula": {
    "numerator": "[what counts as success]",
    "denominator": "[total opportunities]",
    "timeframe": "[rolling window]"
  },
  "baseline": {
    "value": "[current measurement]",
    "period": "[when it was measured]",
    "std_dev": "[if known]"
  },
  "observation_window_hours": "[time between action and measurable outcome]",
  "min_sample_size": "[for statistical confidence]",
  "target": "[improvement goal]",
  "revert_threshold": "[floor — revert if below this]"
}
```

#### Question Chain for Hybrid

```
Q: "Do you have real data, or are you building something new?"
   → Determines starting point

Q: "Would you like to iterate fast against a rubric first, then validate with real data?"
   → Usually yes

Q: "How will we know if your rubric actually matches what real users want?"
   → This is the key question — the gap between internal and external is the learning

Setup:
  Phase 1 config → Internal (rubric + LLM judge)
  Phase 2 config → External (real data + statistical test)
  Transition rule → "Move to Phase 2 when internal score plateaus or hits target"
```

### Step 4: Scoping Modifiable Targets

Present the files in the improvement area:

```
"For [area], I see these files:

SAFE TO MODIFY (text-based, produces measurable output):
  ✅ prompts/inquiry_response.md — the main prompt template
  ✅ config/classification_rules.json — classification thresholds
  ✅ templates/email_body.md — email response template

RISKY TO MODIFY (could break dependencies):
  ⚠️ src/api_client.py — connects to external APIs
  ⚠️ src/database.py — database queries

DO NOT MODIFY (would cause data corruption or system failure):
  🛑 migrations/ — database schema
  🛑 .env — credentials
  🛑 package.json — dependencies

Does this mapping look right? Any files I should move between categories?"
```

### Step 5: Writing program.md Together

Guide the user through writing instructions for the AI agent:

```
Q: "What's your FIRST hypothesis about what will improve the metric?"
   → Start narrow: test one idea at a time

Q: "What KINDS of changes should the agent try?"
   → Get a prioritized list

Q: "What should the agent NEVER do?"
   → Explicit constraints prevent disasters

Q: "Are there any patterns or frameworks the agent should follow?"
   → E.g., CLOSER framework, specific coding patterns, style guides
```

Generate `program.md` from their answers and present for review.

### Step 6: Execution Configuration

```
Q: "How long should each experiment take?"
   → Default: 5 minutes. Adjust based on system complexity.
   → For prompts: generation_time × test_cases
   → For code: compile + run + measure

Q: "How many experiments? Overnight (~50-100) or quick test (5-10)?"
   → Match to their urgency and data volume

Q: "Where should this run?"
   → n8n: best for webhook/API integrations
   → Claude Code: best for prompt/skill improvement
   → GitHub Actions: best for code repos
   → Cron: simplest, most reliable

Q: "When should it run? Continuously, nightly, on-demand?"
   → Match to their workflow
```

### Step 7: Generate All Artifacts

Create the loop folder and all files:

1. `config.json` — populated with all collected information
2. `program.md` — reviewed and approved by user
3. `rubric.json` — (internal only) scoring criteria
4. `measurement.py` — metric calculation script
5. `experiments.json` — empty array, ready for logging
6. `README.md` — documents the loop purpose, metric, and setup decisions
7. Update `registry.json` — register the new loop

### Step 8: Test Run

Always run one test iteration before launching:

```
"Let me run a single test to make sure everything works:

1. Agent reads program.md ✓
2. Agent proposes a change to [target file] ✓
3. Change is applied ✓
4. Metric is calculated: [score] ✓
5. Score compared to baseline: [better/worse] ✓
6. Change would be [kept/reverted] ✓

Everything looks good. Ready to launch the full loop?"
```

If the test fails, diagnose and fix before proceeding.

---

## Common Discovery Pitfalls

### Pitfall 1: "The metric is my gut feeling"
**Fix**: "If you can't compute it automatically, the loop can't run. Let's find something measurable that correlates with your gut feeling."

### Pitfall 2: "Change everything at once"
**Fix**: "If we change 5 things and the metric improves, we won't know which change helped. Let's start with one hypothesis and expand later."

### Pitfall 3: "My rubric is perfect"
**Fix**: "Your rubric reflects what you THINK matters. Real data might disagree. Let's plan to validate internally first, then check against external data."

### Pitfall 4: "5 minutes is plenty"
**Fix**: Run a timed test. "Your system actually takes 8 minutes to produce output. Let's set the budget to 10 minutes to be safe."

### Pitfall 5: "The agent can change anything"
**Fix**: "If the agent modifies your database schema, it could corrupt all your data. Let's draw clear boundaries."

### Pitfall 6: "I'll know it when I see it"
**Fix**: "That works for manual review, but the loop runs 100 times overnight. We need criteria the LLM can evaluate consistently. Let's make your 'I know it when I see it' explicit."

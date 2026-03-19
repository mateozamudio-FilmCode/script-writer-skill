# Analysis Guide: Learning from AutoResearch Results

This guide covers analyzing experiment results, extracting patterns, comparing loops, and generating actionable insights.

## Single Loop Analysis

### Experiment Timeline

Read `experiments.json` and compute:

```
Total iterations: [N]
Kept (improvements): [K] ([K/N]%)
Reverted: [N-K] ([1 - K/N]%)
Best score: [best]
Starting score: [baseline]
Total improvement: [best - baseline] ([percentage]%)
Average improvement per kept iteration: [avg]
Time to best score: [iteration number of best]
```

### Improvement Curve

Plot or describe the improvement trajectory:

```
Score over iterations:

Iteration  1: 70.0  ████████████████████
Iteration  5: 72.5  █████████████████████
Iteration 12: 78.0  ████████████████████████
Iteration 23: 82.0  ██████████████████████████
Iteration 31: 84.0  ███████████████████████████
Iteration 35: 85.0  ███████████████████████████
Iteration 47: 85.2  ███████████████████████████

Pattern: Rapid improvement (iter 1-23), then plateau (iter 23+)
Convergence: Yes, at iteration ~35
```

### What Worked vs What Didn't

Group experiments by whether they were kept:

**Kept changes (what improved the metric):**
```
Iter  5: "Added specific property details to opening" → +2.5
Iter 12: "Included social proof (review count)" → +5.5
Iter 23: "Shortened response to under 200 chars" → +4.0
Iter 31: "Added urgency via check-in date proximity" → +2.0
Iter 35: "Restructured to lead with benefit, not greeting" → +1.0
```

**Reverted changes (what hurt the metric):**
```
Iter  3: "Made tone more formal" → -1.2
Iter  8: "Added multiple property options" → -3.0
Iter 15: "Included pricing in first response" → -2.5
Iter 28: "Added emojis for friendliness" → -0.8
```

### Pattern Extraction

Look for recurring themes in kept vs reverted changes:

```
PATTERNS THAT HELP:
- Specificity (details, numbers, proof) → avg +3.0
- Brevity (shorter responses) → avg +2.5
- Urgency (time-based hooks) → avg +1.5

PATTERNS THAT HURT:
- Formality (corporate tone) → avg -1.5
- Information overload (too many options) → avg -2.0
- Premature pricing → avg -2.5

INSIGHT: Users want short, specific, urgent responses.
         They don't want formal, information-heavy messages.
```

## Multi-Loop Comparison

### Cross-Loop Pattern Analysis

When multiple loops target different areas of the same product:

```
Loop 1 (Inquiry Response): Social proof helps (+5.5), brevity helps (+4.0)
Loop 2 (Classification): Stricter thresholds help (+8.0), fewer categories help (+3.0)
Loop 3 (Email Templates): Personalization helps (+6.0), short subject lines help (+4.5)

CROSS-LOOP INSIGHT:
- "Less is more" pattern appears in ALL three loops
  - Shorter responses, fewer categories, shorter subjects
  - Hypothesis: Users are overwhelmed. Simplicity wins.
  
- "Specificity" helps in Loops 1 and 3 but wasn't tested in Loop 2
  - Recommendation: Create Loop 4 testing specific classification criteria
```

### Improvement ROI Comparison

```
Loop Name        | Iterations | Time   | Improvement | Effort/Point
-----------------|-----------|--------|-------------|-------------
Inquiry Response | 47        | 4.5h   | +3.0%       | 1.5h per 1%
Classification   | 23        | 2.3h   | +21.4%      | 0.1h per 1%
Email Templates  | 30        | 3.0h   | +4.5%       | 0.7h per 1%

INSIGHT: Classification had the highest ROI (fastest improvement per unit of effort).
         Consider: Are there other threshold/config optimizations with similar ROI?
```

## Internal vs External Gap Analysis

When a loop uses hybrid validation, compare internal and external scores:

```
Internal rubric says: 85/100 (excellent)
External data says:   10.5% conversion (barely improved from 10.0%)

GAP: +15 points on rubric but only +0.5% on conversion

Diagnosis:
- Rubric weights "framework adherence" at 30%
- But real users don't care about framework structure
- They care about: speed of response, relevance, trust signals

Rubric Calibration:
- Reduce "framework adherence" weight: 30% → 10%
- Increase "response speed" weight: 5% → 20%
- Add "personalization" criterion: 0% → 15%
- Rerun internal loop with calibrated rubric
```

This gap analysis is one of the most valuable outputs of hybrid autoresearch — it reveals where your quality intuitions diverge from reality.

## Generating Reports

### Loop Completion Report

When a loop completes or is archived, generate:

```markdown
# AutoResearch Report: [Loop Name]

## Summary
- Duration: [start] to [end] ([total hours])
- Iterations: [N] total, [K] improvements kept
- Metric: [baseline] → [final] ([improvement]%)
- Status: [completed/archived] — Reason: [why]

## Top Changes That Worked
1. [Change description] → +[improvement]
2. [Change description] → +[improvement]
3. [Change description] → +[improvement]

## Changes That Didn't Work
1. [Change description] → -[degradation]
2. [Change description] → -[degradation]

## Patterns Discovered
- [Pattern 1]: [description and evidence]
- [Pattern 2]: [description and evidence]

## Recommendations
- [What to try next based on findings]
- [What to avoid based on findings]
- [Suggested new loops based on learnings]

## Improvement Timeline
[Score chart or timeline showing progression]
```

### Portfolio Report

Across all loops:

```markdown
# AutoResearch Portfolio Report: [Project Name]

## Active Loops
[Table of active loops with status]

## Completed Loops
[Table of completed loops with final results]

## Key Learnings
[Cross-loop patterns and insights]

## Recommended Next Steps
[What loops to create next, based on analysis]

## Overall Impact
[Total improvement across all areas]
```

## When to Create New Loops

Analysis should surface opportunities for new loops:

1. **A pattern appears across multiple loops** → Test it as a dedicated hypothesis
2. **Internal/external gap is large** → Create a rubric calibration loop
3. **A loop converges quickly** → The area might benefit from a different angle
4. **An untested area shares characteristics with a successful loop** → Apply the winning pattern
5. **External data reveals a new bottleneck** → Target it with a new loop

## Statistical Significance for External Metrics

For external loops, determine if improvements are real or noise:

```
Baseline: mean = 10.0%, std_dev = 0.3%
Current measurement: 10.8%

Z-score = (10.8 - 10.0) / 0.3 = 2.67
P-value = 0.0038

Interpretation:
- Z > 1.96 → Significant at 95% confidence ✓
- Z > 2.58 → Significant at 99% confidence ✓

This improvement is real with 99%+ confidence.
```

For small sample sizes, use more conservative thresholds:
- N < 30: Use t-test instead of z-test
- N < 50: Require p < 0.01 (99% confidence)
- N < 100: Require p < 0.05 (95% confidence)
- N > 100: Standard thresholds apply

## Experiment Log Best Practices

Good experiment logs enable good analysis. Each entry should capture:

- **What changed** (not just "modified file X" but "increased urgency threshold from 3 to 5 days")
- **Why it was tried** (the hypothesis behind the change)
- **What happened** (metric value, improvement amount)
- **Whether it was kept** (and why — threshold, improvement, or manual decision)

Avoid: "Changed stuff" → "Modified classification threshold for Y1 category from 72h to 120h based on hypothesis that longer warm periods improve conversion"

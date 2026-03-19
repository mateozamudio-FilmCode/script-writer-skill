# Management Guide: Running and Orchestrating AutoResearch Loops

This guide covers managing the portfolio of autoresearch loops — running, pausing, monitoring, and orchestrating multiple loops.

## Loop Lifecycle

Each loop moves through these states:

```
created → ready → active → [paused] → completed → archived
                     ↑         |
                     └─────────┘
```

- **created**: Config exists but hasn't been validated
- **ready**: Test run passed, awaiting launch
- **active**: Running experiments
- **paused**: Temporarily stopped (user decision, error, or threshold hit)
- **completed**: Hit target or converged (no more improvement)
- **archived**: Stored for reference, no longer running

## Running a Loop

### Single Loop Execution

The core loop logic (pseudocode — adapt to the executor):

```
function run_loop(loop_id):
    config = load("autoresearch_loops/{loop_id}/config.json")
    program = load("autoresearch_loops/{loop_id}/program.md")
    experiments = load("autoresearch_loops/{loop_id}/experiments.json")
    best_score = config.results.best_score or config.metric.baseline
    
    for iteration in range(config.execution.max_iterations):
        # 1. Read current state of target files
        current_state = snapshot(config.targets.can_modify)
        
        # 2. Ask AI agent to propose a change
        change = agent.propose_change(
            program=program,
            targets=config.targets.can_modify,
            previous_experiments=experiments[-10:],  # Last 10 for context
            best_score=best_score,
            constraints=config.targets.cannot_modify
        )
        
        # 3. Apply the change
        apply(change)
        
        # 4. Measure the metric
        if config.metric.type == "internal":
            score = evaluate_with_rubric(config.internal_metric)
        elif config.metric.type == "external":
            score = evaluate_with_data(config.external_metric)
        elif config.metric.type == "hybrid":
            score = evaluate_hybrid(config)
        
        # 5. Keep or revert
        if is_better(score, best_score, config.metric.direction):
            best_score = score
            commit(change, f"Iteration {iteration}: {score}")
            kept = true
        else:
            revert(current_state)
            kept = false
        
        # 6. Check guardrails
        if score < config.metric.revert_threshold:
            revert(current_state)
            pause_loop(loop_id, reason="Below revert threshold")
            break
        
        # 7. Log
        experiments.append({
            iteration: iteration,
            timestamp: now(),
            hypothesis: change.description,
            changes_made: change.diff,
            metric_value: score,
            previous_best: best_score if not kept else score - change.improvement,
            improvement: score - (best_score if not kept else score - change.improvement),
            kept: kept,
            duration_seconds: elapsed,
            notes: change.notes
        })
        
        save(experiments, "autoresearch_loops/{loop_id}/experiments.json")
        update_registry(loop_id, best_score, iteration)
        
        # 8. Check convergence
        if is_converged(experiments[-20:]):
            complete_loop(loop_id, reason="Converged")
            break
    
    generate_report(loop_id)
```

### Convergence Detection

A loop has converged when improvement flattens:

```
function is_converged(recent_experiments):
    if len(recent_experiments) < 10:
        return false
    
    # Count improvements in last 10 iterations
    improvements = count(e for e in recent_experiments[-10:] if e.kept)
    
    # If fewer than 2 improvements in last 10 iterations, likely converged
    if improvements < 2:
        return true
    
    # If average improvement in last 10 is < 0.5% of current best
    avg_improvement = mean(e.improvement for e in recent_experiments[-10:] if e.kept)
    if avg_improvement < best_score * 0.005:
        return true
    
    return false
```

## Managing Multiple Loops

### Registry Operations

**List all loops:**
```
Read autoresearch_loops/registry.json
Display: name, status, metric, current_best, iterations, last_run
```

**Run specific loop:**
```
run_loop("loop_001_inquiry_response")
```

**Run all active loops:**
```
for loop in registry.loops where status == "active":
    run_loop(loop.loop_id)
```

**Pause a loop:**
```
Update status to "paused" in registry and config
Log reason: "User requested" | "Below threshold" | "Error"
```

**Resume a loop:**
```
Update status to "active"
Continue from last iteration number
```

**Archive a loop:**
```
Move loop folder to autoresearch_loops/archived/
Update registry
Preserve all experiments and results
```

### Scheduling Multiple Loops

When running multiple loops, stagger them to avoid resource conflicts:

```json
{
  "schedule": [
    {"loop_id": "loop_001", "start_time": "22:00", "estimated_duration": "4h"},
    {"loop_id": "loop_002", "start_time": "02:00", "estimated_duration": "3h"},
    {"loop_id": "loop_003", "start_time": "05:00", "estimated_duration": "2h"}
  ]
}
```

Consider:
- Don't run loops that modify the same files simultaneously
- Allocate more time to loops with larger potential improvement
- External metric loops may need longer observation windows between iterations

### Loop Interaction Rules

Loops that share files need special handling:

```
Loop 1 modifies: inquiry_response.md, classification_rules.json
Loop 2 modifies: classification_rules.json, follow_up_rules.json
                  ^^^^^^^^^^^^^^^^^^^^^^^^
                  SHARED FILE — conflict risk

Resolution options:
1. Run sequentially (Loop 1 finishes, then Loop 2 starts)
2. Split the shared file (each loop gets its own section)
3. Merge: combine into one loop that optimizes both areas
```

## Dashboard Data

The dashboard should display for each loop:

```
Loop Name | Status | Metric Type | Baseline → Current | Improvement | Iterations | Last Run
----------|--------|-------------|---------------------|-------------|------------|----------
Inquiry   | active | external    | 10.0% → 13.0%     | +3.0%       | 47         | 2h ago
Classify  | done   | internal    | 70 → 85            | +21.4%      | 23         | 1d ago
Email     | paused | external    | 15% → 15%          | +0.0%       | 5          | 3d ago
```

Portfolio summary:
- Total active loops
- Total iterations across all loops
- Average improvement
- Best performing loop
- Loops needing attention (paused, errored, stalled)

## Executor-Specific Guidance

### Claude Code
Best for: prompt/skill improvement, small codebases
- Agent reads program.md, modifies files directly
- Metric calculated inline (rubric = LLM call, external = API call)
- Git for version control and revert

### n8n Workflow
Best for: API integrations, scheduled execution, Cloud9 workflows
- Trigger: Schedule node (cron)
- Agent: HTTP Request to Claude API with program.md context
- Apply: Code node writes file changes
- Measure: HTTP Request to data source + Code node for formula
- Decide: IF node (better → keep, worse → revert)
- Log: PostgreSQL insert

### GitHub Actions
Best for: open source, code repos, CI/CD integration
- Trigger: schedule (cron) or workflow_dispatch
- Agent: API call to Claude
- Apply: git commit
- Measure: run test suite or benchmark script
- Decide: compare to previous benchmark
- Log: commit message + artifacts

### Cron Job
Best for: simple, reliable, self-hosted
- Shell script that calls Python
- Python handles agent, apply, measure, decide, log
- Simplest setup, hardest to debug

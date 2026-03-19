# AutoResearch Loop: Humor & Structure Optimization

## Purpose
This loop automatically iterates on the `mh-scriptwriter` agent instructions (`script-writer.md`) to improve the structural setup and flow of jokes, specifically tuning them to the "Operational Realist" tone (Hummiston Method).

## Core Files
- `config.json` - Settings, boundaries (what can/cannot be changed), and metric thresholds.
- `program.md` - Direct instructions to the agent running the experiments.
- `rubric.json` - Evaluation criteria that judges the script's output (max score 20, target 18).
- `experiments.json` - Log of each iteration, hypothesis, change, score, and whether it was kept or reverted.

## How it works
1. The AutoResearch Agent reads `program.md` and proposes a change to `.gemini/skills/mh-scriptwriter/resources/script-writer.md`.
2. The change is made.
3. The `mh-scriptwriter` skill generates a test script based on an established input.
4. An LLM judge grades the script using `rubric.json`.
5. If the total score improves or meets the baseline, the change is kept. If it drops, the change is reverted.
6. Process repeats for configured number of iterations (max 10).

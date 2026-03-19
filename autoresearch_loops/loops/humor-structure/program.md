# AutoResearch Program: Humor & Structure Optimization

## Goal
Increase the score of script outputs against the Operational Realist Rubric from baseline to at least 18 (Elite).

## Context
The "Operational Realist" brand requires a very specific integration of humor (the Hummiston Method) combined with strong operational math. Currently, scripts are failing on humor because of structural issues: the flow and setup within the logic of the script do not properly support the jokes. The jokes end up feeling like random interjections rather than load-bearing punchlines subverting serious situations.

## What You Can Change
- `.gemini/skills/mh-scriptwriter/resources/script-writer.md`  — You can adjust the rules, constraints, examples, or structuring guidelines for how the agent outlines and writes the script.

## What You CANNOT Change
- `.gemini/skills/mh-scriptwriter/resources/MARCUS-VOICE.md` — Brand constraints are locked.
- `.gemini/skills/mh-scriptwriter/resources/copywriting-eval-rubric.md` — Do not change the grading criteria.

## Hypothesis
Humour is not working due to structural issues with how jokes are set up within the logic of the script. Tweaking the `script-writer.md` instructions regarding structure, pacing, and serious setups will provide a better runway for the "Hummiston" humor to land naturally.

## Strategy
1. **Analyze:** Look at `script-writer.md`'s current logic flow and setup constraints.
2. **Modify Structure Rules:** Add explicit instructions requiring a high-stakes, purely logical setup *before* any self-deprecating or ironic humor is attempted.
3. **Pacing Rules:** Implement constraints that enforce the "Abrupt Snap" timing—making sure the joke ends quickly and pivots back to cold operational truths.
4. **Test & Evaluate:** Generate a sample script, grade it against `rubric.json`, and note the score.
5. **Keep/Revert:** If the score goes up, keep the edit to `script-writer.md`. If it drops, revert.

## Constraints
- **Time budget:** 5 minutes per experiment.
- **Revert threshold:** Revert immediately if the score drops below 14.
- Only change `script-writer.md`. Do not modify other files in the `resources` directory.

## Evaluation
Evaluation will be done automatically using `measurement.py` via an LLM judge evaluating the output script against `rubric.json`.

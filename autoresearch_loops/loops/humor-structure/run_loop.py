import os
import json
import time
from pathlib import Path
from datetime import datetime, timezone

# ---------------------------------------------------------
# LLM Integration (Requires API Key / Implementation)
# ---------------------------------------------------------
def call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    STUB: Replace with your actual Anthropic or OpenAI API call.
    Returns the text response from the LLM.
    """
    print("[LLM Stub] Calling LLM...")
    # NOTE: To use Claude, install anthropic (pip install anthropic)
    # import anthropic
    # client = anthropic.Anthropic()
    # response = client.messages.create(
    #     model="claude-3-5-sonnet-20241022",
    #     system=system_prompt,
    #     messages=[{"role": "user", "content": user_prompt}],
    #     max_tokens=4096
    # )
    # return response.content[0].text
    
    return "PLACEHOLDER_NEW_FILE_CONTENT"

def propose_change(program_text, target_content, rubric, previous_experiments, constraints):
    """Asks the AI to propose a change to the target files based on the loop rules."""
    system = "You are an AI optimization agent improving a target file."
    prompt = f"""
    Based on the following program:
    {program_text}
    
    Current Target File Content:
    {target_content}
    
    Constraints that MUST be followed:
    {json.dumps(constraints, indent=2)}
    
    Recent experiments:
    {json.dumps(previous_experiments, indent=2)}
    
    Propose a new modified version of the target file that improves the metric against the rubric.
    Return ONLY the raw new file content without markdown code blocks.
    """
    return call_llm(system, prompt)

def evaluate_with_rubric(rubric_data, script_writer_content):
    """
    Evaluates the current script writer instructions.
    1. Generates a mock video script using the new guidelines.
    2. Uses an LLM Judge to grade that generated script using the rubric.
    """
    print("[LLM Stub] Evaluating script with rubric...")
    
    # In a real setup, we provide a standard "outline" fixture to reliably benchmark
    system_gen = "You are the mh-scriptwriter production agent."
    generation_prompt = f"Using these rigorous instructions:\n{script_writer_content}\nWrite a 1-minute sample script targeting the 'Operational Realist' brand based on a generic scenario."
    # sample_script = call_llm(system_gen, generation_prompt)
    sample_script = "MOCK GENERATED SCRIPT"
    
    target_score = 18.0
    system_eval = "You are an expert script evaluator grading against a rubric."
    eval_prompt = f"""
    Evaluate this script:
    {sample_script}
    
    Against this exact rubric:
    {json.dumps(rubric_data, indent=2)}
    
    Provide your evaluation and standard deductions. Return ONLY a numerical score out of 20 as your very final output string.
    """
    # response = call_llm(system_eval, eval_prompt)
    response = str(target_score + 0.1) # Simulate incremental improvement
    
    try:
        # Extract the last floating point number from the evaluation response
        numbers = [float(s) for s in response.split() if s.replace('.','',1).isdigit()]
        if numbers:
            return round(numbers[-1], 2)
        return float(response.strip())
    except ValueError:
        return 0.0

# ---------------------------------------------------------
# Loop Management orchestration
# ---------------------------------------------------------
class LoopExecutor:
    def __init__(self, loop_dir: str, project_root: str):
        self.loop_dir = Path(loop_dir)
        self.project_root = Path(project_root)
        
        self.config_path = self.loop_dir / "config.json"
        self.program_path = self.loop_dir / "program.md"
        self.experiments_path = self.loop_dir / "experiments.json"
        
        # Determine paths handling Windows vs Posix cleanly
        self.config = self.load_json(self.config_path)
        self.experiments = self.load_json(self.experiments_path)
        self.program_text = self.program_path.read_text(encoding="utf-8")
        
        # metric schema: 'rubric_file' applies to internal_metric
        rubric_file_name = self.config.get("internal_metric", {}).get("rubric_file", "rubric.json")
        self.rubric_path = self.loop_dir / rubric_file_name
        self.rubric = self.load_json(self.rubric_path) if self.rubric_path.exists() else {}
        
        # Resolve target paths directly from project_root
        self.targets = [self.project_root / t for t in self.config["targets"]["can_modify"]]

    def load_json(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    def save_json(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def snapshot_targets(self):
        snapshot = {}
        for t in self.targets:
            snapshot[t] = t.read_text(encoding="utf-8")
        return snapshot

    def restore_snapshot(self, snapshot):
        for t, content in snapshot.items():
            t.write_text(content, encoding="utf-8")

    def run(self):
        print(f"Starting execution for loop: {self.config['name']}")
        max_iters = self.config["execution"]["max_iterations"]
        best_score = self.config["results"]["best_score"]
        if best_score is None:
            best_score = self.config["metric"]["baseline"] or 0.0

        for i in range(max_iters):
            iteration_number = self.config["results"]["total_iterations"] + 1
            print(f"\n--- Iteration {iteration_number} ---")
            
            start_time = time.time()
            snapshot = self.snapshot_targets()
            
            # 1. Read current state of targets
            target_content_str = "\n\n".join([f"--- {t.name} ---\n{t.read_text('utf-8')}" for t in self.targets])
            
            # 2. Ask agent to propose change
            print("Proposing change...")
            new_content = propose_change(
                self.program_text, 
                target_content_str, 
                self.rubric, 
                self.experiments[-10:], # Last 10 experiments for context
                self.config["targets"]["cannot_modify"]
            )
            
            # 3. Apply the proposed change
            print("Applying change to targets...")
            # Assigning back to targets (for simplicity, only supports 1 modifiable target correctly here, or writes the LLM block entirely)
            if self.targets:
                self.targets[0].write_text(new_content, encoding="utf-8")
            
            # 4. Measure the metric
            print("Evaluating changes against the rubric...")
            current_writer_content = self.targets[0].read_text(encoding="utf-8")
            score = evaluate_with_rubric(self.rubric, current_writer_content)
            print(f"Score achieved: {score} (Best was {best_score})")
            
            # 5. Keep or Revert decision
            direction = self.config["metric"]["direction"]
            kept = False
            improvement = 0.0
            
            if (direction == "higher_better" and score > best_score) or \
               (direction == "lower_better" and score < best_score):
                improvement = abs(score - best_score)
                best_score = score
                kept = True
                print("Change KEPT!")
            else:
                print("Change REVERTED.")
                self.restore_snapshot(snapshot)
                
            # 6. Check Guardrails
            revert_threshold = self.config["metric"].get("revert_threshold")
            if revert_threshold is not None:
                if (direction == "higher_better" and score < revert_threshold) or \
                   (direction == "lower_better" and score > revert_threshold):
                    print(f"SCORE DROPPED BELOW REVERT THRESHOLD ({revert_threshold})! Pausing loop.")
                    self.config["status"] = "paused"
                    self.restore_snapshot(snapshot)
                    break # Abort loop limits
                    
            # 7. Log to experiment history
            duration = int(time.time() - start_time)
            exp_entry = {
                "iteration": iteration_number,
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "hypothesis": "Automated hypothesis (Requires LLM structured output block)",
                "changes_made": "Automated diff (Requires LLM structured output block)",
                "metric_value": score,
                "previous_best": best_score if not kept else score - improvement,
                "improvement": improvement if kept else score - best_score,
                "kept": kept,
                "duration_seconds": duration,
                "notes": "Automated execution log."
            }
            self.experiments.append(exp_entry)
            self.save_json(self.experiments_path, self.experiments)
            
            # 8. Update configuration registry
            self.config["results"]["best_score"] = best_score
            self.config["results"]["total_iterations"] = iteration_number
            if kept:
                self.config["results"]["improvements"] += 1
            self.config["results"]["last_run"] = exp_entry["timestamp"]
            self.save_json(self.config_path, self.config)
            
        print("\nLoop execution cycle completed.")

if __name__ == "__main__":
    # Assumes run_loop.py lives directly inside autoresearch_loops/loops/humor-structure/
    loop_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(loop_dir, "../../../"))
    
    executor = LoopExecutor(loop_dir, project_root)
    executor.run()

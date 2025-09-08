# logsage/rca_template.py

def get_rca_prompt_template() -> str:
    """
    Root Cause Analysis Prompt Template for LogSage.
    
    This template incorporates prompt engineering techniques including:
    - Role-playing: Defines the LLM as a pipeline failure diagnosis assistant
    - Few-shot learning: Provides clear examples and format constraints
    - Output format constraints: Structured Diagnosis Process + Root Cause sections
    
    The template guides the LLM to focus on diagnostic reasoning using the 
    filtered critical error log blocks from the LogSage pipeline.
    
    Returns:
        str: Complete RCA prompt template with placeholders for log content
    """
    return """# Role: You are a pipeline failure diagnosis assistant. Your task is to identify the
root cause of pipeline failures based on execution logs and configuration info.

# Skills:
• Task Type Identification: Read config files to determine the task type (e.g.,
unit test, code scan). Output under Diagnosis Process → Task Type.
• Error Log Analysis: Read logs to identify up to 10 key error lines. Focus
on terminal and causal errors. Output as line range + conclusion. Do
NOT analyze normal/warning logs.
• Root Cause Inference: Use log and config analysis (don't mix unrelated
errors). List up to 3 likely causes with concrete names and detailed, objective
explanation. No fix suggestions.

# Output Format:
• Two parts: Diagnosis Process and Root Cause.
• For Diagnosis Process, include:
  – Task type: e.g., Run npm dependency installation
  – Error analysis: e.g., Lines 6–12: Unit test 'abc' failed
    due to result mismatch
  – Summarize causally related/similar errors in one line
  – When referencing too many lines, use only first 5 + etc.
• For Root Cause, format each cause as:
  [High Likelihood] Unit test `abc` failed due to ...
• Prefer one cause, max three. Use concrete info (test name, file, dep).

# Notes:
• Be concise and factual. Use "lines a, b, c–d" format when needed.
• Use inline code for log lines, code blocks for log content.
• No fix suggestions allowed.
• All results will be used for solution generation. Follow rules strictly.

# Constraints:
• DO NOT include normal/process/non-critical logs.
• DO NOT analyze similar/adjacent logs separately.
• DO NOT output more than 5 log line references without using etc.

---

# Log Analysis Task

Please analyze the following filtered log content to identify the root cause of the pipeline failure:

```
{filtered_logs}
```

Please provide your analysis following the exact output format specified above."""


def format_rca_prompt(filtered_logs: list[str]) -> str:
    """
    Format the RCA prompt template with actual filtered log content.
    
    Args:
        filtered_logs (list[str]): Pruned and filtered log lines from LogSage pipeline
        
    Returns:
        str: Complete RCA prompt ready for LLM input
        
    Example:
        logs = ["ERROR: Test failed", "FATAL: Build crashed"]
        prompt = format_rca_prompt(logs)
        # Returns formatted prompt with logs embedded
    """
    log_content = "\n".join(filtered_logs)
    return get_rca_prompt_template().format(filtered_logs=log_content)


def format_logs_with_line_numbers(filtered_logs: list[str]) -> str:
    """
    Format filtered logs with line numbers for better LLM analysis.
    
    Args:
        filtered_logs (list[str]): Pruned log lines from LogSage pipeline
        
    Returns:
        str: Log content with line numbers for easier reference in analysis
        
    Example:
        Input: ["ERROR: Connection failed", "FATAL: Process crashed"]
        Output: "1: ERROR: Connection failed\n2: FATAL: Process crashed"
    """
    return "\n".join(f"{i+1}: {line}" for i, line in enumerate(filtered_logs))


def create_rca_prompt_with_line_numbers(filtered_logs: list[str]) -> str:
    """
    Create complete RCA prompt with line-numbered log content.
    
    Combines the RCA template with filtered logs formatted with line numbers
    to facilitate precise error line referencing in the LLM's analysis.
    
    Args:
        filtered_logs (list[str]): Final pruned log lines from LogSage pipeline
        
    Returns:
        str: Complete RCA prompt with line-numbered logs ready for LLM analysis
    """
    numbered_logs = format_logs_with_line_numbers(filtered_logs)
    return get_rca_prompt_template().format(filtered_logs=numbered_logs)
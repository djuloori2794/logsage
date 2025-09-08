from logsage.config import KEYWORDS, LOG_TAIL_LINES

def read_log(path: str) -> list[str]:
    """
    Read log file into list of lines.
    
    Args:
        path (str): File path to the log file
            Example: "/path/to/build.log" or "logs/error.log"
    
    Returns:
        list[str]: List of all lines from the log file (including newline characters)
            Example: ["2024-01-01 INFO: Starting build\n", "2024-01-01 ERROR: Build failed\n"]
    
    Raises:
        FileNotFoundError: If the log file doesn't exist
        IOError: If there are issues reading the file
    """
    with open(path, "r") as f:
        return f.readlines()


def keyword_match(line: str) -> bool:
    """
    Check if a log line contains any error keyword from the configured list.
    
    Performs case-insensitive matching against predefined error keywords like
    "fatal", "error", "fail", "exception", "missing", etc.
    
    Args:
        line (str): Single log line to check
            Example: "2024-01-01 ERROR: Database connection failed"
    
    Returns:
        bool: True if line contains any error keyword, False otherwise
            Example: True for "ERROR: Failed to start" (contains "error")
                    False for "INFO: Process completed" (no error keywords)
    
    Keywords checked (from config.KEYWORDS):
        ["fatal", "fail", "panic", "error", "exit", "kill", "no such file", 
         "err:", "err!", "failures:", "err ", "missing", "exception", "cannot"]
    """
    return any(k.lower() in line.lower() for k in KEYWORDS)


def filter_log_lines(log_lines: list[str]) -> list[tuple[int, str]]:
    """
    Filter log lines to identify key error lines using multiple parallel strategies.
    
    Implements Algorithm 1 from the paper: Key Log Filtering Process.
    This is the first stage of the LogSage pipeline that extracts relevant error 
    log lines using keyword matching and log tail prioritization.
    
    Args:
        log_lines (list[str]): Full list of all log lines from the file
            Example: ["INFO: Starting build", "ERROR: Connection failed", "DEBUG: Retrying..."]
    
    Returns:
        list[tuple[int, str]]: Sorted list of (line_index, line_content) tuples for filtered lines
            Example: [(1, "ERROR: Connection failed"), (5, "FATAL: Process crashed"), (198, "Build failed")]
            - First element: 0-based line index in original log
            - Second element: Stripped line content (no leading/trailing whitespace)
    
    Filtering Strategies (Algorithm 1):
        1. Keyword Matching: Lines containing error keywords (fatal, error, fail, etc.)
        2. Log Tail Prioritization: Last LOG_TAIL_LINES=200 lines from the log
        3. Deduplication: Ensures each line appears only once in candidate pool
    
    Example:
        Input: 1000 lines total, last 200 lines + 15 error keyword matches
        Output: ~210 unique filtered lines (some overlap between tail and keywords)
    """
    tail = set(range(len(log_lines) - LOG_TAIL_LINES, len(log_lines)))
    candidate_pool = set()  # Use set to automatically handle deduplication

    for i, line in enumerate(log_lines):
        if keyword_match(line) or i in tail:
            candidate_pool.add((i, line.strip()))

    # Convert back to sorted list by line number (maintaining log order)
    filtered = sorted(list(candidate_pool), key=lambda x: x[0])
    return filtered


from logsage.config import KEYWORDS, LOG_TAIL_LINES

def read_log(path: str) -> list[str]:
    """Read log file into list of lines."""
    with open(path, "r") as f:
        return f.readlines()


def keyword_match(line: str) -> bool:
    """Check if a log line contains an error keyword."""
    return any(k.lower() in line.lower() for k in KEYWORDS)


def filter_log_lines(log_lines: list[str]) -> list[tuple[int, str]]:
    """
    Filter log lines using:
      - keyword matching
      - log tail prioritization
    Returns list of (line_number, line_content).
    """
    tail = set(range(len(log_lines) - LOG_TAIL_LINES, len(log_lines)))
    filtered = []

    for i, line in enumerate(log_lines):
        if keyword_match(line) or i in tail:
            filtered.append((i, line.strip()))

    return filtered


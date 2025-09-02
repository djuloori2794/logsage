# logsage/config.py

# ---------------------
# Log Filter Configs
# ---------------------
KEYWORDS = [
    "fatal", "fail", "panic", "error", "exit", "kill",
    "no such file", "err:", "err!", "failures:", "err ", "missing", "exception", "cannot"
]
LOG_TAIL_LINES = 200  # Number of lines from the end of logs to consider

# ---------------------
# Log Expand Configs
# ---------------------
EXPAND_BEFORE = 4      # Lines before a keyword hit to include
EXPAND_AFTER = 6       # Lines after a keyword hit to include

# ---------------------
# Weight Initialization
# ---------------------
ALPHA = 0.7  # max candidate-to-log ratio for high-confidence weights
BETA = 500  # max absolute size of candidate pool for high-confidence weights

# ---------------------
# Weight Enhancement
# ---------------------
FAILURE_PATTERNS = [r"--- FAIL:", r"Failures?:"]  # strong signals
SECTION_PATTERN = r"^\s*#"                         # headers or section markers
ENABLE_WEAK_BOOST = True                          # optional for all candidate lines
FAILURE_LINE_WEIGHT = 10   # Weight for lines like "--- FAIL:"
KEYWORD_BONUS = 2          # Bonus for curated keywords
GENERIC_BONUS = 1          # Generic reinforcement

# ---------------------
# Context Expansion
# ---------------------
NUM_LINES_BEFORE = 2
NUM_LINES_AFTER = 2

# Thresholds from the paper
WEIGHT_THRESHOLD_LOW = 1  # When filtering is weak, be lenient
WEIGHT_THRESHOLD_HIGH = 3  # When filtering is strong, be selective
WEIGHT_COUNT_THRESHOLD = 500  # γ: Used to decide if recall is sparse

# ---------------------
# Block Ranking
# ---------------------
TOKEN_LIMIT = 22000       # Final token limit for pruning

# logsage/config.py

# possible error logs in the ci
KEYWORDS = [
    "fatal", "fail", "panic", "error", "exit", "kill",
    "no such file", "err:", "err!", "failures:", "err ", "missing", "exception", "cannot"
]

LOG_TAIL_LINES = 200   # number of lines from the end to prioritize
EXPAND_BEFORE = 4      # lines before error to include
EXPAND_AFTER = 6       # lines after error to include

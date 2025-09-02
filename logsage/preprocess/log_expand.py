from logsage.config import EXPAND_BEFORE, EXPAND_AFTER

def expand_log_blocks(log_lines: list[str], key_line_nums: list[int]) -> list[str]:
    """
    Expand around key log lines to preserve context.
    Returns a list of unique expanded lines.
    """
    seen = set()
    expanded = []

    for idx in key_line_nums:
        start = max(0, idx - EXPAND_BEFORE)
        end = min(len(log_lines), idx + EXPAND_AFTER + 1)

        for i in range(start, end):
            if i not in seen:
                expanded.append(log_lines[i].strip())
                seen.add(i)

    return expanded

# LogSage

LogSage is an intelligent log preprocessing pipeline designed to extract the most relevant information from large log files for LLM analysis. It uses a multi-stage approach to identify, weight, and select the most important log sections while staying within token budget constraints.

## Overview

Large log files often contain thousands of lines, making them impractical for LLM analysis due to token limits. LogSage solves this by intelligently pruning logs to their most critical sections, preserving context around failures and important events.

## Features

- **Smart Filtering**: Identifies relevant log sections using keyword matching and tail analysis
- **Weight-Based Selection**: Assigns importance scores to log lines based on failure patterns and keywords
- **Context Preservation**: Maintains surrounding context for high-importance lines
- **Token Budget Management**: Ensures final output stays within configurable token limits (default: 22,000 tokens)
- **Failure Detection**: Specialized patterns for detecting test failures, errors, and critical events

## Pipeline Stages

1. **Log Reading**: Loads raw log file
2. **Initial Filtering**: Filters lines based on keywords and tail extraction
3. **Weight Assignment**: Assigns initial importance weights to all lines
4. **Pattern Enhancement**: Boosts weights for failure patterns and keywords
5. **Context Expansion**: Expands blocks around high-weight lines to preserve context
6. **Block Ranking**: Ranks blocks by weight density
7. **Budget Selection**: Selects top blocks within token budget using greedy strategy

## Usage

```bash
python logsage/run_pipeline.py <path_to_log_file>
```

### Example

```bash
python logsage/run_pipeline.py /path/to/build.log
```

This will process the log file and output the most relevant sections to stdout.

## Configuration

Key parameters can be adjusted in `logsage/config.py`:

- `TOKEN_LIMIT`: Maximum tokens in final output (default: 22,000)
- `KEYWORDS`: Error keywords to search for
- `LOG_TAIL_LINES`: Lines from end of log to consider (default: 200)
- `EXPAND_BEFORE/AFTER`: Context lines around keyword hits
- `FAILURE_PATTERNS`: Regex patterns for failure detection

## Project Structure

```
logsage/
├── config.py              # Configuration parameters
├── run_pipeline.py         # Main pipeline orchestrator
└── core/
    ├── log_filter.py       # Initial log filtering
    ├── weight_init.py      # Weight assignment
    ├── weight_enhance.py   # Pattern-based weight enhancement
    ├── context_expand.py   # Context expansion around important lines
    ├── block_ranker.py     # Block ranking by density
    └── token_budget.py     # Token budget management
```

## Algorithm

LogSage implements a sophisticated weighting algorithm that:

1. Identifies candidate lines using keyword matching and log tail analysis
2. Assigns higher weights to lines containing failure patterns
3. Provides bonus weights for curated keywords
4. Expands context around high-weight lines to maintain readability
5. Uses greedy selection to maximize information density within token constraints

This approach ensures that the most critical information (errors, failures, exceptions) is preserved while maintaining enough context for effective LLM analysis.
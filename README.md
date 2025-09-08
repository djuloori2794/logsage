# LogSage

LogSage is an intelligent log preprocessing pipeline designed to extract the most relevant information from large log files for LLM analysis. It uses a multi-stage approach to identify, weight, and select the most important log sections while staying within token budget constraints.

## Overview

Large log files often contain thousands of lines, making them impractical for LLM analysis due to token limits. LogSage solves this by intelligently pruning logs to their most critical sections, preserving context around failures and important events.

## Features

- **Smart Filtering**: Identifies relevant log sections using keyword matching, tail analysis, and deduplication
- **Asymmetric Log Expansion**: Expands around key error lines (4 before, 6 after) to preserve critical context  
- **Weight-Based Selection**: Assigns importance scores using adaptive algorithms from research
- **Pattern Enhancement**: Emphasizes critical failures and error patterns with specialized weighting
- **Contextual Window Expansion**: Preserves semantic continuity around high-importance lines
- **Density-Based Ranking**: Prioritizes log blocks by information density for optimal selection
- **Token Budget Management**: Greedy selection within configurable token limits (default: 22,000 tokens)
- **RCA Template Integration**: Generates structured prompts for LLM-based root cause analysis

## Pipeline Stages

1. **Log Reading**: Loads raw log file
2. **Key Log Filtering**: Filters lines using keyword matching, tail analysis, and deduplication  
3. **Log Expansion**: Asymmetric expansion around key error lines (m=4, n=6) to preserve context
4. **Initial Weight Assignment**: Assigns importance weights using adaptive thresholds (α=0.7, β=500)
5. **Pattern-Based Weight Enhancement**: Boosts critical failures, section headers, and error patterns
6. **Contextual Window Expansion**: Adaptive threshold expansion (θ=1 or 3) around high-weight lines  
7. **Density-Based Block Ranking**: Ranks contiguous blocks by weight density using Equation 3
8. **Token Budget Selection**: Greedy selection within 22,000 token limit
9. **RCA Template Generation**: Creates structured prompts for LLM-based root cause analysis

## Usage

### Basic Usage - Raw Log Processing

```bash
python logsage/run_pipeline.py <path_to_log_file>
```

### RCA Template Generation - For LLM Analysis

```bash
python logsage/run_pipeline.py <path_to_log_file> --rca
```

### Examples

```bash
# Process build log and output pruned log lines
python logsage/run_pipeline.py /path/to/build.log

# Generate structured RCA prompt for LLM analysis
python logsage/run_pipeline.py /path/to/build.log --rca
```

**Output Modes:**
- **Raw mode**: Outputs filtered and ranked log lines for direct analysis
- **RCA mode**: Generates structured prompt template with role-playing instructions for LLM-based root cause analysis

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
├── rca_template.py         # RCA prompt template for LLM analysis
└── core/
    ├── log_filter.py       # Key log filtering with deduplication
    ├── log_expand.py       # Asymmetric log expansion around errors
    ├── weight_init.py      # Initial weight assignment (Equation 1)
    ├── weight_enhance.py   # Pattern-based weight enhancement  
    ├── context_expand.py   # Contextual window expansion (Equation 2)
    ├── block_ranker.py     # Density-based block ranking (Equation 3)
    └── token_budget.py     # Token budget management with greedy selection
```

## Algorithm

LogSage implements a research-based Token Overflow Pruning system with four key components:

### 1. Key Log Filtering & Expansion
- **Algorithm 1**: Multi-strategy filtering (keyword matching, tail prioritization, deduplication)
- **Asymmetric expansion**: m=4 lines before, n=6 lines after critical errors to capture context

### 2. Adaptive Weight Assignment (Equation 1)
- **High confidence**: Weight=3 when |I|/|L| ≤ α=0.7 and |I| ≤ β=500  
- **Standard confidence**: Weight=1 for candidate lines
- **No weight**: Weight=0 for non-candidates

### 3. Contextual Window Expansion (Equation 2)
- **Adaptive threshold**: θ=1 (broad) when max(W)=1 or sparse filtering, θ=3 (selective) otherwise
- **Context preservation**: Expands [i-4, i+6] around lines with weight ≥ θ

### 4. Density-Based Ranking & Selection (Equation 3)
- **Block density**: density(Bⱼ) = Σwᵢ/(eⱼ - sⱼ + 1) for contiguous blocks
- **Greedy selection**: Maximizes information within 22,000 token budget
- **RCA template**: Structured prompt generation for LLM-based root cause analysis

This approach ensures optimal information density while maintaining semantic continuity for effective LLM-based failure diagnosis.
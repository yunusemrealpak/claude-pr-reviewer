"""Review prompt templates for Claude Code CLI."""


def get_review_prompt(commit_summary: str, files_summary: str, diff_content: str) -> str:
    """
    Generate the review prompt for Flutter/Dart code.

    Args:
        commit_summary: Summary of commits in the PR
        files_summary: Summary of file changes
        diff_content: Raw diff content

    Returns:
        Complete prompt string for Claude
    """
    return f"""Review this Flutter/Dart pull request for code quality.

## Commits in PR:
{commit_summary}

## Changed Files:
{files_summary}

## Code Diff:
```diff
{diff_content}
```

## Review Criteria:

### 1. Flutter Best Practices
- Is widget composition correct?
- Are const constructors used?
- Is state management proper?

### 2. Clean Architecture Compliance
- Is layer separation (domain/data/presentation) correct?
- Is dependency injection properly implemented?
- Is repository pattern followed?

### 3. Cubit/BLoC Patterns
- Is state handling correct?
- Is event-driven architecture applied?
- Are states immutable?

### 4. Dart Conventions
- Is null safety properly used?
- Are effective_dart rules followed?
- Are naming conventions correct?

### 5. Performance
- Are there unnecessary rebuilds?
- Is there memory leak risk?
- Is async handling correct?

### 6. Security
- Is input validation done?
- Is there sensitive data exposure risk?

## Output Format:

Provide a structured review:
- **Overall Verdict**: APPROVED / CHANGES REQUESTED / COMMENT
- **Key Findings**: By severity (HIGH/MEDIUM/LOW)
- **File/Line Suggestions**: Specific suggestions if any
- **Summary Recommendation**: Brief overall assessment

Be constructive and specific. Focus on the most important issues."""


SYSTEM_PROMPT = """You are a senior Flutter/Dart code reviewer.

FOCUS AREAS:
- Clean Architecture compliance (domain/data/presentation layers)
- Cubit state management patterns
- Widget composition and performance
- Null safety and error handling
- Test coverage suggestions

SEVERITY LEVELS:
- CRITICAL: Must fix before merge
- HIGH: Should fix, potential bug
- MEDIUM: Recommended improvements
- LOW: Style/convention suggestions"""

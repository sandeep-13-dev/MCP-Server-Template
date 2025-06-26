"""
Example prompts for MCP Server Template.

This module demonstrates how to create MCP prompts that provide
structured prompt templates for LLM interactions.
"""

from fastmcp import FastMCP
from typing import Dict, Any, List, Optional

# Get the global FastMCP instance
mcp = FastMCP("MCP Server Template")


@mcp.prompt("code-review")
async def code_review_prompt(
    code: str,
    language: str = "python",
    focus_areas: Optional[List[str]] = None
) -> str:
    """
    Generate a prompt for code review.
    
    Args:
        code: The code to review
        language: Programming language
        focus_areas: Specific areas to focus on (e.g., performance, security)
        
    Returns:
        String containing the formatted prompt
    """
    focus_text = ""
    if focus_areas:
        focus_text = f"\nPlease pay special attention to: {', '.join(focus_areas)}"
    
    return f"""Please review the following {language} code and provide feedback:

```{language}
{code}
```

Review criteria:
- Code quality and readability
- Best practices adherence
- Potential bugs or issues
- Performance considerations
- Security concerns
- Documentation quality{focus_text}

Please provide:
1. Overall assessment
2. Specific issues found
3. Suggestions for improvement
4. Positive aspects of the code
"""


@mcp.prompt("data-analysis")
async def data_analysis_prompt(
    data_description: str,
    analysis_goals: List[str],
    data_format: str = "CSV"
) -> str:
    """
    Generate a prompt for data analysis tasks.
    
    Args:
        data_description: Description of the dataset
        analysis_goals: List of analysis objectives
        data_format: Format of the data (CSV, JSON, etc.)
        
    Returns:
        String containing the formatted prompt
    """
    goals_text = "\n".join([f"- {goal}" for goal in analysis_goals])
    
    return f"""I have a {data_format} dataset with the following characteristics:

{data_description}

I want to perform the following analysis:
{goals_text}

Please provide:
1. A step-by-step analysis plan
2. Appropriate statistical methods to use
3. Python code examples for the analysis
4. Visualization suggestions
5. Potential insights to look for
6. Common pitfalls to avoid

Focus on actionable insights and clear, interpretable results.
"""


@mcp.prompt("api-documentation")
async def api_documentation_prompt(
    endpoint_name: str,
    method: str,
    parameters: Dict[str, Any],
    description: str
) -> str:
    """
    Generate a prompt for creating API documentation.
    
    Args:
        endpoint_name: Name/path of the API endpoint
        method: HTTP method (GET, POST, etc.)
        parameters: Dictionary of parameters and their descriptions
        description: Brief description of what the endpoint does
        
    Returns:
        String containing the formatted prompt
    """
    params_text = ""
    if parameters:
        params_text = "\n".join([f"- {name}: {desc}" for name, desc in parameters.items()])
    
    return f"""Please create comprehensive API documentation for the following endpoint:

**Endpoint:** {method} {endpoint_name}
**Description:** {description}

**Parameters:**
{params_text}

Please include:
1. Complete endpoint description
2. Request/response examples
3. Parameter validation rules
4. Error response formats
5. Usage examples in curl and Python
6. Rate limiting information (if applicable)
7. Authentication requirements (if any)

Format the documentation in a clear, developer-friendly manner with proper code examples.
"""


@mcp.prompt("bug-report")
async def bug_report_prompt(
    issue_description: str,
    steps_to_reproduce: List[str],
    expected_behavior: str,
    actual_behavior: str,
    environment_info: Optional[Dict[str, str]] = None
) -> str:
    """
    Generate a prompt for creating detailed bug reports.
    
    Args:
        issue_description: Brief description of the issue
        steps_to_reproduce: List of steps to reproduce the bug
        expected_behavior: What should happen
        actual_behavior: What actually happens
        environment_info: Environment details (OS, versions, etc.)
        
    Returns:
        String containing the formatted prompt
    """
    steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps_to_reproduce)])
    
    env_text = ""
    if environment_info:
        env_text = "\n**Environment:**\n" + "\n".join([f"- {k}: {v}" for k, v in environment_info.items()])
    
    return f"""Please help me create a comprehensive bug report for the following issue:

**Issue Description:**
{issue_description}

**Steps to Reproduce:**
{steps_text}

**Expected Behavior:**
{expected_behavior}

**Actual Behavior:**
{actual_behavior}{env_text}

Please provide:
1. A well-structured bug report
2. Additional information that might be helpful
3. Potential root causes
4. Suggested debugging steps
5. Workarounds (if any)
6. Priority level assessment

Format this as a professional bug report suitable for a development team.
"""


@mcp.prompt("feature-planning")
async def feature_planning_prompt(
    feature_name: str,
    feature_description: str,
    user_stories: List[str],
    constraints: Optional[List[str]] = None
) -> str:
    """
    Generate a prompt for feature planning and requirements gathering.
    
    Args:
        feature_name: Name of the feature
        feature_description: Detailed description
        user_stories: List of user stories
        constraints: Technical or business constraints
        
    Returns:
        String containing the formatted prompt
    """
    stories_text = "\n".join([f"- {story}" for story in user_stories])
    
    constraints_text = ""
    if constraints:
        constraints_text = "\n\n**Constraints:**\n" + "\n".join([f"- {constraint}" for constraint in constraints])
    
    return f"""Please help me plan the following feature:

**Feature Name:** {feature_name}

**Description:**
{feature_description}

**User Stories:**
{stories_text}{constraints_text}

Please provide:
1. Detailed requirements analysis
2. Technical architecture suggestions
3. Implementation phases/milestones
4. Potential risks and mitigation strategies
5. Testing strategy
6. Success metrics
7. Timeline estimation approach

Focus on creating a comprehensive plan that addresses both technical and business aspects.
"""


@mcp.prompt("refactoring-guide")
async def refactoring_guide_prompt(
    code_snippet: str,
    current_issues: List[str],
    refactoring_goals: List[str],
    language: str = "python"
) -> str:
    """
    Generate a prompt for code refactoring guidance.
    
    Args:
        code_snippet: Code that needs refactoring
        current_issues: List of current problems with the code
        refactoring_goals: List of goals for the refactoring
        language: Programming language
        
    Returns:
        String containing the formatted prompt
    """
    issues_text = "\n".join([f"- {issue}" for issue in current_issues])
    goals_text = "\n".join([f"- {goal}" for goal in refactoring_goals])
    
    return f"""Please help me refactor the following {language} code:

```{language}
{code_snippet}
```

**Current Issues:**
{issues_text}

**Refactoring Goals:**
{goals_text}

Please provide:
1. Step-by-step refactoring plan
2. Refactored code with explanations
3. Design patterns that could be applied
4. Testing strategy for the refactored code
5. Performance implications
6. Backward compatibility considerations

Focus on clean, maintainable code that follows best practices.
"""


# Export all prompts for the module loader
__all__ = [
    "code_review_prompt",
    "data_analysis_prompt",
    "api_documentation_prompt",
    "bug_report_prompt",
    "feature_planning_prompt",
    "refactoring_guide_prompt"
] 
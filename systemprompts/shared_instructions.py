"""
Shared system prompt instructions to reduce redundancy across tools
"""

# Common line number handling instructions
LINE_NUMBER_INSTRUCTIONS = """CRITICAL LINE NUMBER INSTRUCTIONS
Code is presented with line number markers "LINE│ code". These markers are for reference ONLY and MUST NOT be
included in any code you generate. Always reference specific line numbers in your replies in order to locate
exact positions if needed to point to exact locations. Include a very short code excerpt alongside for clarity.
Include context_start_text and context_end_text as backup references. Never include "LINE│" markers in generated code
snippets."""

# Common file request JSON format
FILES_REQUIRED_JSON_FORMAT = """IF MORE INFORMATION IS NEEDED
If you need additional context (e.g., related files, configuration, dependencies, test files) to provide meaningful
collaboration, you MUST respond ONLY with this JSON format (and nothing else). Do NOT ask for the same file you've been
provided unless for some reason its content is missing or incomplete:
{
  "status": "files_required_to_continue",
  "mandatory_instructions": "<your critical instructions for the agent>",
  "files_needed": ["[file name here]", "[or some folder/]"]
}"""

# Common overengineering warning
OVERENGINEERING_WARNING = """Remember: Overengineering is an anti-pattern — avoid suggesting solutions that introduce unnecessary abstraction,
indirection, or configuration in anticipation of complexity that does not yet exist, is not clearly justified by the
current scope, and may not arise in the foreseeable future."""

# Common grounding guidance
GROUNDING_GUIDANCE = """• Ground every suggestion in the project's current tech stack, languages, frameworks, and constraints.
• Recommend new technologies or patterns ONLY when they provide clearly superior outcomes with minimal added complexity.
• Avoid speculative, over-engineered, or unnecessarily abstract designs that exceed current project goals or needs.
• Keep proposals practical and directly actionable within the existing architecture."""

def build_prompt_with_common_sections(role_section: str, specific_guidelines: str, additional_sections: str = "") -> str:
    """
    Build a system prompt with common sections included.
    
    Args:
        role_section: Tool-specific role description
        specific_guidelines: Tool-specific guidelines and procedures
        additional_sections: Any additional tool-specific content
    
    Returns:
        Complete system prompt with common sections included
    """
    return f"""ROLE
{role_section}

{LINE_NUMBER_INSTRUCTIONS}

{FILES_REQUIRED_JSON_FORMAT}

{specific_guidelines}

{GROUNDING_GUIDANCE}

{OVERENGINEERING_WARNING}

{additional_sections}"""

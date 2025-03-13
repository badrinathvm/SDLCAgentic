from langchain.tools import tool
import re

# usage 
def clean_markdown(content: str) -> str:
        """
        Cleans and fixes common Markdown formatting issues.

        Args:
            content (str): The raw Markdown content to clean.

        Returns:
            str: The cleaned Markdown content.
        """
        def fix_heading_levels(content):
            lines = content.splitlines()
            updated_lines = []
            for line in lines:
                if line.strip().startswith("#"):
                    heading_level = line.count("#", 0, len(line))
                    line = re.sub(r"^#+", "#" * min(6, heading_level), line)
                updated_lines.append(line)
            return "\n".join(updated_lines)

        def add_blank_lines(content):
            content = re.sub(r"(\n#+ .+)", r"\1\n", content)
            content = re.sub(r"(\n[-*+] .+)", r"\1\n", content)
            return content

        def fix_nested_lists(content):
            lines = content.splitlines()
            updated_lines = []
            for line in lines:
                if line.startswith("  - ") or line.startswith("  * ") or line.startswith("  + "):
                    line = "    " + line.strip()
                updated_lines.append(line)
            return "\n".join(updated_lines)

        # Apply transformations
        content = fix_heading_levels(content)
        content = add_blank_lines(content)
        content = fix_nested_lists(content)
        return content


# Wrap the tool
# markdown_tool = Tool(
#     name="CleanMarkdown",
#     func=clean_markdown,
#     description="Cleans and fixes Markdown formatting issues."
# )

# cleaned_markdown = markdown_tool.run(markdown_content)
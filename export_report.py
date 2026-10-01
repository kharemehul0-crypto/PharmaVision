"""
Utility to export project_report.md into a styled, professional HTML report
ready for printing to PDF via any browser (Ctrl+P -> Save as PDF).
"""

import os
import re


def convert_markdown_to_html(md_text: str) -> str:
    """Converts basic markdown formatting into clean HTML tags."""
    # Escape basic HTML entities (except when already formatted)
    text = md_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Headers
    text = re.sub(r"^#### (.*?)$", r"<h4>\1</h4>", text, flags=re.MULTILINE)
    text = re.sub(r"^### (.*?)$", r"<h3>\1</h3>", text, flags=re.MULTILINE)
    text = re.sub(r"^## (.*?)$", r"<h2>\1</h2>", text, flags=re.MULTILINE)
    text = re.sub(r"^# (.*?)$", r"<h1>\1</h1>", text, flags=re.MULTILINE)

    # Images
    text = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<div style="text-align:center; margin:20px 0;"><img src="\2" alt="\1" style="max-width:100%; border:1px solid #ddd; border-radius:6px; box-shadow:0 2px 6px rgba(0,0,0,0.1);"><p style="font-size:0.88em; color:#586069; margin-top:6px;"><em>Figure: \1</em></p></div>', text)

    # Bold and italics
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", text)

    # Inline code
    text = re.sub(r"`(.*?)`", r"<code>\1</code>", text)

    # Horizontal rules
    text = re.sub(r"^---$", r"<hr>", text, flags=re.MULTILINE)

    # Convert tables
    lines = text.split("\n")
    in_table = False
    html_lines = []

    for line in lines:
        if line.strip().startswith("|") and line.strip().endswith("|"):
            cells = [c.strip() for c in line.strip()[1:-1].split("|")]
            if all(set(c).issubset({"-", ":"}) for c in cells):
                continue  # Skip separator line
            tag = "th" if not in_table else "td"
            if not in_table:
                html_lines.append('<div class="table-container"><table><thead><tr>')
                for c in cells:
                    html_lines.append(f"<{tag}>{c}</{tag}>")
                html_lines.append("</tr></thead><tbody>")
                in_table = True
            else:
                html_lines.append("<tr>")
                for c in cells:
                    html_lines.append(f"<{tag}>{c}</{tag}>")
                html_lines.append("</tr>")
        else:
            if in_table:
                html_lines.append("</tbody></table></div>")
                in_table = False

            # List items
            if line.strip().startswith("- "):
                html_lines.append(f"<li>{line.strip()[2:]}</li>")
            elif re.match(r"^\d+\.\s", line.strip()):
                content = re.sub(r"^\d+\.\s", "", line.strip())
                html_lines.append(f"<li>{content}</li>")
            elif line.strip().startswith("&lt;pre&gt;") or line.strip().startswith("```"):
                html_lines.append(f"<pre><code>")
            elif line.strip():
                if not line.startswith("<h") and not line.startswith("<hr"):
                    html_lines.append(f"<p>{line}</p>")
                else:
                    html_lines.append(line)
            else:
                html_lines.append("")

    if in_table:
        html_lines.append("</tbody></table></div>")

    return "\n".join(html_lines)


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    md_path = os.path.join(base_dir, "docs", "project_report.md")
    html_path = os.path.join(base_dir, "docs", "project_report.html")

    if not os.path.exists(md_path):
        print(f"[!] Report not found at: {md_path}")
        return

    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    body_html = convert_markdown_to_html(md_content)

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PharmaCount-CV: Project Report</title>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: #24292e;
    max-width: 900px;
    margin: 40px auto;
    padding: 0 20px;
    background-color: #fff;
  }}
  h1 {{ font-size: 2.2em; border-bottom: 2px solid #eaecef; padding-bottom: 0.3em; margin-top: 24px; color: #1a1f2c; }}
  h2 {{ font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; margin-top: 20px; color: #2c3e50; }}
  h3 {{ font-size: 1.25em; margin-top: 18px; color: #34495e; }}
  h4 {{ font-size: 1.05em; margin-top: 14px; color: #2980b9; }}
  p {{ margin: 10px 0; }}
  code {{ font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace; background: #f6f8fa; padding: 0.2em 0.4em; border-radius: 3px; font-size: 85%; }}
  pre {{ background: #f6f8fa; padding: 16px; border-radius: 6px; overflow-x: auto; font-size: 85%; }}
  pre code {{ background: none; padding: 0; }}
  .table-container {{ overflow-x: auto; margin: 16px 0; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 90%; }}
  th, td {{ border: 1px solid #dfe2e5; padding: 8px 12px; text-align: left; }}
  th {{ background-color: #f6f8fa; font-weight: 600; }}
  tr:nth-child(2n) {{ background-color: #fcfcfc; }}
  hr {{ height: 0.25em; padding: 0; margin: 24px 0; background-color: #e1e4e8; border: 0; }}
  li {{ margin: 4px 0; }}
  @media print {{
    body {{ max-width: 100%; margin: 20mm; font-size: 11pt; }}
    h1, h2, h3 {{ page-break-after: avoid; }}
    table, pre {{ page-break-inside: avoid; }}
  }}
</style>
</head>
<body>
{body_html}
</body>
</html>"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_template)

    print(f"[OK] Formatted HTML report generated successfully at: {html_path}")
    print("     You can open this in Chrome/Edge and press Ctrl+P -> 'Save as PDF' to generate your final PDF report.")


if __name__ == "__main__":
    main()

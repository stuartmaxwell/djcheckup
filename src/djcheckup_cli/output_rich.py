"""Use Rich to display output."""

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from djcheckup_cli.dataclasses import CheckResponse

console = Console()

MARKDOWN = """
# This is an h1

Rich can do a pretty *decent* job of rendering markdown.

1. This is a list item
2. This is another list item
"""


def rich_output(results: list[CheckResponse]) -> None:
    """Display results using Rich."""
    table = Table(title="DJCheckup Results Summary", show_lines=True)

    table.add_column("Check", justify="left")
    table.add_column("Result", justify="left")
    table.add_column("Message", justify="left")

    for result in results:
        table.add_row(result.name, result.result.value.capitalize(), Markdown(result.message))

    console.print(Panel(table))

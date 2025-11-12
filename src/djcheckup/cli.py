"""Command line interface."""

from typing import Annotated

import rich
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from djcheckup.check_defs import all_checks
from djcheckup.checks import SiteChecker
from djcheckup.outputs import rich_output, sitecheck_as_json

app = typer.Typer()


@app.command()
def run_checks(
    url: Annotated[str, typer.Argument(help="The URL to check.")],
    *,
    output_json: Annotated[
        bool,
        typer.Option(help="Prints the results in JSON format."),
    ] = False,
) -> None:
    """Run the DJ Checkup tool against a specific URL."""
    with Progress(
        SpinnerColumn(),
        TextColumn(f"[bold green]Checking {url}..."),
        console=Console(),
        transient=True,
    ) as progress:
        task = progress.add_task("checking")
        checker = SiteChecker(url=url)
        results = checker.run_checks(all_checks)
        progress.update(task, completed=True)

    if output_json:
        rich.print_json(sitecheck_as_json(results))
    else:
        rich_output(results)

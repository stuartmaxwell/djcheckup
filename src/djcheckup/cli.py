"""Command line interface."""

from typing import Annotated

import rich
import typer

from djcheckup.check_defs import all_checks
from djcheckup.checks import SiteChecker
from djcheckup.outputs import output_results_as_json, rich_output

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
    checker = SiteChecker(url=url)
    results = checker.run_checks(all_checks)

    if output_json:
        rich.print_json(output_results_as_json(results))
    else:
        rich_output(results)

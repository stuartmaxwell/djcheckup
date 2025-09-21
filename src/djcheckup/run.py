"""Command line interface."""

from typing import Annotated

import rich
import typer

from djcheckup.check_defs import all_checks
from djcheckup.checks import SiteChecker
from djcheckup.output_json import output_results_as_json
from djcheckup.output_rich import rich_output

app = typer.Typer()


@app.command()
def run_checks(
    url: str,
    *,
    output_json: Annotated[
        bool,
        typer.Option(help="Output results in JSON format."),
    ] = False,
) -> None:
    """Run all checks for a given URL."""
    checker = SiteChecker(url)
    results = checker.run_checks(all_checks)

    if output_json:
        rich.print_json(output_results_as_json(results))
    else:
        rich_output(results)


if __name__ == "__main__":
    app()

"""Command line interface."""

import typer

from djcheckup_cli.check_defs import all_checks
from djcheckup_cli.checks import SiteChecker
from djcheckup_cli.output_rich import rich_output

app = typer.Typer()


@app.command()
def run_checks(url: str) -> None:
    """Run all checks for a given URL."""
    checker = SiteChecker(url)
    results = checker.run_checks(all_checks)

    rich_output(results)


if __name__ == "__main__":
    app()

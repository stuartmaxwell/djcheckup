"""Nox file."""

import nox


@nox.session(python=["3.11", "3.12", "3.13", "3.14", "3.15"])
def test(session: nox.Session) -> None:
    """Run the test suite."""
    session.install("-e", ".", "--group", "dev")
    session.run("pytest")

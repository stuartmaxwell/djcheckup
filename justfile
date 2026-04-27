# Set the default recipe to list all available commands
@default:
    @just --list

# Synchronize the current working set with lock file
sync:
    pdm sync --clean

# Resolve and lock dependencies
lock:
    pdm lock --exclude-newer 7d

# Run the command line interface
@run *ARGS:
    pdm run djcheckup {{ ARGS }}

# Install pre-commit hooks
@pc-install:
    pdm run pre-commit install

# Upgrade pre-commit hooks
@pc-up:
    pre-commit autoupdate

# Run pre-commit hooks
@pc-run:
    pre-commit run --all-files

# Create a new GitHub release - this requires Python 3.11 or newer, and the GitHub CLI must be installed and configured
version := `echo "from tomllib import load; print(load(open('pyproject.toml', 'rb'))['project']['version'])" | pdm run --quiet`

[confirm("Are you sure you want to create a new release?\nThis will create a new GitHub release and will build and deploy a new version to PyPi.\nYou should have already updated the version number using one of the bump recipes.\nTo check the version number, run just version.\n\nCreate release?")]
@release:
    echo "Creating a new release for v{{version}}"
    git pull
    gh release create "v{{version}}" --generate-notes

@version:
    git pull
    echo {{version}}

# Run pytest
@test *ARGS:
    pdm run pytest {{ ARGS }}

# Run coverage
@cov:
    pdm run pytest --cov

# Run coverage
@cov-html:
    pdm run pytest --cov --cov-report=html --cov-context=test
    echo Coverage report: file://`pwd`/htmlcov/index.html

# Run nox
@nox:
    pdm run nox --session test

# Use uv to bump the patch version. Include `--dry-run` to see what would happen without actually bumping the version.
@bump *ARGS:
    uv version --bump patch {{ ARGS }}

# Use uv to bump the minor version. Include `--dry-run` to see what would happen without actually bumping the version.
@bump-minor *ARGS:
    uv version --bump minor {{ ARGS }}

# Use uv to bump the major version. Include `--dry-run` to see what would happen without actually bumping the version.
@bump-major *ARGS:
    uv version --bump major {{ ARGS }}

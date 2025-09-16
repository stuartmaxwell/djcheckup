# Set the default recipe to list all available commands
@default:
    @just --list

# Set the Python version
python_version := "3.13"

# Set the uv run command
uvr := "uv run"

#Set the uv command to run a tool
uvt := "uv tool run"

# Sync the package
@sync:
    uv sync

# Sync the package
@sync-up:
    uv sync --upgrade

# Build the package
@build:
    uv build

# Publish the package - this requires a $HOME/.pypirc file with your credentials
@publish:
      rm -rf ./dist/*
      uv build
      uv tool run twine check dist/*
      uv tool run twine upload dist/*

# Upgrade pre-commit hooks
@pc-up:
    uv tool run pre-commit autoupdate

# Run pre-commit hooks
@pc-run:
    uv tool run pre-commit run --all-files

# Use BumpVer to increase the patch version number. Use just bump -d to view a dry-run.
@bump *ARGS:
    uv run bumpver update --patch {{ ARGS }}
    @just sync

# Use BumpVer to increase the minor version number. Use just bump -d to view a dry-run.
@bump-minor *ARGS:
    uv run bumpver update --minor {{ ARGS }}
    @just sync

@bump-major *ARGS:
    uv run bumpver update --major {{ ARGS }}
    @just sync
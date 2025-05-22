# MIP Installability Checker

Provides the ability to test the installability of a MicroPython package via `mip`, as well as some scripts that utilise this capability.

## Requirements

- Python 3.12
- `uv` (Python package manager)
- `gh` (GitHub CLI)
- `micropython` available on the system path

## Scripts

The scripts can be run via `uv run <SCRIPT_NAME>.py`

### check_input_file.py

This script takes an input file (`input.txt`) containing a list of repositories and checks if they are installable via `mip`. It will output the results to `output.txt`.

See `example.list.txt` for an example of the input file format.

### update_awesome_list.py

This script trawls the Awesome MicroPython list and checks if the not-yet-flagged repositories are installable via `mip`. Any repositories that are newly installable will have their badge added to the list in a change on the HowManyOliversAreThere fork, and a PR will be created against the original Awesome MicroPython list.

set quiet := true

# Default command: show the available workflows.
[private]
default: help

# List public project workflows.
help:
    @just --list

# Run the deterministic Python tests.
test:
    python3 -B -m unittest discover -s tests -p 'test_bridge.py'
    python3 -B -m unittest discover -s tests -p 'test_core.py'
    python3 -B -m unittest discover -s tests -p 'test_editor_data.py'

# Run optional browser tests (requires Python Playwright and Chromium).
test-browser:
    python3 -B tests/test_browser.py

# Create a minimal .ankiaddon archive in dist/.
build:
    python3 -B scripts/build_addon.py

# Run the available automated checks and package verification.
check: test build

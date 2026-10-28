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

# Build the importable base package for direct deck generators.
build-foundation:
    PYTHONPATH="/usr/local/share/anki/app_packages:{{justfile_directory()}}" /usr/local/share/anki/python/bin/python3.13 scripts/build_aic_foundation_package.py --output 'templates/aic-foundation/AIC Foundation.apkg'

# Verify that the foundation package imports with all AIC note types intact.
verify-foundation:
    PYTHONPATH="/usr/local/share/anki/app_packages:{{justfile_directory()}}" /usr/local/share/anki/python/bin/python3.13 scripts/verify_aic_foundation_package.py 'templates/aic-foundation/AIC Foundation.apkg'

# Run the available automated checks and package verification.
check: test build

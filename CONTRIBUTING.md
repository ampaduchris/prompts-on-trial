# Contributing

This repository is built by directing Claude Code against `docs/spec.md`. Issues that describe a spec gap, a check that passes a bad output, or a prompt that leaks a personal detail are welcome. Use synthetic text; never attach a real CV, profile or booking.

For a change: open an issue first. Pull requests need green CI and a test tagged with the requirement id it proves.

Set up: `uv sync --locked`, then `uv run pytest -q --tb=line`.

By contributing you agree that your contribution is licensed under the MIT licence.

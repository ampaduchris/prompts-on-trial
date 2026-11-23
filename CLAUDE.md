# prompts-on-trial: rules for an agent in this repo

- `docs/spec.md` is the sole authority. Prompts and drafts never override it. If the spec and a request disagree, stop and say so.
- Tag every test with `@pytest.mark.req("REQ-###")`. `scripts/trace.py` prints the matrix; strict mode fails CI on an untested MUST (see DEV-006 for when it turns on).
- No personal content. Every input, persona, employer and event is synthetic. The private prompt sources never enter this repository.
- CI never calls a model. No model key in any workflow. Judged checks run locally on the owner's key.
- Run tests from the lockfile: `uv sync --locked`, then `uv run pytest -q --tb=line`.
- One session, one pull request. Open it as a draft. Never merge or approve.
- Append one row to `docs/BUILD-LOG.md` per session. Log every departure from the spec in `docs/DEVIATIONS.md`.
- British English. Short declarative sentences. No em dashes.

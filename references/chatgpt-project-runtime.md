# ChatGPT Project Runtime

Read this only when running the skill from a ChatGPT Project where `scripts/` is not already present in the sandbox.

## Bootstrap

Canonical files:

- `https://raw.githubusercontent.com/jonosin/nzstudy-grounded-research-skill/main/scripts/sources.py`

Use ChatGPT's web retrieval to load the raw script text. The Python sandbox may not have outbound internet access, so do not depend on `requests`, `urllib`, `curl`, or `pip` inside Python to fetch it.

Use the code runner to save the retrieved script text unchanged to a local path such as:

`/mnt/data/nzstudy-grounded-research/sources.py`

Set a task-local ledger path, for example:

`/mnt/data/nzstudy-grounded-research/ledger.json`

Then use the commands from `SKILL.md` with the local script path and explicit `--ledger` value.

## Passing webpage evidence to Python

Web retrieval and Python are separate capabilities.

1. Retrieve and open the webpage with ChatGPT's web tool.
2. Capture the exact source passage plus enough surrounding page text to preserve context.
3. Use the code runner to write that retrieved text to a local `.txt` file.
4. Run `sources.py quote ... --from <page.txt>` against that file.

Do not ask Python itself to fetch the webpage.

## Runtime failure

If any of these are unavailable:

- web retrieval,
- Python/code execution,
- ability to save the retrieved source text locally,
- ability to execute `sources.py`,

continue only in `Verification mode: LLM-only`. Keep the same evidence-first structure, but do not claim deterministic verification.

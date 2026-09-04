# NZ Study Grounded Research Skill

Evidence-first research for NZ Study marketing content.

The skill wraps the grounded-citation pattern from NousResearch's Hermes Agent and adds an NZ Study claim-support gate. The goal is simple:

`search -> retrieve source -> save exact evidence -> verify evidence -> check claim support -> create content idea`

## ChatGPT Project setup

Add `PROJECT_SOURCE.md` to the Project sources.

On a research request, the router loads the public `SKILL.md`. If Python is available, it also bootstraps `scripts/sources.py` and verifies exact evidence before the result can be called deterministically verified.

Example prompt:

> Research Auckland Grammar School for useful marketing content angles. Only use facts that pass the grounded evidence process.

## Repository layout

```text
SKILL.md
PROJECT_SOURCE.md
scripts/
  sources.py
references/
  chatgpt-project-runtime.md
  source-policy.md
evals/
  evals.json
tests/
  smoke_test.py
LICENSE
THIRD_PARTY_NOTICES.md
```

## Reliability boundary

The Python verifier proves that an accepted evidence quote exists in the captured source text and that citation IDs/URLs are consistent.

The semantic support gate is still an LLM judgement. The skill reduces that risk by forcing the model to compare the proposed claim directly with accepted evidence and by banning stronger wording unless the evidence supports it.

## Credits

This project is inspired by and adapts the grounded-citation workflow of NousResearch's Hermes Agent, released under the MIT License. See `THIRD_PARTY_NOTICES.md`.

The skill structure and writing follow ideas from Anthropic's Skill Creator and Matt Pocock's Writing for Agents guidance: short routing metadata, progressive disclosure, deterministic work in scripts, single sources of truth, and checkable completion criteria.

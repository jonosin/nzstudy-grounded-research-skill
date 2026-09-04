# NZ Study Grounded Research Router

Use the `nzstudy-grounded-research` workflow for every request that researches a school, university, campus, programme, facility, ranking, destination, student-life fact, or other external fact that may become NZ Study marketing content.

Canonical public repository:
`https://github.com/jonosin/nzstudy-grounded-research-skill`

Before the first such research task in a chat:

1. Load the canonical `SKILL.md` from:
   `https://raw.githubusercontent.com/jonosin/nzstudy-grounded-research-skill/main/SKILL.md`
2. Follow that skill for the full task.
3. If deterministic verification is required and the scripts are not already available locally, load `references/chatgpt-project-runtime.md` from the same repository and bootstrap the verifier.

The key invariant is **evidence-first**: retrieve evidence, verify it, then write factual claims and content ideas.

If the Python/code runner is unavailable or its usage limit is exhausted, state `Verification mode: LLM-only`. Never label the result deterministically verified unless the verifier actually ran and passed.

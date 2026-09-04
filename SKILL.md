---
name: nzstudy-grounded-research
description: Evidence-first web research for NZ Study marketing. Use whenever the user asks to research a school, university, campus, programme, facility, ranking, location, student life, or any external fact that may become marketing content. Use it even if the user only asks for "content ideas" or "research this school". It verifies evidence before allowing factual claims.
compatibility: Requires web retrieval. Deterministic verification requires Python 3 or an equivalent code runner.
---

# NZ Study Grounded Research

Use an **evidence-first** process. Build claims from retrieved evidence. Do not write the marketing claim first and search for a citation later.

## Workflow

### 1. Start the evidence ledger

Use `scripts/sources.py` with one ledger for the research task.

```bash
python scripts/sources.py --ledger <ledger.json> reset
```

If this is a ChatGPT Project and the scripts are not local, read `references/chatgpt-project-runtime.md` and bootstrap them first.

**Done when:** a fresh ledger exists for this task.

### 2. Search for candidate sources

Search broadly enough to find useful marketing facts. Prefer sources in this order:

1. Official school or university pages for facilities, programmes, campus facts, fees, dates, and services.
2. Government, regulator, accreditation, or official statistics sources.
3. Reputable independent news, education, or ranking sources for reputation and comparison claims.
4. Blogs, forums, social posts, and search snippets only as leads.

Open the underlying page before using it as evidence. A search-result snippet is not final evidence.

When a claim depends on reputation, comparison, ranking, accreditation, or another source-strength decision, read `references/source-policy.md`.

Register each useful URL **when you retrieve it**, before drafting claims:

```bash
python scripts/sources.py --ledger <ledger.json> add <URL> --title "<title>"
```

**Done when:** every source that may support the final output has a stable ledger ID.

### 3. Capture exact evidence

Save the retrieved page text to a local evidence file. Copy an exact sentence or passage that supports the candidate fact.

Attach it:

```bash
python scripts/sources.py --ledger <ledger.json> quote <ID> \
  --text "<exact source wording>" --from <page.txt>
```

The command must succeed. A failed exact-match check means the evidence is not verified.

**Done when:** every factual claim you plan to use has at least one accepted evidence quote.

### 4. Run the support gate

For each candidate claim, compare only the claim and its accepted evidence.

Classify it as:

- `SUPPORTED`: the evidence directly supports the full claim.
- `PARTIAL`: the evidence supports only part of the claim or weaker wording.
- `UNSUPPORTED`: the evidence does not support it.
- `AMBIGUOUS`: the source wording is unclear or context is missing.

Use only `SUPPORTED` claims. Rewrite `PARTIAL` claims to the strongest wording the evidence directly supports, then check again.

Examples:

- Evidence: "The recreation centre includes a 25-metre indoor pool."
- Supported: "Students have access to a 25-metre indoor pool."
- Unsupported: "The school is famous for world-class swimming facilities."

Treat `known for`, `famous for`, `leading`, `best`, `world-class`, `top`, and similar reputation language as comparison claims. Require explicit independent evidence or an applicable ranking. An institution describing itself with these words is not enough by itself.

**Done when:** every final factual statement is `SUPPORTED` and no stronger than its evidence.

### 5. Create content opportunities

Generate marketing ideas only from the supported evidence set.

Use this compact structure:

```markdown
## <Content angle>
Verified fact: <conservative factual claim>
Evidence: "<exact accepted quote>"
Source: <page title> [<ledger id>]
Safe content wording: <marketing-ready wording that does not exceed the evidence>
```

If useful, add a short note about why the fact may be interesting to students. Keep that note clearly separate from the verified fact.

### 6. Verify before delivery

Write the final research output to a draft file. Cite source IDs inline as `[1]`, `[2]`, and so on. Generate the Sources block mechanically:

```bash
python scripts/sources.py --ledger <ledger.json> render --style evidence --replace-in <draft.md>
```

Then run:

```bash
python scripts/sources.py --ledger <ledger.json> verify <draft.md> --evidence
```

Deliver the result as **deterministically verified** only if the command exits successfully.

If Python or the script cannot run, state `Verification mode: LLM-only` near the top. Continue with evidence-first research, but do not call the result deterministically verified.

**Done when:** verification passes, or the limitation is disclosed as `LLM-only`.

## Research rules

- Use retrieved page content as the source of truth for external facts.
- Keep exact numbers, dates, names, rankings, and facility specifications identical to the source.
- Attribute disagreement instead of merging conflicting sources into one fact.
- If no reliable evidence supports a useful claim, report `No verified source found`.
- Keep evidence and interpretation separate. The evidence card is factual. Marketing suggestions come after it.
- Do not turn existence into reputation. `Has X` does not mean `known for X`.
- Do not turn a school marketing statement into an independent comparison.
- Prefer one strong primary source over many weak copies for simple factual claims.
- For comparison, reputation, ranking, award, or disputed claims, seek an independent source.

## Completion criteria

The task is complete only when:

1. Every final external factual claim has a ledger source ID.
2. Every used source has at least one exact evidence quote accepted by the script.
3. Every final claim passes the support gate.
4. The final draft passes `verify --evidence`, or the output is explicitly marked `Verification mode: LLM-only`.
5. Each content suggestion is derived from a verified fact, not the reverse.

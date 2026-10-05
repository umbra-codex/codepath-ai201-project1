"""
Decide whether each run met the acceptance criteria in criteria.md.

Two ways in:

    python run_eval.py --label before     run_eval finds `judge` below and
                                          marks each question pass or fail
    python scorer.py results/run_X.md     turns that run log into the
                                          one-row-per-criterion table the
                                          README asks for

`judge` passes a run only if it met every criterion that applies to it. The
table is where the criteria are counted separately, "n of 5" per run.

How each criterion is checked:

1. Retrieved chunk contains the answer. The question is marked `answerable` in
   questions.py AND its `expects` phrase appears in a retrieved chunk. A
   question the corpus can't answer fails this one, on purpose.
2. Every answer names a source. The answer mentions a retrieved file by name.
   A gate refusal names nothing, so it fails.
3. The gate stops out-of-corpus questions. The OUT_OF_SCOPE questions go
   through retrieval and the gate. Deterministic, so one number for all runs.
4. One topic per chunk. The same five chunks `python app.py chunks` shows,
   each checked for a single source and at most one THREAD header.
   Deterministic too.
5. No hallucinated answers. Applies when the retrieved chunks don't contain
   the answer. Passes if the answer says so instead of answering anyway.
   Counted out of however many runs it applied to.

Matching ignores case and whitespace, so "16 GB" still matches "16GB".

Criteria 1, 3 and 4 re-run retrieval rather than reading it from the log, since
the log keeps sources but not chunk text. Retrieval is deterministic, so that
gives the same chunks, as long as the index hasn't been rebuilt since the run.
The table warns if the retrieved sources don't match the log.
"""

import re
import sys
from pathlib import Path

import gate
import questions as qs

# Ways the model says the documents don't have it. Criterion 5 counts any of
# these as an honest "I don't know". Compared after `_squash`.
ADMISSIONS = [
    "don't have enough information",
    "do not have enough information",
    "no mention",
    "not mention",
    "does not cover",
    "do not cover",
    "don't cover",
    "doesn't cover",
    "not covered",
    "do not provide",
    "does not provide",
    "don't provide",
    "doesn't provide",
    "not specified",
]


def _squash(text: str) -> str:
    """Lowercase with all whitespace removed."""
    return "".join(text.lower().split())


def _item(question: str) -> dict:
    for item in qs.answered():
        if item["question"] == question:
            return item
    raise KeyError(f"not in questions.py: {question}")


def chunks_contain_answer(question: str, expects: str, results) -> bool:
    """Criterion 1."""
    if not _item(question).get("answerable") or not expects.strip():
        return False
    return any(_squash(expects) in _squash(r.text) for r in results)


def names_a_source(answer: str, results) -> bool:
    """Criterion 2."""
    if answer.strip() == gate.REFUSAL:
        return False
    return any(_squash(Path(r.source).stem) in _squash(answer) for r in results)


def admits_no_answer(answer: str) -> bool:
    """Criterion 5, for runs where the chunks don't hold the answer."""
    said = _squash(answer)
    return answer.strip() == gate.REFUSAL or any(_squash(p) in said for p in ADMISSIONS)


def judge(question: str, expects: str, answer: str, results) -> bool:
    """True if this run met every criterion that applies to it (1 or 5, and 2)."""
    if chunks_contain_answer(question, expects, results):
        grounded = True
    else:
        grounded = admits_no_answer(answer)
    return grounded and names_a_source(answer, results)


# ─── The criterion table ────────────────────────────────────────────────────


def _read_log(path: Path):
    """Pull the settings and every (question, run, sources, answer) out of a run log."""
    text = path.read_text(encoding="utf-8")
    settings = re.search(r"top-k: (\d+) · relevance cutoff: ([\d.]+)", text)
    corpus = re.search(r"Corpus: `([^`]+)` \(index variant `([^`]+)`\)", text)
    runs = re.findall(
        r"### (.+?) — run (\d+)\n\n.*?- Sources retrieved: (.*?)\n\n```\n(.*?)\n```",
        text,
        re.S,
    )
    return {
        "top_k": int(settings.group(1)),
        "threshold": float(settings.group(2)),
        "corpus": corpus.group(1),
        "variant": corpus.group(2),
        "runs": [(q, int(n), s, a) for q, n, s, a in runs],
    }


def _sample_chunks(corpus: str, n: int = 5):
    """The same spread-out sample `python app.py chunks` prints."""
    from chunker import split_documents
    from ingest import load_documents

    chunks = split_documents(load_documents(corpus))
    step = max(len(chunks) // n, 1)
    return chunks[::step][:n]


def one_topic(chunk) -> bool:
    """Criterion 4."""
    return chunk.text.count("THREAD:") <= 1


def criterion_table(path: Path) -> str:
    from store import search

    log = _read_log(path)
    top_k, corpus, variant = log["top_k"], log["corpus"], log["variant"]
    n_runs = max(run for _, run, _, _ in log["runs"])

    retrieved = {}
    warnings = []
    for question, _, sources, _ in log["runs"]:
        if question in retrieved:
            continue
        results = search(question, top_k=top_k, corpus=corpus, variant=variant)
        retrieved[question] = results
        now = ", ".join(sorted({r.source for r in results}))
        if now != sources:
            warnings.append(f"{question}: log retrieved [{sources}], now [{now}]")

    c1 = [0] * n_runs
    c2 = [0] * n_runs
    c5 = [0] * n_runs
    c5_applied = [0] * n_runs
    for question, run, _, answer in log["runs"]:
        results = retrieved[question]
        i = run - 1
        if chunks_contain_answer(question, _item(question)["expects"], results):
            c1[i] += 1
        else:
            c5_applied[i] += 1
            c5[i] += admits_no_answer(answer)
        c2[i] += names_a_source(answer, results)

    oos = getattr(qs, "OUT_OF_SCOPE", [])
    refused = sum(
        not gate.check(
            search(q, top_k=top_k, corpus=corpus, variant=variant), log["threshold"]
        ).passed
        for q in oos
    )
    sample = _sample_chunks(corpus)
    single = sum(one_topic(c) for c in sample)

    n_q = len(qs.answered())
    rows = [
        ("1. Retrieved chunk contains the answer", 4, n_q, [f"{c}/{n_q}" for c in c1], c1),
        ("2. Every answer names a source", n_q, n_q, [f"{c}/{n_q}" for c in c2], c2),
        ("3. Gate stops out-of-corpus questions", 4, len(oos),
         [f"{refused}/{len(oos)}"] * n_runs, [refused] * n_runs),
        ("4. One topic per chunk", 4, len(sample),
         [f"{single}/{len(sample)}"] * n_runs, [single] * n_runs),
    ]

    lines = [
        f"Scored from `{path}` by `scorer.py::criterion_table`.",
        "",
        "| Criterion | Target | " + " | ".join(f"Run {i}" for i in range(1, n_runs + 1)) + " | Verdict |",
        "|---|---|" + "|".join(["---"] * n_runs) + "|---|",
    ]
    for name, target, out_of, cells, counts in rows:
        verdict = "MET" if all(c >= target for c in counts) else "MISSED"
        lines.append(f"| {name} | {target} of {out_of} | {' | '.join(cells)} | {verdict} |")

    # Criterion 5 is "at least four of five tries" where the chunks lacked the
    # answer, so it's counted out of the runs it applied to, as a rate.
    cells = [f"{k}/{m}" if m else "n/a" for k, m in zip(c5, c5_applied)]
    met = all(m == 0 or k / m >= 4 / 5 for k, m in zip(c5, c5_applied))
    lines.append(
        f"| 5. No hallucinated answers | 4 of 5 tries | {' | '.join(cells)} | "
        f"{'MET' if met else 'MISSED'} |"
    )

    if warnings:
        lines += ["", "⚠️ Retrieval changed since this log was written, so criteria 1, 2 and 5"]
        lines += ["may not match what the run saw:", ""] + [f"- {w}" for w in warnings]
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python scorer.py results/run_<stamp>_<label>.md", file=sys.stderr)
        sys.exit(2)
    print(criterion_table(Path(sys.argv[1])))

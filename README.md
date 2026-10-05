# The Unofficial Guide

Name: Sean Humphreys
Corpus: `advice_threads`

# Stretch Features

I'm adding two stretch features: metadata filtering, so you can narrow a search
to specific threads by source, and conversation memory, so a follow-up question
in the same session can build on the last one.

---

# Unit 1

## What This Does

This system answers questions from `advice_threads`, a corpus of 23 student
forum threads about college life. Ask it how much RAM a CS laptop needs or
whether it's too late to change majors, and it answers from what students
wrote, naming the thread it used. When the threads don't cover a question, it
says so instead of guessing.

## Chunking Strategy

**Chunk Size:** 800
**Overlap:** 0

The `advice_threads` corpus is 23 forum threads, 320 to 796 characters
each: a question, then two to five replies. In Milestone 1, I noticed the
replies depend on each other. In the bike thread, reply 3 opens with "Both
true," which means nothing without replies 1 and 2.

So each thread stays whole. `CHUNK_SIZE=800` sits just above the longest
thread (796), which gives 23 chunks for 23 documents.

I use no `CHUNK_OVERLAP` because no thread gets cut. The starter's `800/120`
setting stepped forward 680 characters at a time, so three threads over
`680` got a second chunk holding only their tails, one of them two characters
long.

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** — source: thread_bike_commute.txt#0 `— produced by: chunker.py::split_documents`

```
THREAD: Is a bike worth it for a 20 minute walk commute?

--- reply 1 (14 votes) ---
Yeah. Cuts an 18 minute walk to about 6. The thing nobody mentions is storage — covered bike parking exists at three buildings and is full by 9am at all three.

--- reply 2 (9 votes) ---
Counterpoint, I sold mine. Between November and March the paths are either icy or salted and salt destroys a drivetrain in one season.

--- reply 3 (22 votes) ---
Both true. I keep a cheap bike for September to November and walk the rest of the year. Total cost was about $120 for the bike and I don't care what happens to it.

--- reply 4 (5 votes) ---
If you do get one, the campus does free registration and it's the only reason I got mine back after it was taken.
```

**Chunk 2** — source: thread_first_gen.txt#0 `— produced by: chunker.py::split_documents`

```
THREAD: Anything specific for first-generation students?

--- reply 1 (33 votes) ---
The advising office has a specific programme and it is genuinely good, but it is opt-in and badly publicised. Ask for it by name.

--- reply 2 (41 votes) ---
The thing I'd say: the unwritten rules are the hard part, not the coursework. Ask about the unwritten rules explicitly. People are happy to explain them and nobody volunteers them.

--- reply 3 (16 votes) ---
Emergency fund for textbooks and travel exists and is not means-tested beyond a short form.
```

**Chunk 3** — source: thread_laptop_specs.txt#0 `— produced by: chunker.py::split_documents`

```
THREAD: How much laptop do I actually need for CS courses?

--- reply 1 (31 votes) ---
Less than the recommended spec page says. 16GB of RAM is the one number worth paying for; everything else you'll never notice.

--- reply 2 (18 votes) ---
Adding: the lab machines exist and are better than anything you'll buy. For the heavy assignments people just use those.

--- reply 3 (12 votes) ---
I did two years on an 8GB machine and it was fine until the last project, at which point it very much wasn't. 16 is the answer.
```

**Chunk 4** — source: thread_office_hours_etiquette.txt#0 `— produced by: chunker.py::split_documents`

```
THREAD: Is it weird to go to office hours with no specific question?

--- reply 1 (44 votes) ---
No, and this is the single most common thing first years get wrong. 'I'm following the lectures but I don't feel like I understand the shape of it' is a completely normal thing to say.

--- reply 2 (29 votes) ---
They're usually empty. You are doing the instructor a favour by turning up.

--- reply 3 (18 votes) ---
If it helps, treat it as a standing appointment. Go every week for a month and it stops feeling like a thing.
```

**Chunk 5** — source: thread_professor_email.txt#0 `— produced by: chunker.py::split_documents`

```
THREAD: Do professors actually answer email?

--- reply 1 (21 votes) ---
Varies enormously. General rule I've found: if the syllabus states a response window, it's honoured. If it doesn't, assume 48 hours and don't panic before then.

--- reply 2 (33 votes) ---
Office hours are dramatically more effective than email for anything that takes more than two sentences to answer. They're also usually empty.

--- reply 3 (15 votes) ---
Empty office hours is the biggest unused resource here and I say that having wasted a year not going.

For each one, ask: could someone answer a question using only this,
without reading what came before or after?
```

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:** What is the CPU, and how much memory is within the laptop?

**Answer:** Based on the provided documents, there is no mention of the laptop's CPU. However, regarding memory, the documents suggest having 16GB of RAM (thread_laptop_specs.txt).

```
Sources retrieved: thread_laptop_specs.txt, thread_laundry_timing.txt, thread_printing.txt

1 model calls this session, 579 tokens (538 in, 41 out)

```

**My relevance cutoff:** 0.7, set as `THRESHOLD` in `config.py`.

The five questions about my corpus came back between 0.402 and 0.596. The five
out-of-scope ones came back between 0.828 and 0.952. Nothing landed in between,
which leaves a gap of 0.232. I put the cutoff at 0.7, near the middle of that
gap (0.712). The farthest in-corpus question clears it by 0.104 and the nearest
out-of-scope one misses it by 0.128. All ten distances are in the table below.

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

| Question                                                             | In corpus? | Best distance |
| -------------------------------------------------------------------- | ---------- | ------------- |
| What is the CPU, and how much memory is within the laptop?           | Yes        | 0.440         |
| When is the deadline to have my transfer credits accepted?           | Yes        | 0.480         |
| What are the most common regrets for first-year students?            | Yes        | 0.596         |
| Is it too late to change majors as a third- or fourth-year student?  | Yes        | 0.402         |
| What is the deadline for assignments before they're considered late? | Yes        | 0.413         |
| What is the capital of Mongolia?                                     | No         | 0.948         |
| How do I change the oil in a diesel engine?                          | No         | 0.930         |
| Who won the 1994 World Cup?                                          | No         | 0.952         |
| What is the recommended dosage of ibuprofen for a headache?          | No         | 0.828         |
| How do I write a for loop in Rust?                                   | No         | 0.8712        |

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1.** I asked Claude to give a summary of the documents in advice_threads so I
can think of questions for Milestone 2.

**2.** I asked Claude for a guide to create the split_documents function and had
it verify the logic and output when completed.

**Unit 2**

**3.** I asked Claude to turn my run logs into the tables and draft the unit 2
write-up here, one step at a time, and had a second model (DeepSeek, through
Hermes) review each step before I committed. Claude marked criterion 5 MET.
The review said that didn't hold up as written, so I revised the criterion in
criteria.md.

**4.** For the diagnosis I asked Claude to find the pattern in my misses. Its
first try called the stage "loading", miscounted my misses, and gave a pattern
that just restated criterion 1. The review caught all three. The pattern now
in Diagnoses came from the second try. After grading, the feedback said every
miss has to name a stage and say what that stage did, and "none of the five
stages broke" did neither. The diagnosis names loading again, and this time it
says what `load_documents` did with the 23 files.

**5.** Claude wrote the hybrid search. The review found that its check for
keyword matches did nothing, since BM25 gives common words a small score and
every chunk passed. Claude fixed it by dropping words that appear in more than
half the chunks.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion                              | Target | Run 1 | Run 2 | Run 3 | Verdict |
| -------------------------------------- | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer | 4 of 5 | 3/5   | 3/5   | 3/5   | MISSED  |
| 2. Every answer names a source         | 5 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 3. Gate stops out-of-corpus questions  | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 4. One topic per chunk                 | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 5. No hallucinated answers             | 4 of 5 | 2/2   | 2/2   | 2/2   | MET     |

Scored from `results/run_2026-09-30_1553_before.md` by `scorer.py::criterion_table`.

Criteria 3 and 4 are each measured in one deterministic pass, so the same
number goes in all three run columns.

Criterion 1 can't reach its target with this question set. Two of my five
questions (transfer-credit deadline, late-work deadline) ask for something the
corpus doesn't hold, so the most it can score is 3/5. It stays MISSED against
the 4-of-5 target I set in unit 1, and I diagnose it under Diagnoses.

Criterion 5 only applies when the retrieved chunks don't contain the answer,
which is those same two questions. Each run therefore has 2 tries, not 5, and
a cell of 2/2 can't be measured against "4 of 5" as the target is written.
Pooled across the three runs it is 6 of 6 tries, which is above a four-in-five
rate, so I marked it MET. Testing the target as written needs at least five
tries where the chunks lack the answer.
I revised criterion 5 in `criteria.md` for this reason, and its verdict below
is against the revision.

The question table in the results file shows `pass` on all 15 runs, which
measures something different. `scorer.py::judge` passes a run when it meets
criterion 1 or criterion 5, plus criterion 2. The table above counts each
criterion on its own, which is why criterion 1 reads 3/5.

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

### Real output

Everything below is run 1 from `results/run_2026-09-30_1553_before.md`, except
the chunk text for criteria 1 and 4. The results file keeps sources but not
chunk text, so those two were printed again with `app.py`. Retrieval is
deterministic and the distances match the log.

**Criterion 1. Retrieved chunk contains the answer**

Question: "Is it too late to change majors as a third- or fourth-year student?"
Expected phrase: `extra semester`.

Retrieval, produced by `store.py::search` (printed by `python app.py retrieve`).
The `Gate:` line comes from `gate.py::check`:

```
#   distance   source                           preview
----------------------------------------------------------------------------------------------------
1   0.4019     thread_changing_major.txt        THREAD: How hard is it to change major in second yea...
2   0.6000     thread_pass_fail.txt             THREAD: When should you actually use the pass/fail o...
3   0.6916     thread_first_year_regret.txt     THREAD: What do you wish you'd known in first year? ...

Gate: best distance 0.402 is under the 0.7 cutoff
```

The top chunk in full, produced by `chunker.py::split_documents` (printed by
`python app.py chunks --from-doc thread_changing_major.txt`):

```
======================================================================
Chunk 1  |  source: thread_changing_major.txt#0  |  produced by: chunker.py::split_documents
======================================================================
THREAD: How hard is it to change major in second year?

--- reply 1 (22 votes) ---
Administratively trivial — it's a form. The real question is whether the credits you've taken map onto the new requirements.

--- reply 2 (27 votes) ---
Depends enormously on the direction. Moving within the sciences is usually fine. Moving into a science from outside in your third year means an extra semester more often than not.

--- reply 3 (19 votes) ---
Talk to the department adviser for the major you want, not your current one. They know the exceptions.
```

**Criterion 2. Every answer names a source**

Same question, run 1. The answer text is produced by
`generate.py::answer_from_chunks`, called from `run_eval.py::run_once`, and
written to the results file by `run_eval.py::main`.

- Best distance: 0.4019 (passed the gate)
- Sources retrieved: thread_changing_major.txt, thread_first_year_regret.txt, thread_pass_fail.txt

```
Based on the provided documents, moving into a science from outside in your third year often means an extra semester, but the documents do not cover whether it is too late to change majors as a fourth-year student (*thread_changing_major.txt*).
```

**Criterion 3. Gate stops out-of-corpus questions**

Produced by `run_eval.py::check_out_of_scope`, cutoff 0.7. Refused 5 of 5.

| Out-of-scope question | Best distance | Gate |
|---|---|---|
| What is the capital of Mongolia? | 0.948 | refused |
| How do I change the oil in a diesel engine? | 0.930 | refused |
| Who won the 1994 World Cup? | 0.952 | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.828 | refused |
| How do I write a for loop in Rust? | 0.871 | refused |

**Criterion 4. One topic per chunk**

The five sampled chunks, produced by `chunker.py::split_documents` (printed by
`python app.py chunks`). Each has one source file and one `THREAD:` header.

```
23 chunks total. Showing 5, spread across the corpus.

======================================================================
Chunk 1  |  source: thread_bike_commute.txt#0  |  produced by: chunker.py::split_documents
======================================================================
THREAD: Is a bike worth it for a 20 minute walk commute?

--- reply 1 (14 votes) ---
Yeah. Cuts an 18 minute walk to about 6. The thing nobody mentions is storage — covered bike parking exists at three buildings and is full by 9am at all three.

--- reply 2 (9 votes) ---
Counterpoint, I sold mine. Between November and March the paths are either icy or salted and salt destroys a drivetrain in one season.

--- reply 3 (22 votes) ---
Both true. I keep a cheap bike for September to November and walk the rest of the year. Total cost was about $120 for the bike and I don't care what happens to it.

--- reply 4 (5 votes) ---
If you do get one, the campus does free registration and it's the only reason I got mine back after it was taken.

======================================================================
Chunk 2  |  source: thread_first_gen.txt#0  |  produced by: chunker.py::split_documents
======================================================================
THREAD: Anything specific for first-generation students?

--- reply 1 (33 votes) ---
The advising office has a specific programme and it is genuinely good, but it is opt-in and badly publicised. Ask for it by name.

--- reply 2 (41 votes) ---
The thing I'd say: the unwritten rules are the hard part, not the coursework. Ask about the unwritten rules explicitly. People are happy to explain them and nobody volunteers them.

--- reply 3 (16 votes) ---
Emergency fund for textbooks and travel exists and is not means-tested beyond a short form.

======================================================================
Chunk 3  |  source: thread_laptop_specs.txt#0  |  produced by: chunker.py::split_documents
======================================================================
THREAD: How much laptop do I actually need for CS courses?

--- reply 1 (31 votes) ---
Less than the recommended spec page says. 16GB of RAM is the one number worth paying for; everything else you'll never notice.

--- reply 2 (18 votes) ---
Adding: the lab machines exist and are better than anything you'll buy. For the heavy assignments people just use those.

--- reply 3 (12 votes) ---
I did two years on an 8GB machine and it was fine until the last project, at which point it very much wasn't. 16 is the answer.

======================================================================
Chunk 4  |  source: thread_office_hours_etiquette.txt#0  |  produced by: chunker.py::split_documents
======================================================================
THREAD: Is it weird to go to office hours with no specific question?

--- reply 1 (44 votes) ---
No, and this is the single most common thing first years get wrong. 'I'm following the lectures but I don't feel like I understand the shape of it' is a completely normal thing to say.

--- reply 2 (29 votes) ---
They're usually empty. You are doing the instructor a favour by turning up.

--- reply 3 (18 votes) ---
If it helps, treat it as a standing appointment. Go every week for a month and it stops feeling like a thing.

======================================================================
Chunk 5  |  source: thread_professor_email.txt#0  |  produced by: chunker.py::split_documents
======================================================================
THREAD: Do professors actually answer email?

--- reply 1 (21 votes) ---
Varies enormously. General rule I've found: if the syllabus states a response window, it's honoured. If it doesn't, assume 48 hours and don't panic before then.

--- reply 2 (33 votes) ---
Office hours are dramatically more effective than email for anything that takes more than two sentences to answer. They're also usually empty.

--- reply 3 (15 votes) ---
Empty office hours is the biggest unused resource here and I say that having wasted a year not going.
```

**Criterion 5. No hallucinated answers**

Question: "What is the deadline for assignments before they're considered late?"
The corpus has no late cutoff, so the right answer is to say so. Run 1. The
answer text is produced by `generate.py::answer_from_chunks`, called from
`run_eval.py::run_once`, and written to the results file by `run_eval.py::main`.

- Best distance: 0.4132 (passed the gate)
- Sources retrieved: thread_first_year_regret.txt, thread_group_project.txt, thread_late_work.txt

```
Based on the provided documents, there is no mention of a specific deadline for assignments before they're considered late, though they do mention deadlines regarding asking for extensions (thread_late_work.txt). Therefore, I do not have enough information to answer this question.
```

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| #   | Criterion                                        | Verdict | How I decided |
| --- | ------------------------------------------------ | ------- | ------------- |
| 1   | Retrieved chunks contain the answer              | MISSED  | 3/5 on every run against a target of 4. I counted a question only when the corpus can answer it and its expected phrase is in a retrieved chunk, and the transfer-credit and late-work questions ask for deadlines no thread gives. The laptop question got credit on `16GB` alone though no thread names a CPU, so counting only full answers gives 2/5. |
| 2   | Every answer names a source                      | MET     | All 15 answers mention the filename of at least one retrieved thread, inline or on a `Source:` line. I counted the two deadline questions too, because they cite the thread they checked while saying it has no deadline. |
| 3   | The relevance gate stops out-of-corpus questions | MET     | The gate refused all five `OUT_OF_SCOPE` questions in its one pass. The nearest was the ibuprofen question at 0.828 against a 0.7 cutoff, so none of them was close. |
| 4   | One topic per chunk                              | MET     | Each of the five sampled chunks comes from one file and has one `THREAD:` header, so none of them mixes two threads. That is 5/5 against a target of 4, and it was not close. |
| 5   | No hallucinated answers                          | MET (revised) | Closest of the five, and I revised it. The original could not be measured as written: it quotes a sentence no answer uses word for word, and only the two deadline questions apply, so a run has two tries where it asks for five. Against the revision in `criteria.md` (any wording that says the documents don't cover it, as a rate over the tries that apply) it is 2/2 on every run, and I read all six answers to check that none offers a deadline of its own. |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

Criterion 1 is my only miss, and it missed on the same two questions in all
three runs. Retrieval is deterministic, so that is one miss per question and
not six.

**"When is the deadline to have my transfer credits accepted?"** The stage is
loading, the only stage that decides which facts the pipeline has.
`ingest.py::load_documents` reads every `.txt` and `.md` file in one folder,
the one `AI201_CORPUS` names, and makes one `Document` per file. I pointed it
at `corpora/advice_threads/documents`, so it loaded 23 student threads and no
policy document. Its only check is a count: `python ingest.py` reports `23
documents, 12,490 characters`. It doesn't look at what the files say, so a
corpus without this deadline loads the same as one that has it, with no error.
The date was in none of the 23 files, so it was not in any chunk or vector,
and the later stages had nothing to find. `python app.py retrieve` ranks
`thread_transfer_credits.txt` first at 0.4800, whole, in one chunk. It is the
only thread that mentions transfer credits, and it is about whether they count
toward the major ("the department decides, not the registrar"). It never gives
a date. Generation said the documents had no such deadline, which was correct.
I asked for a fact that was never loaded, and I flagged it `answerable: False`
in `questions.py` for that reason, so criterion 1 could not pass it.

**"What is the deadline for assignments before they're considered late?"**
Loading again, by the same mechanism: `load_documents` read 23 files and the
cutoff is in none of them. `thread_late_work.txt` ranks first at 0.4132. It
covers what happens once work is late ("If it says 10% a day, it's 10% a day")
and says the rule comes from each instructor's syllabus, so there is no cutoff
in it to retrieve. The word "deadline" appears in three threads and none of
them says when one is.

**"What is the CPU, and how much memory is within the laptop?"** The scorer
counts this as a pass, and I count it as half a miss.
`thread_laptop_specs.txt` ranks first at 0.4404 and gives the memory ("16GB of
RAM is the one number worth paying for"). The missing half is a loading miss
too: `load_documents` read the same 23 files, and none of them names a CPU.
That same reply says of everything else "you'll never notice".

**The pattern:** The two full misses are one problem, and it sits at loading.
Both ask for an official
rule, a deadline that a department or an instructor sets, and both threads
answer by pointing at whoever sets it: "the department decides", "the syllabus
is accurate". The corpus is students talking about what happened to them. It
can answer the questions about regrets and changing majors from that
experience. It has no dates. The CPU half of the laptop question is a smaller
version of the same gap: I asked for a spec, and the thread only says what
mattered in practice.

Distance can't see this. The two unanswerable questions came back at 0.4132
and 0.4800, inside the range of the three the corpus can answer (0.4019,
0.4404 and 0.5956). A close distance means the topic matched. It says nothing
about whether the answer is in the chunk. Five questions is a small sample,
but the right thread already ranks first for all five, so I don't expect a
change to chunking or retrieval to turn these into passes. The only stage that
handled the gap was generation, which said the documents didn't have it.

**Were my targets set low?** I missed one. Of the four I met, three were
safe.

Criterion 4 could not have failed. The 23 threads run from 317 to 793
characters once loaded (320 to 796 bytes on disk, the figure in unit 1),
`CHUNK_SIZE` is 800, and `chunker.py` keeps a document whole when it fits, so
I got 23 chunks with one thread in each. To make it a test I'd check all 23
chunks instead of a sample of five, at a chunk size small enough to split
threads, and require that no chunk mixes two threads or cuts a reply in half.

Criterion 3 was safe too. My five out-of-scope questions are nowhere near the
corpus (the capital of Mongolia, a diesel oil change), and the nearest came
back at 0.828 against a 0.7 cutoff. I'd tighten the target from 4 of 5 to 5 of
5. The harder case is a campus question the corpus doesn't answer. My two
deadline questions are that case, and they passed the gate at 0.4132 and
0.4800, so the gate does nothing for them. Criterion 5 is the one that covers
them, and it rests on only two questions.

Criterion 2 is already at 5 of 5, so the number can't go up, but the check is
loose: an answer passes if it mentions any retrieved filename. I'd tighten it
to require the name of the top-ranked thread, which is the one the answer
should rest on.

## The Improvement

**What I changed:** Hybrid search. `store.py::search` now ranks every chunk
two ways, by meaning (cosine distance, as before) and by keyword match (BM25
from `rank-bm25`), and merges the two rankings with reciprocal rank fusion in
`store.py::_fuse`. The top three of the merged list come back. Each chunk
keeps its cosine distance and the gate's 0.7 cutoff is the same, but what the
gate sees can change: it compares the best distance among the three chunks
returned, and the merged top three can leave out the nearest chunk. That can
turn a pass into a refusal and never the reverse. `config.HYBRID` turns hybrid
search on, and `AI201_HYBRID=0` turns it off to reproduce the before run.
Nothing else changed: same chunks, same index, same prompt, same `top-k`.

**Why I picked it:** My diagnosis says the two deadline questions miss because
the corpus has no deadline, and hybrid search is the retrieval change most
likely to prove that wrong, since both questions contain the exact word
"deadline". My prediction before running it is that criterion 1 stays at 3/5.

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion                              | Target | Run 1 | Run 2 | Run 3 | Verdict |
| -------------------------------------- | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer | 4 of 5 | 3/5   | 3/5   | 3/5   | MISSED  |
| 2. Every answer names a source         | 5 of 5 | 4/5   | 4/5   | 5/5   | MISSED  |
| 3. Gate stops out-of-corpus questions  | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 4. One topic per chunk                 | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 5. No hallucinated answers             | 4 of 5 | 2/2   | 2/2   | 2/2   | MET     |

Scored from `results/run_2026-10-04_2248_after.md` by
`scorer.py::criterion_table`, hybrid search on. Criterion 5 is counted the
same way as in the before log, against the unit 2 revision in `criteria.md`.

**Before and after, side by side:**

| Criterion                              | Target | Before (runs 1, 2, 3) | After (runs 1, 2, 3) | Verdict       |
| -------------------------------------- | ------ | --------------------- | -------------------- | ------------- |
| 1. Retrieved chunk contains the answer | 4 of 5 | 3/5, 3/5, 3/5         | 3/5, 3/5, 3/5        | MISSED both   |
| 2. Every answer names a source         | 5 of 5 | 5/5, 5/5, 5/5         | 4/5, 4/5, 5/5        | MET to MISSED |
| 3. Gate stops out-of-corpus questions  | 4 of 5 | 5/5, 5/5, 5/5         | 5/5, 5/5, 5/5        | MET both      |
| 4. One topic per chunk                 | 4 of 5 | 5/5, 5/5, 5/5         | 5/5, 5/5, 5/5        | MET both      |
| 5. No hallucinated answers             | 4 of 5 | 2/2, 2/2, 2/2         | 2/2, 2/2, 2/2        | MET both      |

#### Real output, after

Everything below is from `results/run_2026-10-04_2248_after.md`, except the
retrieval listing, which I printed again with `app.py` because the results
file keeps sources but not their order.

**Criteria 1 and 2, on the one question that changed**

Question: "What are the most common regrets for first-year students?"

Retrieval, produced by `store.py::search` and `store.py::_fuse` (printed by
`python app.py retrieve`). The `Gate:` line comes from `gate.py::check`:

```
#   distance   source                           preview
----------------------------------------------------------------------------------------------------
1   0.6714     thread_office_hours_etiquette.txt THREAD: Is it weird to go to office hours with no sp...
2   0.6205     thread_pass_fail.txt             THREAD: When should you actually use the pass/fail o...
3   0.6432     thread_first_gen.txt             THREAD: Anything specific for first-generation stude...

Gate: best distance 0.621 is under the 0.7 cutoff
```

In the before run `thread_first_year_regret.txt` was first at 0.5956. Here it
is gone. The expected phrase `pass/fail` is still in `thread_pass_fail.txt`,
so criterion 1 counts this question as a pass.

Run 1 answer, produced by `generate.py::answer_from_chunks`, called from
`run_eval.py::run_once`. It names no source, so it fails criterion 2:

```
Based on the provided documents, the text does not mention the most common regrets for first-year students. Therefore, I do not have enough information to answer this question.
```

Run 3 answer, same function. It names two files, so it passes criterion 2:

```
Based on the provided documents, the text does not mention the most common regrets for first-year students, so I do not have enough information to answer that part of the question. 

However, the documents do mention that first-year students commonly get the etiquette of office hours wrong by thinking it is weird to go with no specific question (*thread_office_hours_etiquette.txt*), and one student mentioned regretting spending a pass/fail option on an easy course (*thread_pass_fail.txt*).
```

**Criterion 3. Gate stops out-of-corpus questions**

Produced by `run_eval.py::check_out_of_scope`, cutoff 0.7. Refused 5 of 5, at
the same distances as the before run.

| Out-of-scope question | Best distance | Gate |
|---|---|---|
| What is the capital of Mongolia? | 0.948 | refused |
| How do I change the oil in a diesel engine? | 0.930 | refused |
| Who won the 1994 World Cup? | 0.952 | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.828 | refused |
| How do I write a for loop in Rust? | 0.871 | refused |

**Criterion 4. One topic per chunk**

Chunking and the index did not change, so the five sampled chunks are the
ones already shown under the before run log, produced by
`chunker.py::split_documents`.

**Criterion 5. No hallucinated answers**

Question: "What is the deadline for assignments before they're considered late?"
Run 1, produced by `generate.py::answer_from_chunks`.

- Best distance: 0.4132 (passed the gate)
- Sources retrieved: thread_first_year_regret.txt, thread_group_project.txt, thread_late_work.txt

```
Based on the provided documents, there is no mention of the specific deadline time or date for assignments before they are considered late (the documents only discuss what happens when something is handed in late or how to ask for extensions). Therefore, I do not have enough information to answer this question. 

Source: `thread_late_work.txt`, `thread_first_year_regret.txt`, and `thread_group_project.txt`.
```

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

No. It made one criterion worse and moved none of the others.

Criterion 2 went from 5/5 on every run to 4/5, 4/5 and 5/5, which turns it
from MET to MISSED. One question did that. For "What are the most common
regrets for first-year students?", meaning-only search ranked
`thread_first_year_regret.txt` first at 0.5956. Keyword search ranked it
fifth, because that thread never uses the word "regret". Its title is "What
do you wish you'd known in first year?". The office-hours thread ranked first
on keywords, since it shares "most", "common" and "first" with my question
("the single most common thing first years get wrong"). After fusion the
regrets thread fell to fourth and out of the top three. Without it the model
said it didn't have enough information in runs 1 and 2 and named no source.
In run 3 it gave a partial answer and cited two files.

Criterion 1 stayed at 3/5 on all three runs, which is what I predicted before
the run. Both deadline questions still get the right thread first, and
neither thread has a deadline in it. That supports the diagnosis: the corpus
has no deadline for retrieval to find.

The run also showed a weakness in my scorer. Criterion 1 still counts the
regrets question as a pass, because its expected phrase `pass/fail` appears
in `thread_pass_fail.txt`, which was retrieved. The thread that answers the
question was gone. So the 3/5 after is weaker than the 3/5 before, and one
expected phrase was too thin a check for that question.

Criteria 3, 4 and 5 did not move. The gate refused the same five out-of-scope
questions at the same distances.

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

Two criteria are missed after the fix, and the fix caused one of them.

**Criterion 2, every answer names a source (4/5, 4/5, 5/5):** Hybrid search
broke this, and it is still switched on in `config.py`. The quick repair is
`AI201_HYBRID=0`, which gives back the before run's 5/5. A better repair
would keep keyword search and stop it from pushing out the nearest chunk,
either by weighting the meaning ranking above the keyword one in
`store.py::_fuse` or by always keeping the nearest chunk in the top three.
Stemming would not help, since the regrets thread has no form of the word
"regret" in it. There is a second fix in the prompt: `GROUNDING_INSTRUCTION`
in `generate.py` asks for the document an answer came from and says nothing
about naming the files checked when there is no answer. I stopped because the
milestone asks for one change and an honest result. Adjusting the fusion
until my five questions pass again would fit the fix to the test, and I
couldn't tell whether it helped anywhere else.

**Criterion 1, retrieved chunk contains the answer (3/5, 3/5, 3/5):**
Unchanged, and no change to chunking, embedding, or retrieval will move it.
The two questions that fail ask for deadlines the corpus doesn't have. The fix
is at loading: a document that states the policy, which I don't have and won't
write to pass my own test, or two replacement questions the threads can
answer. I stopped because swapping questions after seeing which ones failed
would be moving the target. The hybrid run was my check that retrieval wasn't
hiding an answer, and criterion 1 came back the same.

**Also weak, though no criterion caught it:** My scorer checks criterion 1
with one expected phrase per question. After the fix it passed the regrets
question on `pass/fail` with the regrets thread missing. Without that pass
the after score is 2/5. It also passes the laptop question on `16GB` when no
thread names a CPU. I left the scorer's checks alone between the two runs so
both logs are scored the same way.

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->

Criterion 5 first, and criterion 1 with it, because they turned out to be one
mistake.

Criterion 5 was the least consistent of the five. It asked for "four of five
tries" when only two of my questions ever trigger it, so every run was 2/2,
and it quoted an exact sentence that nothing in my system produces. Which
questions it applies to is decided by an `answerable` flag I set by hand in
`questions.py`, so it measures my labeling as much as the system. I revised
the wording in unit 2. The sample is still two questions.

Criterion 1 has the other half of the problem. Both criteria count over the
same five questions. Every question I wrote to test criterion 5 is one the
corpus can't answer, so it is a guaranteed miss on criterion 1. With two of
them in the set, criterion 1 was capped at 3/5 against a target of 4 before I
ran anything.

Next unit I'd write two question sets before any run: five the corpus can
answer, for criterion 1, and five on-topic questions it can't, for criterion
5. Criterion 1 would read "for at least 4 of 5 answerable questions, the
thread that answers the question is in the top three". That names the thread,
where my scorer checked for one expected phrase and passed the regrets
question after its thread was gone. Criterion 5 would read "for at least 4 of
5 unanswerable questions, the answer says the documents don't cover it, on
every run".

I'd also write down how each criterion is checked at the same time as its
target. The checks I added later in `scorer.py` ended up deciding what counted
as a pass.

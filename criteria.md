# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. _"Retrieval works"_ is an opinion. _"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"_ is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; _"80% seemed reasonable"_ does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**
My corpus is 23 student threads with one topic each, and every thread is short
enough (320 to 796 characters) to fit whole in one 800-character chunk. A
question about a thread's topic should bring that thread back in the top 3, so
most of my questions should pass. I left room for one miss. The weakest match
of my five is the first-year regrets question at 0.596, so that is where I had
the least margin.
<!-- e.g. "One of my questions is about a topic only two documents mention, so
     I expect that one to be hard." -->

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**
All five, because naming a source doesn't depend on how hard the question is.
`generate.py::build_prompt` labels every excerpt `[from <filename>]`, and
`GROUNDING_INSTRUCTION` tells the model to name the document its answer came
from. The filename is in front of the model on every call. A miss would mean
the model ignored an instruction. That is a fault in my prompt whatever the
question is, so I didn't leave room for one.
<!-- Why all five and not four? What about your setup makes that achievable —
     or what would have to go wrong for it not to be? -->

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**
There was a clean gap. My five in-corpus questions came back between 0.402 and
0.596, and the five out-of-scope ones between 0.828 and 0.952, with nothing in
between. I set `THRESHOLD` to 0.7, inside that gap. I kept the target at 4 of 5
because the gap is measured on only ten questions. The nearest out-of-scope
one, the ibuprofen question at 0.828, is 0.128 from the cutoff, so a change to
my chunking or my embedding model could move one question across.
<!-- What did your distances look like when you set the cutoff in Milestone 4?
     Was there a clean gap, or did the two groups overlap? -->

---

## 4. One topic per chunk

At least 4 of 5 sampled chunks discuss only one thread's topic, with no chunk blending content from two different threads.

**Why this target:**
Each file in `advice_threads` is a self-contained thread on one topic; a chunk spanning two threads would mean my `CHUNK_SIZE`/boundaries aren't respecting document breaks, which would hurt retrieval precision.

---

## 5. No hallucinated answers

When the retrieved chunks don't actually contain the answer, the system says "I don't have enough information about that topic" rather than answering anyway-in at least four of five tries.

**Why this target:**
Distinct from criterion #3 (out-of-corpus). This catches in-corpus-adjacent
questions where retrieval returns chunks, but none actually answer them.
That's the case where a model most tempted to guess.

In my corpus that case is the two deadline questions. `thread_late_work.txt`
talks about deadlines ("If it says 10% a day, it's 10% a day") and
`thread_transfer_credits.txt` says the department decides, but neither thread
gives a date. Both came back closer than my 0.7 cutoff, at 0.413 and 0.480, so
the gate lets them through and the only thing stopping a guess is one line in
`GROUNDING_INSTRUCTION`: "If the documents don't cover the question, say you
don't have enough information. Do not guess." The gate is code and does the
same thing every time. That line is an instruction to a model, and the model's
wording changes from run to run, so I allowed one miss in five.

> **Revised in unit 2:** When the retrieved chunks don't contain the answer,
> the answer says the documents don't cover it instead of answering anyway, in
> at least four of every five tries where that applies. Any wording that says
> so counts: the gate's refusal, "no mention of", "do not cover", "not enough
> information". The full list is `ADMISSIONS` in `scorer.py`. The rate has to
> hold in every run.
>
> **Why revised:** I couldn't measure the original. It quotes one exact
> sentence, and nothing in my system produces it. The gate's fixed refusal in
> `gate.py` reads "I don't have enough information about that.", and the prompt
> in `generate.py` only tells the model to say it doesn't have enough
> information, so each answer is worded differently ("there is no mention of a
> specific deadline"). The original also counts five tries, and only two of my
> five questions retrieve chunks that lack the answer, so a run has two tries.
> The four-in-five bar has not moved. The revision changes what counts as
> saying so, and it takes the rate over the tries that exist.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->

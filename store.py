"""
Stages 3 and 4 of the pipeline: embedding chunks and retrieving them.

Three things in here are worth knowing about, because they'd quietly break the
rest of the project if they were wrong:

1. The Chroma collection is created with cosine distance, explicitly. Chroma
   defaults to squared L2, and the 0.6 threshold the course uses is calibrated
   against cosine. Getting this wrong makes every distance number meaningless.

2. `search` returns the distance alongside each chunk. Milestone 4 has you
   compare distances, so they have to be visible.

3. The embedding model is the one Chroma bundles, not one loaded through
   `sentence-transformers`. It is the same model — `all-MiniLM-L6-v2`, 384
   dimensions — but it arrives as an ONNX build from Chroma's own CDN, so the
   install needs neither PyTorch nor a reachable Hugging Face. See `_embedder`.
"""

import os
import re
import shutil
from collections import Counter
from dataclasses import dataclass

# Must be set BEFORE chromadb is imported. Without it, some Chroma versions
# print "Failed to send telemetry event ..." on every single call — which looks
# exactly like a real error, isn't one, and cost a previous cohort a lot of
# confused help-channel messages.
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

import chromadb  # noqa: E402

import config
from chunker import Chunk


@dataclass
class Result:
    """One retrieved chunk and how far it was from the question."""

    text: str
    source: str
    label: str
    distance: float  # LOWER IS BETTER. 0.3 is close, 0.9 is unrelated.
    produced_by: str


_model = None

# The model Chroma bundles. Anything else in config.EMBEDDING_MODEL means
# "fetch that one from Hugging Face instead" — see `_embedder`.
BUNDLED_MODEL = "all-MiniLM-L6-v2"


class _OnnxEmbedder:
    """
    Chroma's built-in embedder, wrapped to look like the other two.

    Chroma's embedding functions are called directly and hand back numpy
    arrays. The rest of this file wants `.encode(texts)`, so the adapter lives
    here rather than making every caller care which embedder it got.
    """

    def __init__(self):
        from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

        self._ef = ONNXMiniLM_L6_V2()

    def encode(self, texts, show_progress_bar: bool = False):
        return [vector.tolist() for vector in self._ef(list(texts))]


def _sentence_transformer(name: str):
    """
    The escape hatch: any model that isn't the bundled one.

    Unit 2's "try a second embedding model" stretch option comes through here,
    and so does anything you set `EMBEDDING_MODEL` to. This path *does* need
    `sentence-transformers` and a reachable Hugging Face, neither of which the
    default install has — which is the whole point of the default install.
    """
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            f"config.EMBEDDING_MODEL is set to {name!r}, which isn't the model "
            f"Chroma bundles ({BUNDLED_MODEL!r}), so it has to be downloaded "
            f"from Hugging Face.\n"
            f"Install the optional dependency first:\n"
            f"    pip install 'sentence-transformers>=3.4,<3.5'\n"
            f"Or set EMBEDDING_MODEL back to {BUNDLED_MODEL!r}."
        ) from exc

    return SentenceTransformer(name)


def _embedder():
    """
    Load the embedding model once and keep it.

    First call is slow — it downloads about 80 MB. That's why setup happens
    before class.
    """
    global _model

    if _model is not None:
        return _model

    # Used only by this repo's own smoke test, which runs where no model can be
    # downloaded at all. Never set this yourself.
    if os.getenv("AI201_FAKE_EMBEDDINGS") == "1":
        from _smoke_embedder import FakeEmbedder

        _model = FakeEmbedder()
    elif config.EMBEDDING_MODEL == BUNDLED_MODEL:
        _model = _OnnxEmbedder()
    else:
        _model = _sentence_transformer(config.EMBEDDING_MODEL)

    return _model


def embed(texts: list[str]) -> list[list[float]]:
    """Turn text into vectors. Runs on your machine, costs no API quota."""
    vectors = _embedder().encode(texts, show_progress_bar=False)
    # sentence-transformers and the smoke stand-in return something with a
    # .tolist(); _OnnxEmbedder has already done that conversion itself.
    return vectors.tolist() if hasattr(vectors, "tolist") else vectors


def _client():
    return chromadb.PersistentClient(
        path=str(config.CHROMA_DIR),
        settings=chromadb.config.Settings(anonymized_telemetry=False),
    )


def build_index(
    chunks: list[Chunk],
    corpus: str | None = None,
    variant: str = "default",
) -> int:
    """
    Embed every chunk and store it.

    `variant` lets you keep more than one index of the same corpus at the same
    time. In unit 2, when you compare two chunking strategies, index the second
    one as variant="v2" and you can query both instead of deleting the first
    and starting over.
    """
    name = config.collection_name(corpus, variant)
    client = _client()

    try:
        client.delete_collection(name)
    except Exception:
        pass

    collection = client.create_collection(
        name=name,
        # ⚠️ Do not remove. Chroma defaults to squared L2, and every distance
        # number in this course assumes cosine.
        metadata={"hnsw:space": "cosine"},
    )

    batch = 256
    for start in range(0, len(chunks), batch):
        window = chunks[start : start + batch]
        collection.add(
            ids=[f"{c.source}#{c.index}" for c in window],
            documents=[c.text for c in window],
            embeddings=embed([c.text for c in window]),
            metadatas=[
                {"source": c.source, "index": c.index, "produced_by": c.produced_by}
                for c in window
            ],
        )

    return len(chunks)


def search(
    question: str,
    top_k: int | None = None,
    corpus: str | None = None,
    variant: str = "default",
    sources: list[str] | None = None,
) -> list[Result]:
    """
    Retrieve the chunks that best match a question.

    With `config.HYBRID` off this is meaning only: the nearest chunks,
    nearest-first. With it on, every chunk is ranked by meaning and by keyword
    match, the two rankings are fused, and the top of the fused list comes
    back. Either way each Result carries its cosine distance.
    """
    top_k = top_k or config.TOP_K
    name = config.collection_name(corpus, variant)

    try:
        collection = _client().get_collection(name)
    except Exception as exc:
        raise RuntimeError(
            f"No index called '{name}'. Run `python app.py index` first."
        ) from exc

    where = {"source": {"$in": sources}} if sources else None

    # Hybrid asks for every chunk with its distance, so the keyword ranking has
    # the whole collection to choose from. Fine at this corpus size; a large
    # one would want a candidate pool instead.
    wanted = collection.count() if config.HYBRID else min(top_k, collection.count())

    raw = collection.query(
        query_embeddings=embed([question]),
        n_results=wanted,
        where=where,
    )

    results: list[Result] = []
    for text, meta, distance in zip(
        raw["documents"][0], raw["metadatas"][0], raw["distances"][0]
    ):
        results.append(
            Result(
                text=text,
                source=str(meta.get("source", "unknown")),
                label=f"{meta.get('source', 'unknown')}#{meta.get('index', 0)}",
                distance=float(distance),
                produced_by=str(meta.get("produced_by", "unknown")),
            )
        )

    if config.HYBRID:
        results = _fuse(results, question)[:top_k]
    return results


_WORD = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> list[str]:
    """Lowercase words and numbers, for keyword matching."""
    return _WORD.findall(text.lower())


def _fuse(semantic: list[Result], question: str) -> list[Result]:
    """
    Re-rank chunks by meaning and by keyword match together.

    `semantic` is every candidate chunk, nearest-first. BM25 scores each one on
    the words it shares with the question, and the two rankings are combined
    with reciprocal rank fusion: a chunk earns 1 / (RRF_K + rank) from each
    ranking. A chunk that shares no distinguishing word with the question earns
    nothing from the keyword side.

    Results keep their cosine distance, so the relevance gate still has a real
    distance to compare against the cutoff. The gate sees only the chunks
    returned, though, so if the nearest chunk is fused out of the top few, the
    best distance it compares is larger than the true nearest one. That can
    turn a pass into a refusal. It can never do the reverse.
    """
    if not semantic:
        return []

    try:
        from rank_bm25 import BM25Okapi
    except ImportError as exc:
        raise RuntimeError(
            "config.HYBRID is on, which needs the rank-bm25 package.\n"
            "Install the course requirements first:\n"
            "    pip install -r requirements.txt\n"
            "Or set AI201_HYBRID=0 to search by meaning only."
        ) from exc

    docs = [_tokens(r.text) for r in semantic]

    # A word in more than half the chunks ("the", "reply", "votes") says
    # nothing about topic. BM25Okapi floors such a word's weight to a small
    # positive number instead of zero, which would hand every chunk a keyword
    # rank, so those words are dropped from the question first.
    in_chunks = Counter(word for doc in docs for word in set(doc))
    query = [w for w in _tokens(question) if in_chunks[w] <= len(docs) / 2]

    scores = BM25Okapi(docs).get_scores(query)
    by_keyword = sorted(
        (i for i in range(len(semantic)) if scores[i] > 0),
        key=lambda i: -scores[i],
    )
    keyword_rank = {i: rank for rank, i in enumerate(by_keyword, start=1)}

    def fused(i: int) -> float:
        score = 1 / (config.RRF_K + i + 1)  # i is the 0-based semantic rank
        if i in keyword_rank:
            score += 1 / (config.RRF_K + keyword_rank[i])
        return score

    order = sorted(range(len(semantic)), key=lambda i: -fused(i))
    return [semantic[i] for i in order]


def index_exists(corpus: str | None = None, variant: str = "default") -> bool:
    """Is there an index here to search, without searching it?

    `serve.py`'s health check asks this. It deliberately does not embed
    anything: loading the embedding model takes 80 MB and a few seconds, and a
    health check that heavy is a health check nobody can afford to call.
    """
    try:
        collection = _client().get_collection(config.collection_name(corpus, variant))
        return collection.count() > 0
    except Exception:
        return False


def reset():
    """Delete every index. Occasionally the fastest way out of a mess."""
    if config.CHROMA_DIR.exists():
        shutil.rmtree(config.CHROMA_DIR)

import time
import timeit
from reuters_parser import parse_all_files, tokenize
from naiveIndexer import build_term_docid_list, sort_and_dedupe, build_index


def spimi_add_pair(index, term, docid):
    """Core SPIMI step: append the docID directly to the term's postings list.
    Assumes documents arrive in increasing docID order, so a duplicate can only
    be the last entry of the list."""
    postings = index.setdefault(term, [])
    if not postings or postings[-1] != docid:
        postings.append(docid)


def spimi_add_document(index, doc):
    """Adds one (newid, title, body) document straight into the index (no list F)."""
    newid, title, body = doc
    for token in tokenize(title + " " + body):
        spimi_add_pair(index, token, int(newid))


def build_spimi_index(docs):
    index = {}
    for doc in docs:
        spimi_add_document(index, doc)
    return index


def first_n_pairs(docs, n=10000):
    """The first n (term, docID) pairings of the corpus (tokenizing is done here, outside the timings)."""
    pairs = []
    for newid, title, body in docs:
        for token in tokenize(title + " " + body):
            pairs.append((token, int(newid)))
            if len(pairs) == n:
                return pairs
    return pairs


def spimi_from_pairs(pairs):
    index = {}
    for term, docid in pairs:
        spimi_add_pair(index, term, docid)
    return index


def naive_from_pairs(pairs):
    return build_index(sort_and_dedupe(pairs))


if __name__ == "__main__":
    docs = parse_all_files()

    start = time.perf_counter()
    spimi_index = build_spimi_index(docs)
    print(f"SPIMI index built: {len(spimi_index)} unique terms "
          f"in {time.perf_counter() - start:.4f} s (full corpus)")
    print("Postings list for 'cocoa' (SPIMI):", spimi_index.get("cocoa"))

    # Correctness: the SPIMI index must equal the naive index
    naive_index = naive_from_pairs(build_term_docid_list(docs))
    print("SPIMI index identical to naive index:", spimi_index == naive_index)

    # Timing on exactly 10,000 term-docID pairings, averaged over many runs
    pairs = first_n_pairs(docs, 10000)
    runs = 200
    naive_t = timeit.timeit(lambda: naive_from_pairs(pairs), number=runs) / runs
    spimi_t = timeit.timeit(lambda: spimi_from_pairs(pairs), number=runs) / runs
    print(f"\nTiming for {len(pairs)} term-docID pairings (average of {runs} runs):")
    print(f"  Naive indexer: {naive_t * 1000:.3f} ms")
    print(f"  SPIMI indexer: {spimi_t * 1000:.3f} ms")
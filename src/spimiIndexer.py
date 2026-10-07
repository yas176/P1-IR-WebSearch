import time
from parser import parse_all_files, tokenize
from naiveIndexer import build_term_docid_list, sort_and_dedupe, build_index


def spimi_add_document(index, doc):
    """
    Takes one (newid, title, body) document and directly inserts its
    (term, docID) pairs into the index dictionary - no intermediate list.
    Avoids duplicate docIDs in the same postings list.
    """
    newid, title, body = doc
    newid = int(newid)
    full_text = title + " " + body
    tokens = tokenize(full_text)

    for token in tokens:
        if token not in index:
            index[token] = []
        # avoid duplicate docIDs for the same term within the same document
        if not index[token] or index[token][-1] != newid:
            index[token].append(newid)


def build_spimi_index(docs):
    """
    Builds the full inverted index by processing documents one at a time,
    directly appending docIDs to each term's postings list.
    """
    index = {}
    for doc in docs:
        spimi_add_document(index, doc)
    return index


def count_pairs_for_n_docs(docs, target_pairs):
    """
    Finds how many documents (starting from the beginning) are needed
    to accumulate at least target_pairs term-docID pairs (pre-dedup).
    Returns the subset of docs.
    """
    total = 0
    subset = []
    for doc in docs:
        newid, title, body = doc
        full_text = title + " " + body
        tokens = tokenize(full_text)
        total += len(tokens)
        subset.append(doc)
        if total >= target_pairs:
            break
    return subset, total


if __name__ == "__main__":
    docs = parse_all_files("data")

    #Build full SPIMI index over the whole corpus
    start = time.perf_counter()
    spimi_index = build_spimi_index(docs)
    spimi_full_time = time.perf_counter() - start

    print(f"SPIMI index built: {len(spimi_index)} unique terms")
    print(f"Time to build full SPIMI index: {spimi_full_time:.4f} seconds")
    print("Postings list for 'cocoa' (SPIMI):", spimi_index.get("cocoa"))

    # Timing comparison: naive vs SPIMI for ~10,000 term-docID pairings
    subset, total_pairs = count_pairs_for_n_docs(docs, 10000)
    print(f"\nUsing {len(subset)} documents (~{total_pairs} term-docID pairings) for timing comparison")

    # Naive approach timing
    start = time.perf_counter()
    F = build_term_docid_list(subset)
    sorted_F = sort_and_dedupe(F)
    naive_index = build_index(sorted_F)
    naive_time = time.perf_counter() - start

    # SPIMI approach timing
    start = time.perf_counter()
    spimi_subset_index = build_spimi_index(subset)
    spimi_time = time.perf_counter() - start

    print(f"\nNaive indexer time (for {total_pairs} pairings): {naive_time:.4f} seconds")
    print(f"SPIMI indexer time (for {total_pairs} pairings): {spimi_time:.4f} seconds")
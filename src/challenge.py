"""Run the 24-hour challenge queries against both index implementations."""

import time

from naiveIndexer import build_index, build_term_docid_list, sort_and_dedupe
from query import and_query, single_term_query
from reuters_parser import parse_all_files
from spimiIndexer import build_spimi_index


CHALLENGE_QUERIES = (
    ("Carmark",),
    ("copper",),
    ("Chrysler", "Bundesbank"),
)


def run_query(index, terms):
    if len(terms) == 1:
        return single_term_query(index, terms[0])
    return and_query(index, terms[0], terms[1])


def timed_query(index, terms):
    start = time.perf_counter()
    result = run_query(index, terms)
    elapsed = time.perf_counter() - start
    return result, elapsed


def print_results(index_name, index, build_seconds):
    print(f"\n{index_name}")
    print(f"Index terms: {len(index)}")
    print(f"Index build time: {build_seconds:.6f} s")
    for terms in CHALLENGE_QUERIES:
        result, query_seconds = timed_query(index, terms)
        query_text = " AND ".join(terms)
        print(f"{query_text}: {len(result)} documents")
        print(f"  Document IDs: {result}")
        print(f"  Query time: {query_seconds:.9f} s")

def check_zero_result(index, terms):
    """Print how many documents each term appears in on its own."""
    for term in terms:
        result, query_seconds = timed_query(index, (term,))
        print(f"{term}: {len(result)} documents")
        print(f"  Document IDs: {result}")
        print(f"  Query time: {query_seconds:.9f} s")


def main():
    docs = parse_all_files()
    print(f"Documents parsed: {len(docs)}")

    start = time.perf_counter()
    naive_index = build_index(
        sort_and_dedupe(build_term_docid_list(docs))
    )
    naive_seconds = time.perf_counter() - start

    start = time.perf_counter()
    spimi_index = build_spimi_index(docs)
    spimi_seconds = time.perf_counter() - start

    print_results("Naive indexer", naive_index, naive_seconds)
    print_results("SPIMI indexer", spimi_index, spimi_seconds)
    print(
        "\nIndexes identical: "
        f"{naive_index == spimi_index}"
    
    )

    # The indexes are identical, so I will check the zero-result query once so we avoid duplicates in the output file
    check_zero_result(naive_index, ("Chrysler", "Bundesbank"))
    


if __name__ == "__main__":
    main()
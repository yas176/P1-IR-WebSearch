from parser import parse_all_files
from naiveIndexer import build_term_docid_list, sort_and_dedupe, build_index


def single_term_query(index, term):
    """
    Returns the postings list for a single term, or an empty list if not found.
    """
    return index.get(term, [])


def and_query(index, term1, term2):
    """
    Returns the intersection of the postings lists for term1 and term2,
    using the two-pointer merge algorithm.
    """
    list1 = single_term_query(index, term1)
    list2 = single_term_query(index, term2)

    result = []
    i, j = 0, 0

    while i < len(list1) and j < len(list2):
        if list1[i] == list2[j]:
            result.append(list1[i])
            i += 1
            j += 1
        elif list1[i] < list2[j]:
            i += 1
        else:
            j += 1

    return result


# main to test both query functions
if __name__ == "__main__":
    docs = parse_all_files("data")
    F = build_term_docid_list(docs)
    sorted_F = sort_and_dedupe(F)
    index = build_index(sorted_F)

    # Subproject2 validation: 3 single-term + 3 AND queries 
    print("***** Single-term queries ******")
    for term in ["dollar", "wheat", "gold"]:
        result = single_term_query(index, term)
        print(f"'{term}': {len(result)} documents -> {result[:10]}{'...' if len(result) > 10 else ''}")

    print("\n******* AND queries ******")
    and_pairs = [("gold", "dollar"), ("wheat", "dollar"), ("gold", "wheat")]
    for term1, term2 in and_pairs:
        result = and_query(index, term1, term2)
        print(f"'{term1}' AND '{term2}': {len(result)} documents -> {result[:10]}{'...' if len(result) > 10 else ''}")

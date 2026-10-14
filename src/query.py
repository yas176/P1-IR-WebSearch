from reuters_parser import parse_all_files
from naiveIndexer import build_term_docid_list, sort_and_dedupe, build_index


def single_term_query(index, term):
    """Returns the postings list for one term ([] if the term is not in the index)."""
    return index.get(term.lower(), [])


def intersect(list1, list2):
    """Two-pointer merge intersection of two sorted postings lists."""
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


def and_query(index, term1, term2):
    """AND query for two terms using the intersection algorithm."""
    return intersect(single_term_query(index, term1), single_term_query(index, term2))


def and_query_multi(index, terms):
    """AND query for any number of terms; intersects the shortest lists first."""
    lists = sorted((single_term_query(index, t) for t in terms), key=len)
    if not lists or not lists[0]:
        return []
    result = lists[0]
    for postings in lists[1:]:
        result = intersect(result, postings)
        if not result:
            break
    return result


def show(result, n=10):
    return f"{len(result)} documents -> {result[:n]}{'...' if len(result) > n else ''}"


if __name__ == "__main__":
    docs = parse_all_files()
    index = build_index(sort_and_dedupe(build_term_docid_list(docs)))

    print("***** Single-term queries *****")
    for term in ["dollar", "wheat", "gold"]:
        print(f"'{term}': {show(single_term_query(index, term))}")

    print("\n***** AND queries *****")
    and_pairs = [("gold", "dollar"), ("wheat", "dollar"), ("gold", "wheat")]
    for t1, t2 in and_pairs:
        print(f"'{t1}' AND '{t2}': {show(and_query(index, t1, t2))}")

    print("\n***** Extra tests *****")
    for t1, t2 in and_pairs:
        expected = sorted(set(index.get(t1, [])) & set(index.get(t2, [])))
        print(f"'{t1}' AND '{t2}' matches Python set intersection:", and_query(index, t1, t2) == expected)
    print("Missing term returns empty list:", single_term_query(index, "zzzznotaword") == [])
    print("AND with a missing term returns empty list:", and_query(index, "gold", "zzzznotaword") == [])
    print("3-term AND (gold, dollar, wheat):", show(and_query_multi(index, ["gold", "dollar", "wheat"])))
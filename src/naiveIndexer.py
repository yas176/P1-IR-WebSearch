from reuters_parser import parse_all_files, tokenize


def get_term_docid_pairs(doc):
    """Takes one (newid, title, body) document and returns (term, docID) pairs."""
    newid, title, body = doc
    tokens = tokenize(title + " " + body)
    return [(token, int(newid)) for token in tokens]


def build_term_docid_list(docs):
    """Step 1: combines the pairs of all documents into one big list F."""
    F = []
    for doc in docs:
        F.extend(get_term_docid_pairs(doc))
    return F


def sort_and_dedupe(F):
    """Step 2: sort F, then remove duplicates (duplicates are adjacent after sorting)."""
    sorted_F = sorted(F)  # by term, then by numeric docID
    deduped = []
    for pair in sorted_F:
        if not deduped or pair != deduped[-1]:
            deduped.append(pair)
    return deduped


def build_index(sorted_F):
    """Step 3: group docIDs of the same term into a postings list (hash table)."""
    index = {}
    for term, docid in sorted_F:
        if term not in index:
            index[term] = []
        index[term].append(docid)
    return index


if __name__ == "__main__":
    docs = parse_all_files()
    F = build_term_docid_list(docs)
    print(f"Total pairs in F: {len(F)}")

    sorted_F = sort_and_dedupe(F)
    print(f"Total unique pairs after dedup: {len(sorted_F)}")

    index = build_index(sorted_F)
    print(f"Total unique terms in index: {len(index)}")
    print("Docs containing 'cocoa':", len(index.get("cocoa", [])))

    # Cleanup check: all four should print False
    for junk in ["lt", "amp", "acumulative", "wasincluded"]:
        print(f"'{junk}' in index:", junk in index)
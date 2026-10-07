from parser import parse_all_files, tokenize


def get_term_docid_pairs(doc):
    """
    Takes one (newid, title, body) document and returns a list of
    (term, docID) pairs.
    """
    newid, title, body = doc
    full_text = title + " " + body
    tokens = tokenize(full_text)

    pairs = []
    for token in tokens:
        pairs.append((token, newid))

    return pairs


def build_term_docid_list(docs):
    """
    Loops through all documents and combines their (term, docID) pairs
    into one big list F.
    """
    F = []
    for doc in docs:
        pairs = get_term_docid_pairs(doc)
        F.extend(pairs)

    return F


# main to test if everything is working correctly
if __name__ == "__main__":
    docs = parse_all_files("data")
    F = build_term_docid_list(docs)
    print(f"Total pairs in F: {len(F)}")
    print("First 10 pairs:", F[:10])
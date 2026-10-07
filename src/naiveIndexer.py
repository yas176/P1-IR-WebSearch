from parser import parse_all_files, tokenize


def get_term_docid_pairs(doc):
    """
    Takes one (newid, title, body) document and returns a list of
    (term, docID) pairs.
    """
    newid, title, body = doc
    full_text = title + " " + body
    tokens = tokenize(full_text)

    # loop through tokens and pair each with newid
    pairs = []
    for token in tokens:
        pairs.append((token, int(newid)))    

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

# Sort F and remove duplicates 
def sort_and_dedupe(F):
    """
    Removes duplicate (term, docID) pairs and sorts the result.
    """
    unique_pairs = set(F)            # drops duplicates
    sorted_F = sorted(unique_pairs)  # sorts by term, then by docID
    return sorted_F

# Turn sorted F into actual index (PostingLists) 
def build_index(sorted_F):
    """
    Converts sorted, deduped (term, docID) pairs into an inverted index:
    a dictionary mapping each term to its postings list (sorted docIDs).
    """
    index = {}
    for term, docid in sorted_F:
        if term not in index:
            index[term] = []
        index[term].append(docid)
    return index


# main to test if everything is working correctly
if __name__ == "__main__":
    docs = parse_all_files("data")
    F = build_term_docid_list(docs)
    print(f"Total pairs in F: {len(F)}")

    sorted_F = sort_and_dedupe(F)
    print(f"Total unique pairs after dedup: {len(sorted_F)}")

    index = build_index(sorted_F)
    print(f"Total unique terms in index: {len(index)}")
    print("Postings list for 'cocoa':", index.get("cocoa"))
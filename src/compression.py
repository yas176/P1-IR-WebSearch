from collections import Counter
from functools import lru_cache
from nltk.stem import PorterStemmer

from reuters_parser import parse_all_files, tokenize, tokenize_case_sensitive
from naiveIndexer import build_term_docid_list, sort_and_dedupe, build_index
from query import single_term_query, and_query

stemmer = PorterStemmer()


@lru_cache(maxsize=None)
def stem_word(word):
    return stemmer.stem(word)



#  Filters (each works on one document's token list) 

def remove_numbers(tokens):
    return [t for t in tokens if not t.isdigit()]


def case_fold(tokens):
    return [t.lower() for t in tokens]


def remove_stopwords(tokens, stop_set):
    return [t for t in tokens if t not in stop_set]


def stem_tokens(tokens):
    return [stem_word(t) for t in tokens]


def top_terms(token_lists, n):
    """The n most frequent terms in the collection (used as the stop word list)."""
    counts = Counter()
    for tokens in token_lists:
        counts.update(tokens)
    return [term for term, _ in counts.most_common(n)]


# Table computation

def count_step(token_lists, transform):
    """Returns (distinct terms, nonpositional postings) after applying transform to every doc."""
    vocab = set()
    postings = 0
    for tokens in token_lists:
        terms = set(transform(tokens))
        postings += len(terms)   # one posting per distinct (term, doc) pair
        vocab.update(terms)
    return len(vocab), postings


def pct(new, ref):
    return round((new - ref) / ref * 100)


def print_table(rows):
    """rows: list of (name, terms, postings, reference_row_index)."""
    base_terms, base_post = rows[0][1], rows[0][2]
    print(f"{'':<16}{'distinct terms':>38}{'nonpositional postings':>42}")
    print(f"{'':<16}{'number':>14}{'D%':>8}{'T%':>8}{'number':>16}{'D%':>8}{'T%':>8}")
    for name, terms, post, ref in rows:
        if ref is None:
            print(f"{name:<16}{terms:>14,}{'':>16}{post:>16,}")
        else:
            rt, rp = rows[ref][1], rows[ref][2]
            print(f"{name:<16}{terms:>14,}{pct(terms, rt):>8}{pct(terms, base_terms):>8}"
                  f"{post:>16,}{pct(post, rp):>8}{pct(post, base_post):>8}")


# compressed index

def get_compressed_pairs(doc, stop_set):
    newid, title, body = doc
    tokens = tokenize(title + " " + body)      # lowercase NLTK tokens
    tokens = remove_numbers(tokens)
    tokens = remove_stopwords(tokens, stop_set)
    tokens = stem_tokens(tokens)
    return [(t, int(newid)) for t in tokens]


def build_compressed_index(docs, stop_set):
    F = []
    for doc in docs:
        F.extend(get_compressed_pairs(doc, stop_set))
    return build_index(sort_and_dedupe(F))


if __name__ == "__main__":
    docs = parse_all_files()

    # Case-sensitive token lists, one per document (the textbook's "unfiltered" is case-sensitive)
    cs_lists = [tokenize_case_sensitive(title + " " + body) for _, title, body in docs]

    # Stop word lists = most frequent terms of THIS collection (case-folded, no numbers)
    folded_lists = [remove_numbers(case_fold(t)) for t in cs_lists]
    stop30 = set(top_terms(folded_lists, 30))
    stop150 = set(top_terms(folded_lists, 150))
    print("30 most frequent terms (used as stop words):", sorted(stop30), "\n")

    steps = [
        ("unfiltered",     lambda t: t, None),
        ("no numbers",     remove_numbers, 0),
        ("case folding",   lambda t: case_fold(remove_numbers(t)), 1),
        ("30 stop words",  lambda t: remove_stopwords(case_fold(remove_numbers(t)), stop30), 2),
        ("150 stop words", lambda t: remove_stopwords(case_fold(remove_numbers(t)), stop150), 2),
        ("stemming",       lambda t: stem_tokens(remove_stopwords(case_fold(remove_numbers(t)), stop150)), 4),
    ]
    rows = []
    for name, transform, ref in steps:
        terms, post = count_step(cs_lists, transform)
        rows.append((name, terms, post, ref))
    print_table(rows)

    # Original vs compressed index on the 6 sample queries ----
    original_index = build_index(sort_and_dedupe(build_term_docid_list(docs)))
    compressed_index = build_compressed_index(docs, stop150)
    print(f"\nOriginal index: {len(original_index)} terms | Compressed index: {len(compressed_index)} terms")

    singles = ["dollar", "wheat", "gold"]
    pairs = [("gold", "dollar"), ("wheat", "dollar"), ("gold", "wheat")]

    print("\n ***** Single-term queries: original vs compressed *****")
    for term in singles:
        s = stem_word(term)
        a = single_term_query(original_index, term)
        b = single_term_query(compressed_index, s)
        print(f"'{term}' (stem '{s}'): original {len(a)} -> compressed {len(b)}")

    print("\n***** AND queries: original vs compressed *****")
    for t1, t2 in pairs:
        a = and_query(original_index, t1, t2)
        b = and_query(compressed_index, stem_word(t1), stem_word(t2))
        print(f"'{t1}' AND '{t2}': original {len(a)} -> compressed {len(b)}")

    #Evidence for the discussion: which words collapse into each query stem 
    vocab = set(t for tokens in folded_lists for t in tokens)
    print("\n*****Words that map to each query stem *****")
    for term in singles:
        s = stem_word(term)
        print(f"stem '{s}':", sorted(w for w in vocab if stem_word(w) == s))
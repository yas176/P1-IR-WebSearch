from parser import parse_all_files, tokenize
from naiveIndexer import sort_and_dedupe, build_index
from query import single_term_query, and_query
from nltk.stem import PorterStemmer



# STOPWORD LISTS

STOPWORDS_30 = [
    "the", "of", "and", "a", "to", "in", "is", "it", "that", "was",
    "for", "on", "are", "as", "with", "his", "they", "at", "be", "this",
    "from", "i", "have", "or", "by", "one", "had", "not", "but", "what"
]

STOPWORDS_150 = STOPWORDS_30 + [
    "all", "were", "we", "when", "your", "can", "said", "there", "use", "an",
    "each", "which", "she", "do", "how", "their", "if", "will", "up", "other",
    "about", "out", "many", "then", "them", "these", "so", "some", "her", "would",
    "make", "like", "him", "into", "time", "has", "look", "two", "more", "write",
    "go", "see", "number", "no", "way", "could", "people", "my", "than", "first",
    "water", "been", "call", "who", "its", "now", "find", "long", "down", "day",
    "did", "get", "come", "made", "may", "part", "over", "new", "sound", "take",
    "only", "little", "work", "know", "place", "year", "live", "me", "back", "give",
    "most", "very", "after", "thing", "our", "just", "name", "good", "sentence", "man",
    "think", "say", "great", "where", "help", "through", "much", "before", "line", "right",
    "too", "mean", "old", "any", "same", "tell", "boy", "follow", "came", "want",
    "show", "also", "around", "form", "three", "small", "set", "put", "end", "does",
    "another", "well", "large", "must", "big", "even", "such", "because", "turn", "here",
    "why", "ask", "went", "men", "read", "need", "land", "different", "home", "us"
]



# Filter functions 

def remove_numbers(tokens):
    """
    Removes purely numeric tokens.
    """
    return [t for t in tokens if not t.isdigit()]


def remove_stopwords(tokens, stopword_list):
    """
    Removes any token found in the given stopword list.
    """
    stopword_set = set(stopword_list)
    return [t for t in tokens if t not in stopword_set]


stemmer = PorterStemmer()

def stem_tokens(tokens):
    """
    Applies the Porter stemmer to each token.
    """
    return [stemmer.stem(t) for t in tokens]



# Helper to build one big token stream from all documents

def get_all_tokens(docs):
    """
    Tokenizes every document and combines into one big list of all tokens.
    """
    all_tokens = []
    for newid, title, body in docs:
        full_text = title + " " + body
        all_tokens.extend(tokenize(full_text))
    return all_tokens




# Full Compression pipeline (for building the compressed index)

def compress_tokens(tokens):
    """
    Applies the full compression pipeline: remove numbers, remove 150 stopwords, stem.
    """
    tokens = remove_numbers(tokens)
    tokens = remove_stopwords(tokens, STOPWORDS_150)
    tokens = stem_tokens(tokens)
    return tokens


def get_compressed_pairs(doc):
    """
    Takes one (newid, title, body) document and returns (stemmed_term, docID) pairs.
    """
    newid, title, body = doc
    newid = int(newid)
    full_text = title + " " + body
    tokens = tokenize(full_text)
    compressed = compress_tokens(tokens)

    pairs = []
    for token in compressed:
        pairs.append((token, newid))
    return pairs


def build_compressed_term_docid_list(docs):
    """
    Loops through all documents, building compressed (term, docID) pairs.
    """
    F = []
    for doc in docs:
        F.extend(get_compressed_pairs(doc))
    return F



# Main function to test the compression pipeline and re-run the 6 sample queries

if __name__ == "__main__":
    docs = parse_all_files("data")
    tokens = get_all_tokens(docs)

    # Part 1: Compression table 
    print(f"{'Step':<20}{'Distinct Terms':>15}")

    unfiltered_vocab = set(tokens)
    print(f"{'unfiltered':<20}{len(unfiltered_vocab):>15}")

    no_numbers = remove_numbers(tokens)
    no_numbers_vocab = set(no_numbers)
    print(f"{'no numbers':<20}{len(no_numbers_vocab):>15}")

    case_folded_vocab = no_numbers_vocab
    print(f"{'case folding':<20}{len(case_folded_vocab):>15}")

    no_30_stop = remove_stopwords(no_numbers, STOPWORDS_30)
    no_30_vocab = set(no_30_stop)
    print(f"{'30 stop words':<20}{len(no_30_vocab):>15}")

    no_150_stop = remove_stopwords(no_numbers, STOPWORDS_150)
    no_150_vocab = set(no_150_stop)
    print(f"{'150 stop words':<20}{len(no_150_vocab):>15}")

    stemmed = stem_tokens(no_150_stop)
    stemmed_vocab = set(stemmed)
    print(f"{'stemming':<20}{len(stemmed_vocab):>15}")

    # Part 2: Build compressed index and re-run the 6 sample queries
    print("\nBuilding compressed index...")
    compressed_F = build_compressed_term_docid_list(docs)
    compressed_sorted_F = sort_and_dedupe(compressed_F)
    compressed_index = build_index(compressed_sorted_F)
    print(f"Compressed index: {len(compressed_index)} unique terms")

    print("\n=== Single-term queries (compressed index) ===")
    for term in ["dollar", "wheat", "gold"]:
        stemmed_term = stemmer.stem(term)
        result = single_term_query(compressed_index, stemmed_term)
        print(f"'{term}' (stemmed: '{stemmed_term}'): {len(result)} documents -> {result[:10]}{'...' if len(result) > 10 else ''}")

    print("\n=== AND queries (compressed index) ===")
    and_pairs = [("gold", "dollar"), ("wheat", "dollar"), ("gold", "wheat")]
    for term1, term2 in and_pairs:
        s1, s2 = stemmer.stem(term1), stemmer.stem(term2)
        result = and_query(compressed_index, s1, s2)
        print(f"'{term1}' AND '{term2}' (stemmed: '{s1}' AND '{s2}'): {len(result)} documents -> {result[:10]}{'...' if len(result) > 10 else ''}")

        
import os
import re
from nltk.tokenize import RegexpTokenizer


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

# NLTK tokenizer: keeps runs of letters/digits, drops punctuation
_tokenizer = RegexpTokenizer(r"[A-Za-z0-9]+")


# PARSER 

def clean_text(text):
    """Replaces SGML entities (&#3; and named ones like &lt; &amp;) with a space."""
    return re.sub(r"&#?\w+;", " ", text)


def parse_sgm_file(filepath):
    """Parses one .sgm file and returns a list of (newid, title, body) tuples."""
    with open(filepath, "r", encoding="latin-1") as f:
        content = f.read()

    documents = re.findall(r"<REUTERS.*?>.*?</REUTERS>", content, re.DOTALL)
    return [parse_document(doc) for doc in documents]


def parse_document(doc_text):
    """Extracts (newid, title, body) from one <REUTERS>...</REUTERS> block."""
    newid_match = re.search(r'NEWID="(\d+)"', doc_text)
    newid = newid_match.group(1) if newid_match else None

    title_match = re.search(r"<TITLE>(.*?)</TITLE>", doc_text, re.DOTALL)
    title = title_match.group(1) if title_match else ""

    body_match = re.search(r"<BODY>(.*?)</BODY>", doc_text, re.DOTALL)
    body = body_match.group(1) if body_match else ""

    # Some documents (BRIEF / UNPROC types) have no TITLE or BODY tags.
    # Fall back to the raw <TEXT> content so they are not indexed as empty.
    if not title.strip() and not body.strip():
        text_match = re.search(r"<TEXT[^>]*>(.*?)</TEXT>", doc_text, re.DOTALL)
        if text_match:
            body = re.sub(r"<[^>]+>", " ", text_match.group(1))

    return newid, clean_text(title), clean_text(body)


def parse_all_files(data_dir=DATA_DIR):
    """Parses every .sgm file in data_dir; returns one list of (newid, title, body)."""
    all_docs = []
    for filename in sorted(os.listdir(data_dir)):
        if filename.endswith(".sgm"):
            all_docs.extend(parse_sgm_file(os.path.join(data_dir, filename)))
    return all_docs


#TOKENIZERS (NLTK) 

def tokenize_case_sensitive(text):
    """NLTK tokens keeping original case (used for the Table 5.1 experiment)."""
    return _tokenizer.tokenize(text)


def tokenize(text):
    """Lowercase NLTK tokens; punctuation is dropped."""
    return [t.lower() for t in _tokenizer.tokenize(text)]


#  Check how many documents use the <TEXT> fallback

def count_untagged_documents(data_dir=DATA_DIR):
    """Counts documents that have neither <TITLE> nor <BODY> tags."""
    count = 0
    for filename in sorted(os.listdir(data_dir)):
        if filename.endswith(".sgm"):
            with open(os.path.join(data_dir, filename), "r", encoding="latin-1") as f:
                content = f.read()
            for block in re.findall(r"<REUTERS.*?>.*?</REUTERS>", content, re.DOTALL):
                if "<TITLE>" not in block and "<BODY>" not in block:
                    count += 1
    return count


if __name__ == "__main__":
    docs = parse_all_files()
    print(f"Total documents parsed: {len(docs)}")

    empty = [d[0] for d in docs if not d[1].strip() and not d[2].strip()]
    print(f"Documents with empty title and body: {len(empty)}")

    print(f"Documents with neither TITLE nor BODY tags: {count_untagged_documents()}")

    newid, title, body = docs[0]
    print("First 20 tokens:", tokenize(title + " " + body)[:20])
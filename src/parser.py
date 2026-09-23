import re
import os


# PARSER FUNCTIONS
# it  extract (newid, title, body) from the raw Reuters .sgm files.


def parse_sgm_file(filepath):
    """
    Parses one .sgm file and returns a list of (newid, title, body) tuples.
    """
    with open(filepath, "r", encoding="latin-1") as f:
        content = f.read()

    documents = re.findall(r"<REUTERS.*?>.*?</REUTERS>", content, re.DOTALL)

    parsed_docs = []
    for doc in documents:
        newid, title, body = parse_document(doc)
        parsed_docs.append((newid, title, body))

    return parsed_docs


def parse_document(doc_text):
    """
    Extracts (newid, title, body) from a single <REUTERS>...</REUTERS> block.
    """
    # NEWID lives inside the opening tag: NEWID="123"
    newid_match = re.search(r'NEWID="(\d+)"', doc_text)
    newid = newid_match.group(1) if newid_match else None

    
    title_match = re.search(r"<TITLE>(.*?)</TITLE>", doc_text, re.DOTALL)
    title = title_match.group(1) if title_match else ""

    body_match = re.search(r"<BODY>(.*?)</BODY>", doc_text, re.DOTALL)
    body = body_match.group(1) if body_match else ""


    title = re.sub(r"&#\d+;", "", title)
    body = re.sub(r"&#\d+;", "", body)

    return newid, title, body


def parse_all_files(data_dir):
    """
    Parses every reut2-*.sgm file in data_dir and returns one combined list
    of (newid, title, body) tuples across the whole corpus.
    """
    all_docs = []
    for filename in sorted(os.listdir(data_dir)):
        if filename.endswith(".sgm"):
            filepath = os.path.join(data_dir, filename)
            docs = parse_sgm_file(filepath)
            all_docs.extend(docs)
    return all_docs



# TOKENIZER FUNCTION
# it converts raw title/body text into a clean list of lowercase and punctuation tokens

def tokenize(text):
    """
    Converts raw text into a list of clean, lowercase tokens.
    Strips punctuation entirely; splits on anything that isn't a letter or digit.
    """
    text = text.lower()
    tokens = re.findall(r"[a-z0-9]+", text)
    return tokens



# MAIN to test parsing and tokenization is working


if __name__ == "__main__":
    docs = parse_all_files("data")
    print(f"Total documents parsed: {len(docs)}")

    newid, title, body = docs[0]
    full_text = title + " " + body
    tokens = tokenize(full_text)
    print("First 20 tokens:", tokens[:20])

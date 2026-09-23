import re
import os

def parse_sgm_file(filepath):
    """
    Parses one .sgm file and returns a list of (newid, title, body) tuples.
    """
    with open(filepath, "r", encoding="latin-1") as f:
        content = f.read()

    # Split the file into individual <REUTERS>...</REUTERS> blocks
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

    # TITLE is optional in some documents
    title_match = re.search(r"<TITLE>(.*?)</TITLE>", doc_text, re.DOTALL)
    title = title_match.group(1) if title_match else ""

    # BODY is optional too (some short "BRIEF" stories have no BODY)
    body_match = re.search(r"<BODY>(.*?)</BODY>", doc_text, re.DOTALL)
    body = body_match.group(1) if body_match else ""

    # Clean stray SGML character references like &#3;
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


if __name__ == "__main__":
    docs = parse_all_files("data")
    print(f"Total documents parsed: {len(docs)}")
    print("First document:", docs[0])
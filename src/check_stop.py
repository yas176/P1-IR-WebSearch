# Diagnostic script: checks whether the sample query terms (dollar, dollars, wheat, gold) are among the 150 most frequent corpus terms used as stop words, 
#to explain why 'dollar' loses documents in the compressed index.


from reuters_parser import parse_all_files, tokenize_case_sensitive
from compression import case_fold, remove_numbers, top_terms

docs = parse_all_files()
lists = [remove_numbers(case_fold(tokenize_case_sensitive(t + " " + b))) for _, t, b in docs]
top150 = top_terms(lists, 150)

for w in ["dollar", "dollars", "wheat", "gold"]:
    rank = top150.index(w) + 1 if w in top150 else None
    print(f"{w}: in top 150 = {w in top150}, rank = {rank}")

print("Documents containing 'dollars':", sum(1 for l in lists if "dollars" in l))
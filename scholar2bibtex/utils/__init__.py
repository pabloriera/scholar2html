"""Utility modules for Scholar2BibTeX.""" 

from IPython import embed
from difflib import SequenceMatcher 


def remove_duplicates(citations, entries):
    """Remove duplicates from the citations by looking repated titles in entries."""
    titles = [e['fields']['title'] for e in entries]
    
    for i, title_a in enumerate(titles):
        for j, title_b in enumerate(titles):
            if i == j:
                continue
            seq = SequenceMatcher(None, title_a, title_b)
            if seq.ratio() > 0.9:
                print(f"Duplicate: {title_a} and {title_b}")
                citations.pop(j)
                entries.pop(j)
        
    
    return citations, entries

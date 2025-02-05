"""Utility modules for Scholar2BibTeX.""" 

from difflib import SequenceMatcher 

def same_text(text_a, text_b, threshold=0.9):
    """Check if two texts are similar."""
    seq = SequenceMatcher(None, text_a, text_b)
    return seq.ratio() > threshold

def remove_duplicates(entries):
    """Remove duplicates by looking repated titles in entries."""
    titles = [e['fields']['title'].lower() for e in entries]
    
    print(f"Got {len(entries)} entries")

    for i, entry_a in enumerate(entries):
        title_a = entry_a['fields']['title'].lower()
        for j, entry_b in enumerate(entries):
            if i == j:
                continue
            title_b = entry_b['fields']['title'].lower()
            if same_text(title_a, title_b):
                print(f"Duplicate: {title_a} and {title_b}")
                # pop entry with method 'scholar' if it exists
                if entry_a['method'] == 'scholar':
                    entries.pop(i)
                elif entry_b['method'] == 'scholar':
                    entries.pop(j)
                else:
                    entries.pop(j)
        
    print(f"Got unique {len(entries)} entries")
    return entries

"""Main script to generate citations from Google Scholar."""
import json
import os
from typing import Dict, List, Tuple, Any
import argparse
from ..utils.downloader import CitationDownloader
from ..utils.renderer import CitationRenderer

def load_config(config_path: str) -> Dict:
    """Load configuration from JSON file."""
    with open(config_path, 'r') as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description='Generate citations from Google Scholar')
    parser.add_argument('--config', default='config/config.json', help='Path to configuration file')
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    output_dir = config.get('output_dir', 'output')
    style = config.get('style', 'plain')
    mandatory_fields = config.get('mandatory_fields', ['year'])
    
    # Initialize components
    downloader = CitationDownloader()
    renderer = CitationRenderer(style_name=style)
    
    # Lists to store all citations and entries
    all_citations: List[Tuple[int, str]] = []
    all_entries: List[Dict[str, Any]] = []
    
    # Process each citation
    for citation in config['citations']:
        user_id = citation['user_id']
        code = citation['code']
        name = citation.get('name', user_id)
        
        print(f"Processing citations for {name}...")
        
        # Download BibTeX file
        bibtex_file = downloader.download_citations(user_id, code, output_dir)
        if not bibtex_file:
            print(f"Failed to download citations for {name}")
            continue
            
        # Load and render citations
        bib_data = renderer.load_bibtex(bibtex_file)
        citations, entries = renderer.render_citations(bib_data, mandatory_fields=mandatory_fields)
        
        # Generate individual HTML and JSON
        html_file = os.path.join(output_dir, f"{user_id}.html")
        json_file = os.path.join(output_dir, f"{user_id}.json")
        
        output_path = renderer.generate_html(citations, html_file, title=f"Citations for {name}")
        renderer.save_json(entries, json_file)
        
        print(f"Generated files for {name}:")
        print(f"  HTML: {output_path}")
        print(f"  JSON: {json_file}")
        
        # Add to combined lists
        all_citations.extend(citations)
        all_entries.extend(entries)
    
    # Generate combined files
    if all_citations:
        # Sort and remove duplicates from combined citations
        all_citations.sort(key=lambda x: (x[0], x[1]), reverse=True)
        all_citations = list(dict.fromkeys(map(tuple, all_citations)))
        
        # Generate combined HTML
        all_html_file = os.path.join(output_dir, "all.html")
        renderer.generate_html(all_citations, all_html_file, title="All Citations")
        
        # Generate combined JSON
        all_json_file = os.path.join(output_dir, "all.json")
        renderer.save_json(all_entries, all_json_file)
        
        print("\nGenerated combined files:")
        print(f"  HTML: {all_html_file}")
        print(f"  JSON: {all_json_file}")

if __name__ == "__main__":
    main() 
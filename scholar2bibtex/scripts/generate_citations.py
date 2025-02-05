"""Main script to generate citations from Google Scholar."""
import json
import os
from typing import Dict, List, Tuple, Any
import argparse


from scholar2bibtex.utils import remove_duplicates
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
    
    # Lists to store all citations and entries
    all_citations: List[Tuple[int, str]] = []
    all_entries: List[Dict[str, Any]] = []
    
    # Process each citation
    for citation in config['users']:

        # Initialize components
        downloader = CitationDownloader()
        renderer = CitationRenderer(style_name=style)

        name = citation.get('name').replace(" ", "_")
        method = citation['method']
        
        print(f"Processing citations for {name}, method: {method}")
        
        if method == 'scholar':
            user_id = citation['user_id']
            code = citation['code']
            # Download BibTeX file
            bibtex_file = downloader.download_citations(user_id, code, output_dir)
            if not bibtex_file:
                print(f"Failed to download citations for {name}")
                continue
        elif method == 'bibtex':
            bibtex_file = citation['bibtex_file']
        else:
            print(f"Invalid method: {method}")
            continue
            
        # Load and render citations
        bib_data = renderer.load_bibtex(bibtex_file)
        entries = renderer.render_citations(
            bib_data,
            method=method,
            name=name,
            mandatory_fields=mandatory_fields,
            skip_titles=config.get("skip_titles", None),
        )

        # Generate individual HTML and JSON
        html_file = os.path.join(output_dir, f"{name}_{method}.html")
        json_file = os.path.join(output_dir, f"{name}_{method}.json")
        
        output_path = renderer.generate_html(entries, html_file, title=f"Citations for {name}")
        renderer.save_json(entries, json_file)
        
        print(f"Generated files for {name}:")
        print(f"  HTML: {output_path}")
        print(f"  JSON: {json_file}")
        
        # Add to combined lists
        all_entries.extend(entries)
    
    # Remove duplicates
    all_entries = remove_duplicates(all_entries)

    # Generate combined files
    if all_entries:
        # Initialize components
        renderer = CitationRenderer(style_name=style)
        
        # Generate combined HTML
        all_html_file = os.path.join(output_dir, "all.html")
        renderer.generate_html(all_entries, all_html_file)
        
        # Generate combined JSON
        all_json_file = os.path.join(output_dir, "all.json")
        renderer.save_json(all_entries, all_json_file)
        
        print("\nGenerated combined files:")
        print(f"  HTML: {all_html_file}")
        print(f"  JSON: {all_json_file}")

if __name__ == "__main__":
    main() 
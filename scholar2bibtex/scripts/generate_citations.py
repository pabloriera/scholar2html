"""Main script to generate citations from Google Scholar."""
import json
import os
from typing import Dict
import argparse
from ..utils.downloader import CitationDownloader
from ..utils.renderer import CitationRenderer

def load_config(config_path: str) -> Dict:
    """Load configuration from JSON file."""
    with open(config_path, 'r') as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description='Generate citations from Google Scholar')
    parser.add_argument('--config', default='config.json', help='Path to configuration file')
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    output_dir = config.get('output_dir', 'output')
    style = config.get('style', 'plain')
    mandatory_fields = config.get('mandatory_fields', ['year'])
    
    # Initialize components
    downloader = CitationDownloader()
    renderer = CitationRenderer(style_name=style)
    
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
        citations = renderer.render_citations(bib_data, mandatory_fields=mandatory_fields)
        
        # Generate HTML
        html_file = os.path.join(output_dir, f"{user_id}.html")
        output_path = renderer.generate_html(citations, html_file)
        print(f"Generated HTML file: {output_path}")

if __name__ == "__main__":
    main() 
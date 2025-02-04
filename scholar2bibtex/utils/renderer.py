"""Module for rendering citations in various formats."""
from typing import List, Tuple, Optional
from pybtex.database.input import bibtex
from pybtex.plugin import find_plugin
import os

class CitationRenderer:
    """Class to handle citation rendering and formatting."""
    
    def __init__(self, style_name: str = "plain"):
        self.style_name = style_name
        self.parser = bibtex.Parser()
        self.style = find_plugin('pybtex.style.formatting', style_name)()
        self.style_plain = find_plugin('pybtex.style.formatting', "plain")()
        
    def load_bibtex(self, file_path: str):
        """Load a BibTeX file."""
        return self.parser.parse_file(file_path)
        
    def render_citations(self, bib_data, mandatory_fields: List[str] = None) -> List[Tuple[int, str]]:
        """
        Render citations in the specified format.
        
        Args:
            bib_data: Loaded BibTeX data
            mandatory_fields: List of required fields for each entry
            
        Returns:
            List of tuples containing (year, formatted_citation)
        """
        if mandatory_fields is None:
            mandatory_fields = ["year"]
            
        formatted_output = []
        
        for entry in bib_data.entries.values():
            if 'year' not in entry.fields:
                continue
                
            # Check for mandatory fields
            if not all(field in entry.fields for field in mandatory_fields):
                continue
                
            year = int(entry.fields['year'])
            
            try:
                formatted_entry = list(self.style.format_entries([entry]))[0]
                formatted_output.append((year, formatted_entry.text.render_as('text')))
            except Exception as e:
                print(f"Error rendering entry: {entry.key} with style {self.style_name}. Error: {e}")
                try:
                    formatted_entry = list(self.style_plain.format_entries([entry]))[0]
                    formatted_output.append((year, formatted_entry.text.render_as('text')))
                except Exception as e:
                    print(f"Error rendering entry: {entry.key} with style plain. Error: {e}")
                    
        return formatted_output
        
    def generate_html(self, citations: List[Tuple[int, str]], output_file: str) -> str:
        """
        Generate HTML output for the citations.
        
        Args:
            citations: List of (year, citation) tuples
            output_file: Path to save the HTML file
            
        Returns:
            Absolute path to the generated HTML file
        """
        # Sort citations by year in descending order
        citations.sort(key=lambda x: x[0], reverse=True)
        
        # Create HTML content
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                table { border-collapse: collapse; width: 100%; }
                th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #f2f2f2; }
                tr:hover { background-color: #f5f5f5; }
            </style>
        </head>
        <body>
        <table>
            <tr><th>Year</th><th>Citation</th></tr>
        """
        
        for year, citation in citations:
            html += f"<tr><td>{year}</td><td>{citation}</td></tr>"
            
        html += """
        </table>
        </body>
        </html>
        """
        
        # Save HTML file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
            
        return os.path.abspath(output_file) 
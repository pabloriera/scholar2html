"""Module for rendering citations in various formats."""

from typing import List, Tuple, Optional, Dict, Any
from IPython import embed
from pybtex.database.input import bibtex
from pybtex.plugin import find_plugin
import os
import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin

from scholar2bibtex.utils import same_text


class CitationRenderer:
    """Class to handle citation rendering and formatting."""

    def __init__(self, style_name: str = "plain"):
        self.style_name = style_name
        self.parser = bibtex.Parser()
        self.style = find_plugin("pybtex.style.formatting", style_name)()
        self.style_plain = find_plugin("pybtex.style.formatting", "plain")()

    def load_bibtex(self, file_path: str):
        """
        Load a BibTeX file, handling duplicate entry keys by adding a counter.

        Args:
            file_path: Path to the BibTeX file

        Returns:
            Parsed BibTeX data with unique entry keys
        """
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Find all entry keys in the content
        entry_keys = {}
        pattern = r"@\w+{([^,]+),"

        # First pass: count occurrences of each key
        for match in re.finditer(pattern, content):
            key = match.group(1).strip()
            entry_keys[key] = entry_keys.get(key, 0) + 1

        # Second pass: modify duplicate keys
        modified_content = content
        for key, count in entry_keys.items():
            if count > 1:
                print(f"Found {count} entries with key '{key}', adding counters...")
                # Replace all occurrences with numbered versions
                counter = 1
                pattern = f"@(\\w+){{{key},"
                while counter <= count:
                    # Replace only the first occurrence in the remaining text
                    new_key = f"{key}_{counter}"
                    match = re.search(pattern, modified_content)
                    if match:
                        entry_type = match.group(1)
                        old = f"@{entry_type}{{{key},"
                        new = f"@{entry_type}{{{new_key},"
                        modified_content = modified_content.replace(old, new, 1)
                    counter += 1

        # Parse the modified content
        return self.parser.parse_string(modified_content)

    def _entry_to_dict(self, entry) -> Dict[str, Any]:
        """Convert a BibTeX entry to a dictionary."""
        return {
            "key": entry.key,
            "type": entry.type,
            "fields": dict(entry.fields),
            "persons": {
                role: [str(person) for person in persons]
                for role, persons in entry.persons.items()
            },
        }

    def render_citations(
        self,
        bib_data,
        method: str,
        name: str,
        mandatory_fields: List[str] = None,
        skip_titles: List[str] = None,
    ) -> Tuple[List[Tuple[int, str]], List[Dict[str, Any]]]:
        """
        Render citations in the specified format.

        Args:
            bib_data: Loaded BibTeX data
            mandatory_fields: List of required fields for each entry

        Returns:
            Tuple containing:
            - List of tuples containing (year, formatted_citation)
            - List of dictionaries containing raw citation data
        """
        if mandatory_fields is None:
            mandatory_fields = ["year"]

        entries = []

        for entry in bib_data.entries.values():

            # if title in skip_titles, skip
            if any(same_text(entry.fields["title"], title) for title in skip_titles):
                continue

            if "year" not in entry.fields:
                continue

            # Check for mandatory fields
            if not all(field in entry.fields for field in mandatory_fields):
                continue

            year = int(entry.fields["year"])
            entry_dict = self._entry_to_dict(entry)
            entry_dict["year"] = year
            entry_dict["name"] = name
            entry_dict["method"] = method
            url = self.get_scholar_link(entry.fields["title"])
            entry_dict["url"] = url
            formatted_output = ""
            try:
                formatted_entry = list(self.style.format_entries([entry]))[0]
                formatted_output = formatted_entry.text.render_as("text")
            except Exception as e:
                print(
                    f"Error rendering entry: {entry.key} with style {self.style_name}. Error: {e}"
                )
                try:
                    formatted_entry = list(self.style_plain.format_entries([entry]))[0]
                    formatted_output = formatted_entry.text.render_as("text")
                except Exception as e:
                    print(
                        f"Error rendering entry: {entry.key} with style plain. Error: {e}"
                    )

            entry_dict["citation"] = formatted_output
            entries.append(entry_dict)

        return entries

    def generate_html(
        self, entries: List[Dict[str, Any]], output_file: str, title: str = None
    ) -> str:
        """
        Generate HTML output for the citations with name-based filtering.

        Args:
            citations: List of (year, citation) tuples
            output_file: Path to save the HTML file
            title: Optional title for the HTML page

        Returns:
            Absolute path to the generated HTML file
        """
        # Sort citations by year in descending order
        entries.sort(key=lambda x: x["year"], reverse=True)

        # Get unique names
        unique_names = sorted(list(set(entry["name"] for entry in entries)))

        # Create HTML content
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #f2f2f2; }
                tr:hover { 
                    background-color: #f5f5f5;
                    text-decoration: underline;
                    color: #0066cc;
                    cursor: pointer;
                }
                h1 { color: #333; }
                .filter-links { margin-bottom: 20px; }
                .filter-links a {
                    margin-right: 15px;
                    text-decoration: none;
                    color: #0066cc;
                    padding: 5px 10px;
                    border-radius: 3px;
                    cursor: pointer;
                }
                .filter-links a.active {
                    background-color: #0066cc;
                    color: white;
                }
                .hidden { display: none; }
            </style>
            <script>
                function filterByName(name) {
                    const rows = document.querySelectorAll('table tr[data-name]');
                    const links = document.querySelectorAll('.filter-links a');
                    
                    links.forEach(link => {
                        if (link.getAttribute('data-name') === name || (name === 'all' && link.getAttribute('data-name') === 'all')) {
                            link.classList.add('active');
                        } else {
                            link.classList.remove('active');
                        }
                    });
                    
                    rows.forEach(row => {
                        if (name === 'all' || row.getAttribute('data-name') === name) {
                            row.classList.remove('hidden');
                        } else {
                            row.classList.add('hidden');
                        }
                    });
                }

                function openUrl(url) {
                    window.open(url, '_blank');
                }
            </script>
        </head>
        <body>
        """

        if title:
            html += f"<h1>{title}</h1>"

        # Add filter links
        html += '<div class="filter-links">\n'
        html += f'<a onclick="filterByName(\'all\')" data-name="all" class="active">All</a>\n'
        for name in unique_names:
            name2 = name.replace("_", " ")
            html += f'<a onclick="filterByName(\'{name}\')" data-name="{name}">{name2}</a>\n'
        html += "</div>\n"

        html += """
        <table>
            <tr><th>Year</th><th>Citation</th></tr>
        """

        for entry in entries:
            if entry["citation"] == "":
                continue
            html += f'<tr data-name="{entry["name"]}" onclick="openUrl(\'{entry["url"]}\')">'
            html += f'<td>{entry["year"]}</td><td>{entry["citation"]}</td></tr>'

        html += """
        </table>
        </body>
        </html>
        """

        # Save HTML file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)

        return os.path.abspath(output_file)

    def save_json(self, entries: List[Dict[str, Any]], output_file: str) -> str:
        """
        Save citation data as JSON.

        Args:
            entries: List of citation entries
            output_file: Path to save the JSON file

        Returns:
            Absolute path to the generated JSON file
        """
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)

        return os.path.abspath(output_file)

    def get_scholar_link(self, title: str, retrieve_url: bool = False) -> str:
        """
        Search Google Scholar for a paper title and return its URL if found.

        Args:
            title: The title of the paper to search for

        Returns:
            str: The direct URL to the paper if found, otherwise the Google Scholar search URL
        """

        # Headers to mimic a browser request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://google.com",
            "Connection": "keep-alive",
        }

        # Construct the search URL
        search_query = quote_plus(title)
        scholar_url = f"https://scholar.google.com/scholar?q={search_query}"

        if retrieve_url:
            try:
                # Make the request to Google Scholar
                response = requests.get(scholar_url, headers=headers, timeout=2)
                response.raise_for_status()

                # Parse the HTML response
                soup = BeautifulSoup(response.text, "html.parser")

                # Look for the div with class gs_or_ggsm
                result_div = soup.find("div", class_="gs_or_ggsm")

                if result_div:
                    # Find the first anchor tag within this div
                    link = result_div.find("a")
                    if link and "href" in link.attrs:
                        # Return the absolute URL
                        return link["href"]

                # If no specific result found, return the search URL
                return scholar_url

            except Exception as e:
                print(f"Error searching Google Scholar: {e}")
                return scholar_url
        else:
            return scholar_url

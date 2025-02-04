# Scholar2BibTeX

A Python package to download and render Google Scholar citations in BibTeX format. This tool automatically downloads citations from specified Google Scholar profiles and generates formatted HTML output.

## Features

- Download citations from multiple Google Scholar profiles
- Convert BibTeX entries to formatted citations
- Generate clean HTML output with citations sorted by year
- Automatic weekly updates via GitHub Actions

## Installation

```bash
git clone https://github.com/yourusername/scholar2bibtex.git
cd scholar2bibtex
pip install .
```

## Configuration

Create a `config.json` file with the following structure:

```json
{
    "output_dir": "output",
    "citations": [
        {
            "user_id": "GOOGLE_SCHOLAR_USER_ID",
            "code": "CITATION_CODE",
            "name": "Author Name"
        }
    ],
    "style": "apa",
    "mandatory_fields": ["year", "journal", "title"]
}
```

### Configuration Fields

- `output_dir`: Directory where BibTeX and HTML files will be saved
- `citations`: List of Google Scholar profiles to process
  - `user_id`: Google Scholar user ID (found in profile URL)
  - `code`: Citation export code (from Google Scholar)
  - `name`: Display name for the author (optional)
- `style`: Citation style (e.g., "apa", "plain")
- `mandatory_fields`: Required fields for each citation

## Usage

Run the citation generator:

```bash
python -m scholar2bibtex.scripts.generate_citations --config config.json
```

## GitHub Actions

The repository includes a GitHub Actions workflow that automatically updates citations every Sunday. The workflow:

1. Checks out the repository
2. Sets up Python
3. Installs dependencies
4. Runs the citation generator
5. Commits and pushes any changes

You can also trigger the workflow manually through the GitHub Actions interface.

## License

MIT License 
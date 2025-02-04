"""Module for downloading citations from Google Scholar."""
import requests
import os
from typing import Dict, Optional

class CitationDownloader:
    """Class to handle downloading citations from Google Scholar."""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://google.com",
            "Connection": "keep-alive",
        }
    
    def download_citations(self, user_id: str, code: str, output_dir: str) -> Optional[str]:
        """
        Download citations for a specific user.
        
        Args:
            user_id: Google Scholar user ID
            code: Citation signature code
            output_dir: Directory to save the BibTeX file
            
        Returns:
            Path to the downloaded file if successful, None otherwise
        """
        url = f"https://scholar.googleusercontent.com/citations?view_op=export_citations&user={user_id}&citsig={code}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"{user_id}.bib")
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(response.text)
                
            return output_file
            
        except requests.RequestException as e:
            print(f"Error downloading citations for user {user_id}: {str(e)}")
            return None 
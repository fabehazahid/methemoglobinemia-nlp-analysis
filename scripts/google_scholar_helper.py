"""Google Scholar Helper -  Creates search URLs for finding PDFs
Since Google Scholar blocks automated scraping, this creates manual search links"""

import pandas as pd
from pathlib import Path
import webbrowser

def create_google_scholar_search_urls(title=None, author=None):
    """Read PubMed metadata and create Google Scholar search URLs
    This helps you manually find PDFs for each abstract
    """
    print("=" * 70)
    print("GOOGLE SCHOLAR PDF FINDER HELPER")
    print("=" * 70)
    print()
    # Read this Pubmed metadata 
    metadata_file = 'data/PDFs and abstracts/pubmed_metadata.csv'
    try:
        df = pd.read_csv(metadata_file)
        print(f"Loaded metadata from {metadata_file} ({len(df)} records)")
    except FileNotFoundError:
        print(f"Metadata file not found: {metadata_file}")
        return
    # Create Google Scholar URLs
    scholar_urls = []
    for index, row in df.iterrows():
        title = row['title']
        pmid = row['pmid']
        
        # Create Google Scholar search URL
        # Remove special characters and create search query
        search_query = title.replace(' ', '+').replace(':', '').replace(',', '')
        scholar_url = f"https://scholar.google.com/scholar?q={search_query}"
        
        scholar_urls.append({
            'pmid': pmid,
            'title': title,
            'google_scholar_url': scholar_url,
            'pdf_found': 'No',  # User can fill this in manually
            'notes': ''
        })
    
    # Save to CSV
    output_file = 'data/PDFs and abstracts/google_scholar_search_urls.csv'
    scholar_df = pd.DataFrame(scholar_urls)
    scholar_df.to_csv(output_file, index=False)
    print(f"Created {len(scholar_urls)} Google Scholar search URLs")
    print(f"Saved to: {output_file}\n")

    print("=" * 70)
    print("HOW TO USE THIS FILE:")
    print("=" * 70)
    print("1. Open 'google_scholar_search_urls.csv' in Excel")
    print("2. Click each Google Scholar URL")
    print("3. Look for [PDF] links on the right side of results")
    print("4. Download PDFs and save to 'data/PDFs and abstracts/'")
    print("5. Name them as: PMID_######.pdf")
    print("6. Mark 'pdf_found' as 'Yes' in the CSV when downloaded")
    print("=" * 70)
    
    return scholar_df

# Function to open first N searches in browser
def open_first_n_searches(n=5):
    """
    Open first N Google Scholar searches in browser tabs
    
    Args:
        n (int): Number of searches to open (default 5)
    """
    try:
        df = pd.read_csv('data/PDFs and abstracts/google_scholar_search_urls.csv')
        
        print(f"\nOpening first {n} Google Scholar searches in browser...")
        print("(Check for [PDF] links on the right side)\n")
        
        # Specify Firefox as the browser
        try:
            browser = webbrowser.get('firefox')  # Change 'firefox' to 'chrome', 'opera', etc., as needed
        except webbrowser.Error:
            print("Firefox not found. Using default browser.")
            browser = webbrowser  # Fallback to default
        
        for index, row in df.head(n).iterrows():
            print(f"Opening: {row['title'][:60]}...")
            browser.open(row['google_scholar_url'])
        
        print(f"\nOpened {n} tabs in your browser!")
        
    except FileNotFoundError:
        print("Run create_google_scholar_search_urls() first!")

if __name__ == "__main__":
    # Create the search list
    create_google_scholar_search_urls()
    
    # Ask user if they want to open searches
    print("\nWould you like to open the first 5 searches in your browser?")
    print("   (This helps you start downloading PDFs quickly)")
    response = input("   Enter 'yes' to open: ").strip().lower()
    
    if response == 'yes' or response == 'y':
        open_first_n_searches(5)
    else:
        print("\nYou can manually open URLs from 'google_scholar_search_urls.csv'")
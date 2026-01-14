"""
PubMed Abstract Downloader using NCBI Entrez API
Downloads abstracts for methemoglobinemia case reports
"""

from Bio import Entrez
import time
import pandas as pd
from pathlib import Path
import os


Entrez.email = "fabehazahid@gmail.com"  

def search_pubmed(query, max_results=50):
    """
    Search PubMed and return list of article IDs (PMIDs)
    
    Args:
        query (str): Search query (e.g., "methemoglobinemia case report")
        max_results (int): Maximum number of results to return
        
    Returns:
        list: PubMed IDs (PMIDs)
    """
    print(f" Searching PubMed for: '{query}'")
    print(f"Requesting up to {max_results} results...\n")
    
    try:
        # Send search request to PubMed API
        handle = Entrez.esearch(
            db="pubmed",           # Database to search
            term=query,            # Search terms
            retmax=max_results,    # Max results
            sort="relevance"       # Sort by relevance
        )
        
        # Parse the XML response
        record = Entrez.read(handle)
        handle.close()
        
        # Extract list of PMIDs from response
        id_list = record["IdList"]
        print(f"Found {len(id_list)} articles\n")
        return id_list
        
    except Exception as e:
        print(f"Error searching PubMed: {e}")
        return []

def fetch_abstract(pmid):
    """
    Fetch abstract and metadata for a single PubMed ID
    
    Args:
        pmid (str): PubMed ID
        
    Returns:
        dict: Article metadata and abstract text
    """
    try:
        # Fetch article details from PubMed
        handle = Entrez.efetch(
            db="pubmed",
            id=pmid,
            rettype="abstract",
            retmode="xml"
        )
        
        # Parse the XML response
        records = Entrez.read(handle)
        handle.close()
        
        # Navigate the nested structure to get article data
        article = records['PubmedArticle'][0]['MedlineCitation']['Article']
        
        # Extract abstract text
        abstract_text = ""
        if 'Abstract' in article:
            abstract_parts = article['Abstract']['AbstractText']
            if isinstance(abstract_parts, list):
                abstract_text = " ".join([str(part) for part in abstract_parts])
            else:
                abstract_text = str(abstract_parts)
        
        # Extract metadata
        metadata = {
            'pmid': pmid,
            'title': article.get('ArticleTitle', 'N/A'),
            'abstract': abstract_text,
            'journal': article.get('Journal', {}).get('Title', 'N/A'),
            'pub_year': article.get('Journal', {}).get('JournalIssue', {}).get('PubDate', {}).get('Year', 'N/A'),
            'authors': ', '.join([
                f"{author.get('LastName', '')} {author.get('Initials', '')}"
                for author in article.get('AuthorList', [])[:3]  # First 3 authors
            ])
        }
        
        return metadata
        
    except Exception as e:
        print(f"Error fetching PMID {pmid}: {e}")
        return None

def download_pubmed_abstracts(query, max_results=50, output_folder='data/PDFs and abstracts'):
    """
    Search PubMed, download abstracts, and save to files
    
    Args:
        query (str): Search query
        max_results (int): Maximum results to download
        output_folder (str): Folder to save abstracts
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    print("=" * 70)
    print(" PUBMED ABSTRACT DOWNLOADER")
    print("=" * 70)
    print()
    
    # Step 1: Search PubMed
    pmids = search_pubmed(query, max_results)
    
    if not pmids:
        print("⚠️  No results found!")
        return
    
    # Step 2: Download abstracts
    print(f"📥 Downloading abstracts...\n")
    all_metadata = []
    
    for i, pmid in enumerate(pmids, 1):
        print(f"[{i}/{len(pmids)}] Fetching PMID: {pmid}")
        
        # Fetch abstract and metadata
        metadata = fetch_abstract(pmid)
        
        if metadata and metadata['abstract']:
            # Save abstract to text file
            filename = f"abstract_{pmid}.txt"
            filepath = Path(output_folder) / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"PMID: {pmid}\n")
                f.write(f"Title: {metadata['title']}\n")
                f.write(f"Journal: {metadata['journal']}\n")
                f.write(f"Year: {metadata['pub_year']}\n")
                f.write(f"Authors: {metadata['authors']}\n")
                f.write(f"\n{'='*80}\n\n")
                f.write(f"ABSTRACT:\n{metadata['abstract']}")
            
            metadata['filename'] = filename
            all_metadata.append(metadata)
            
            print(f"  ✅ Saved: {filename}")
        else:
            print(f"  ⚠️  No abstract available for PMID {pmid}")
        
        # Be polite to NCBI servers - wait between requests
        # NCBI allows 3 requests/second without API key
        time.sleep(0.4)
        print()
    
    # Step 3: Save metadata CSV
    if all_metadata:
        df = pd.DataFrame(all_metadata)
        csv_path = Path(output_folder) / 'pubmed_metadata.csv'
        df.to_csv(csv_path, index=False)
        
        print("=" * 70)
        print(f"Metadata saved to: {csv_path}")
        print(f"Successfully downloaded {len(all_metadata)} abstracts!")
        print(f"Files saved in: {output_folder}")
        print("=" * 70)
    else:
        print("No abstracts were downloaded")

if __name__ == "__main__":
    # Configuration
    search_query = "methemoglobinemia case report"
    max_results = 30  # Start with 30, can increase later
    
    # Run the downloader
    download_pubmed_abstracts(
        query=search_query,
        max_results=max_results,
        output_folder='data/PDFs and abstracts'
    )
    
    print("\nTIP: Check the 'data/PDFs and abstracts' folder for your downloaded abstracts!")
    print("Next step: Run the PMC PDF finder to get full-text PDFs")
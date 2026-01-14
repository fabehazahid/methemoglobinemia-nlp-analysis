"""
Phase 2A: Extract Text from PDFs and Abstracts
Reads all documents and creates a single CSV with all text content
"""

import PyPDF2
from pathlib import Path
import pandas as pd
import os

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        str: Extracted text content
    """
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            
            print(f"  Reading {len(reader.pages)} pages...")
            
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                text += page_text + "\n"
            
            return text
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

def extract_text_from_abstract(txt_path):
    """
    Read text from abstract file
    
    Args:
        txt_path: Path to text file
        
    Returns:
        str: Abstract text content
    """
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

def process_all_documents():
    """
    Process all PDFs and abstracts in the data folder
    """
    
    print("=" * 70)
    print("📄 TEXT EXTRACTION FROM DOCUMENTS")
    print("=" * 70)
    print()
    
    # Define paths
    data_folder = Path('data/PDFs and abstracts')
    output_folder = Path('data/processed')
    
    # Create output folder
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Find all abstracts (text files)
    abstracts = list(data_folder.glob('abstract_*.txt'))
    
    # Find all PDFs
    pdfs = list(data_folder.glob('*.pdf'))
    
    print(f"Found {len(abstracts)} abstracts and {len(pdfs)} PDFs\n")
    
    all_documents = []
    
    # Process abstracts
    print("📝 Processing Abstracts...")
    print("-" * 70)
    
    for i, abstract_file in enumerate(abstracts, 1):
        # Extract PMID from filename
        pmid = abstract_file.stem.replace('abstract_', '')
        
        print(f"[{i}/{len(abstracts)}] PMID {pmid}")
        
        text = extract_text_from_abstract(abstract_file)
        
        if text:
            all_documents.append({
                'pmid': pmid,
                'source_file': abstract_file.name,
                'source_type': 'abstract',
                'text_length': len(text),
                'text': text
            })
            print(f"  ✅ Extracted {len(text)} characters\n")
        else:
            print(f"  ⚠️ Failed to extract\n")
    
    # Process PDFs
    if pdfs:
        print("\n📄 Processing PDFs...")
        print("-" * 70)
        
        for i, pdf_file in enumerate(pdfs, 1):
            # Try to extract PMID from filename
            # Handles formats like: PMID_12345.pdf, PMC12345.pdf, paper_title.pdf
            filename = pdf_file.stem
            
            if 'PMID' in filename or 'PMC' in filename:
                pmid = filename.replace('PMID_', '').replace('PMC', '')
            else:
                pmid = f"PDF_{i}"  # Fallback ID
            
            print(f"[{i}/{len(pdfs)}] {pdf_file.name} (ID: {pmid})")
            
            text = extract_text_from_pdf(pdf_file)
            
            if text:
                all_documents.append({
                    'pmid': pmid,
                    'source_file': pdf_file.name,
                    'source_type': 'pdf',
                    'text_length': len(text),
                    'text': text
                })
                print(f"  ✅ Extracted {len(text)} characters\n")
            else:
                print(f"  ⚠️ Failed to extract\n")
    
    # Save to CSV
    if all_documents:
        df = pd.DataFrame(all_documents)
        output_file = output_folder / 'extracted_texts.csv'
        df.to_csv(output_file, index=False)
        
        print("=" * 70)
        print("✅ EXTRACTION COMPLETE!")
        print("=" * 70)
        print(f"\n📊 Summary:")
        print(f"  Total documents processed: {len(all_documents)}")
        print(f"  Abstracts: {len(abstracts)}")
        print(f"  PDFs: {len([d for d in all_documents if d['source_type'] == 'pdf'])}")
        print(f"\n💾 Saved to: {output_file}")
        print("\n🎯 Next step: Run 'python scripts/nlp_extraction.py'")
        print("=" * 70)
        
    else:
        print("❌ No documents were processed!")
        print("   Make sure you have files in 'data/PDFs and abstracts/'")

if __name__ == "__main__":
    process_all_documents()
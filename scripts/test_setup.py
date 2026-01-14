"""
Test script to verify all dependencies are properly installed
Run this before running the main scraping scripts
"""

def test_imports():
    """Test all required package imports"""
    
    print("=" * 70)
    print(" TESTING PACKAGE IMPORTS")
    print("=" * 70)
    print()
    
    packages = {
        'beautifulsoup4': 'bs4',
        'requests': 'requests',
        'PyPDF2': 'PyPDF2',
        'spacy': 'spacy',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'plotly': 'plotly',
        'seaborn': 'seaborn',
        'matplotlib': 'matplotlib',
        'streamlit': 'streamlit',
        'nltk': 'nltk',
        'biopython': 'Bio'
    }
    
    failed = []
    
    for package_name, import_name in packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name:20s} - OK")
        except ImportError:
            print(f"❌ {package_name:20s} - NOT INSTALLED")
            failed.append(package_name)
    
    print()
    print("-" * 70)
    
    # Test spaCy model
    print("\n🔤 Testing spaCy model...")
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy 'en_core_web_sm' model loaded successfully")
        
        # Test it on sample text
        doc = nlp("Methemoglobinemia was measured at 35%.")
        print(f"   Sample text processed: {len(doc)} tokens detected")
        
    except OSError:
        print("❌ spaCy model 'en_core_web_sm' not found")
        print("   Run: python -m spacy download en_core_web_sm")
        failed.append('spacy model')
    except Exception as e:
        print(f"❌ Error loading spaCy: {e}")
        failed.append('spacy model')
    
    # Test Biopython Entrez
    print("\n🧬 Testing Biopython Entrez...")
    try:
        from Bio import Entrez
        print("✅ Biopython Entrez module loaded")
        print("   Ready for PubMed API access")
    except ImportError:
        print("❌ Biopython not installed")
        print("   Run: pip install biopython")
        failed.append('biopython')
    
    # Summary
    print()
    print("=" * 70)
    if not failed:
        print("🎉 ALL TESTS PASSED! Your environment is ready!")
        print()
        print("Next steps:")
        print("1. Edit 'scripts/pubmed_scraper.py' - add your email")
        print("2. Run: python scripts/pubmed_scraper.py")
        print("3. Run: python scripts/pmc_pdf_finder.py")
    else:
        print(f"⚠️  {len(failed)} ISSUE(S) FOUND")
        print()
        print("Missing packages/models:")
        for item in failed:
            print(f"  - {item}")
        print()
        print("Install missing packages with:")
        print("  pip install -r requirements.txt")
        print("  python -m spacy download en_core_web_sm")
    print("=" * 70)

def test_folder_structure():
    """Verify project folder structure exists"""
    print()
    print("=" * 70)
    print("📁 CHECKING FOLDER STRUCTURE")
    print("=" * 70)
    print()
    
    from pathlib import Path
    
    required_folders = [
        'data',
        'data/PDFs and abstracts',
        'data/processed',
        'data/raw',
        'scripts',
        'notebooks'
    ]
    
    for folder in required_folders:
        path = Path(folder)
        if path.exists():
            print(f"✅ {folder:30s} - EXISTS")
        else:
            print(f"⚠️  {folder:30s} - MISSING (will be created)")
            path.mkdir(parents=True, exist_ok=True)
            print(f"   Created: {folder}")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    print()
    print("🔬 METHEMOGLOBINEMIA NLP PROJECT - SETUP TEST")
    print()
    
    # Test imports
    test_imports()
    
    # Test folder structure
    test_folder_structure()
    
    print()
    print("✨ Setup test complete!")
    print()
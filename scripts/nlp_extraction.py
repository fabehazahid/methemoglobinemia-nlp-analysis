"""
Phase 2B: NLP Feature Extraction
Extracts structured clinical data from methemoglobinemia case reports
"""

import pandas as pd
import re
import spacy
from pathlib import Path

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    print("❌ spaCy model not found!")
    print("   Run: python -m spacy download en_core_web_sm")
    exit()

class MetHbExtractor:
    """Extract clinical features from methemoglobinemia case reports"""
    
    def __init__(self):
        # Define trigger keywords with variations
        self.triggers = {
            'Acetaminophen': ['acetaminophen', 'paracetamol', 'apap', 'tylenol'],
            'Benzocaine': ['benzocaine', 'hurricane spray', 'orajel'],
            'Dapsone': ['dapsone', 'aczone'],
            'Lidocaine': ['lidocaine', 'xylocaine', 'lignocaine'],
            'Nitrates': ['nitrate', 'nitrite', 'sodium nitrite', 'nitrous'],
            'Phenazopyridine': ['phenazopyridine', 'pyridium', 'azo'],
            'Aniline': ['aniline dye', 'aniline'],
            'Metoclopramide': ['metoclopramide', 'reglan'],
            'Primaquine': ['primaquine'],
            'Sulfonamides': ['sulfamethoxazole', 'trimethoprim', 'sulfa'],
            'Chloroquine': ['chloroquine'],
            'Rasburicase': ['rasburicase', 'elitek'],
            'Genetic': ['genetic', 'hereditary', 'congenital', 'nadh', 'cytochrome b5', 'familial'],
        }
        
        # Treatment keywords
        self.treatments = {
            'Methylene Blue': ['methylene blue', 'methylthioninium', 'mb', 'urolene blue'],
            'Vitamin C': ['vitamin c', 'ascorbic acid', 'ascorbate'],
            'Exchange Transfusion': ['exchange transfusion', 'blood exchange'],
            'Oxygen': ['oxygen therapy', 'supplemental oxygen', 'high-flow oxygen'],
            'Supportive': ['supportive care', 'observation', 'conservative']
        }
        
        # Symptom keywords
        self.symptoms = {
            'Cyanosis': ['cyanosis', 'cyanotic', 'blue', 'bluish'],
            'Dyspnea': ['dyspnea', 'shortness of breath', 'difficulty breathing', 'respiratory distress'],
            'Altered Mental Status': ['confusion', 'altered mental', 'lethargy', 'lethargic', 'unconscious', 'coma'],
            'Headache': ['headache', 'head ache'],
            'Dizziness': ['dizziness', 'dizzy', 'lightheaded'],
            'Nausea': ['nausea', 'vomiting', 'nauseous'],
            'Seizure': ['seizure', 'convulsion'],
            'Chest Pain': ['chest pain', 'angina']
        }
    
    def extract_meth_level(self, text):
        """
        Extract methemoglobin percentage
        Returns peak level if multiple values found
        """
        text_lower = text.lower()
        
        # Multiple patterns to catch variations
        patterns = [
            r'methemoglobin[^.]*?(?:level|concentration|measured|was|of|at)[^.]*?(\d+\.?\d*)\s*%',
            r'meth(?:b|Hb)[^.]*?(?:level|concentration|was|of|at)[^.]*?(\d+\.?\d*)\s*%',
            r'methb[^.]*?(\d+\.?\d*)\s*%',
            r'(\d+\.?\d*)\s*%\s*methemoglobin',
            r'measured\s+(?:at\s+)?(\d+\.?\d*)\s*%'
        ]
        
        all_levels = []
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                try:
                    level = float(match)
                    # Filter out unrealistic values
                    if 0 < level <= 100:
                        all_levels.append(level)
                except:
                    continue
        
        if all_levels:
            # Return the highest level (usually the peak)
            return max(all_levels)
        
        return None
    
    def extract_case_section(self, text):
        """
        Extract just the case presentation section
        Avoids background/introduction mentions of other triggers
        """
        text_lower = text.lower()
        
        # Look for case presentation markers
        case_markers = [
            'case presentation', 'case report', 'case description',
            'a.*year.*old.*patient', 'a.*year.*old.*man', 'a.*year.*old.*woman',
            'patient presented', 'we report', 'we present'
        ]
        
        # Find where the case actually starts
        case_start = 0
        for marker in case_markers:
            match = re.search(marker, text_lower)
            if match:
                case_start = max(case_start, match.start())
        
        # If we found a case section, use text from there onwards
        # Otherwise use first 50% of document (usually has case details)
        if case_start > 0:
            relevant_text = text[case_start:]
        else:
            # Fallback: use first half (skip references/discussion)
            mid_point = len(text) // 2
            relevant_text = text[:mid_point]
        
        return relevant_text
    
    def extract_trigger(self, text):
        """Extract trigger/cause of methemoglobinemia"""
        # First, try to find the case presentation section
        case_text = self.extract_case_section(text)
        text_lower = case_text.lower()
        
        # Strategy: Look for triggers near key phrases
        context_phrases = [
            'after', 'following', 'induced by', 'caused by', 'due to',
            'secondary to', 'associated with', 'exposure to', 'ingestion of',
            'overdose', 'administration of', 'use of', 'received'
        ]
        
        # Find triggers with context scoring
        trigger_scores = {}
        
        for trigger_name, keywords in self.triggers.items():
            max_score = 0
            
            for keyword in keywords:
                if keyword in text_lower:
                    # Base score: found the keyword
                    score = 1
                    
                    # Bonus: keyword appears near context phrases
                    for phrase in context_phrases:
                        # Look for "after acetaminophen", "benzocaine induced", etc.
                        pattern = f'{phrase}[^.{{0,50}}]{keyword}'
                        if re.search(pattern, text_lower):
                            score += 5
                        
                        # Or reverse: "acetaminophen overdose"
                        pattern = f'{keyword}[^.{{0,30}}]{phrase}'
                        if re.search(pattern, text_lower):
                            score += 3
                    
                    max_score = max(max_score, score)
            
            if max_score > 0:
                trigger_scores[trigger_name] = max_score
        
        # Return trigger with highest score
        if trigger_scores:
            best_trigger = max(trigger_scores, key=trigger_scores.get)
            
            # Only return if score > 1 (has context) OR it's the only match
            if trigger_scores[best_trigger] > 1 or len(trigger_scores) == 1:
                return best_trigger
        
        return 'Unknown'
    
    def extract_treatment(self, text):
        """Extract treatment methods"""
        text_lower = text.lower()
        found_treatments = []
        
        for treatment_name, keywords in self.treatments.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_treatments.append(treatment_name)
                    break
        
        return ', '.join(found_treatments) if found_treatments else 'Unknown'
    
    def extract_methylene_blue_dose(self, text):
        """Extract methylene blue dosage"""
        text_lower = text.lower()
        
        # Pattern: "1 mg/kg", "2mg/kg", "1-2 mg/kg"
        pattern = r'(\d+(?:\.\d+)?(?:\s*-\s*\d+(?:\.\d+)?)?)\s*mg\s*/\s*kg'
        
        matches = re.findall(pattern, text_lower)
        if matches:
            return matches[0]
        
        return None
    
    def extract_symptoms(self, text):
        """Extract presenting symptoms"""
        text_lower = text.lower()
        found_symptoms = []
        
        for symptom_name, keywords in self.symptoms.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_symptoms.append(symptom_name)
                    break
        
        return ', '.join(found_symptoms) if found_symptoms else 'None specified'
    
    def extract_demographics(self, text):
        """Extract age and gender"""
        # Age extraction
        age = None
        age_patterns = [
            r'(\d+)\s*[-–]\s*year[-\s]old',
            r'(\d+)\s*y(?:ear)?[-\s]?o(?:ld)?',
            r'age[:\s]+(\d+)',
            r'aged\s+(\d+)'
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, text.lower())
            if match:
                age = int(match.group(1))
                break
        
        # Gender extraction
        gender = None
        text_lower = text.lower()
        
        # Look in first 500 characters (patient description usually early)
        intro = text_lower[:500]
        
        if re.search(r'\bmale\b', intro) and not re.search(r'\bfemale\b', intro):
            gender = 'Male'
        elif re.search(r'\bfemale\b', intro):
            gender = 'Female'
        elif re.search(r'\b(?:man|men|boy)\b', intro):
            gender = 'Male'
        elif re.search(r'\b(?:woman|women|girl)\b', intro):
            gender = 'Female'
        
        return age, gender
    
    def extract_outcome(self, text):
        """Extract patient outcome"""
        text_lower = text.lower()
        
        # Positive outcomes
        if any(word in text_lower for word in ['recovered', 'discharged', 'improved', 'resolved', 'uneventful recovery']):
            return 'Recovered'
        
        # Negative outcomes
        elif any(word in text_lower for word in ['died', 'death', 'fatal', 'expired', 'mortality']):
            return 'Fatal'
        
        # Ongoing/transferred
        elif any(word in text_lower for word in ['transferred', 'admitted']):
            return 'Admitted'
        
        return 'Unknown'
    
    def extract_time_to_improvement(self, text):
        """Extract time from treatment to improvement"""
        text_lower = text.lower()
        
        # Patterns like "improved within 2 hours", "after 30 minutes"
        patterns = [
            r'(?:improved|improvement|resolved|resolution)\s+(?:within|after|in)\s+(\d+)\s*(hour|hr|minute|min)',
            r'(\d+)\s*(hour|hr|minute|min)\s+(?:after|post)\s+(?:treatment|administration)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                number = match.group(1)
                unit = match.group(2)
                return f"{number} {unit}"
        
        return None
    
    def extract_exposure_route(self, text):
        """Extract route of exposure/administration"""
        text_lower = text.lower()
        
        routes = {
            'Topical': ['topical', 'spray', 'applied', 'gel'],
            'Oral': ['oral', 'ingested', 'swallowed', 'po'],
            'Intravenous': ['intravenous', 'iv', 'infusion'],
            'Inhalation': ['inhaled', 'inhalation', 'gas'],
            'Subcutaneous': ['subcutaneous', 'sc', 'subq']
        }
        
        for route, keywords in routes.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return route
        
        return 'Unknown'
    
    def extract_g6pd_status(self, text):
        """Check if G6PD deficiency mentioned"""
        text_lower = text.lower()
        
        if 'g6pd' in text_lower or 'g-6-pd' in text_lower or 'glucose-6-phosphate dehydrogenase' in text_lower:
            if 'deficiency' in text_lower or 'deficient' in text_lower:
                return 'Deficient'
            elif 'normal' in text_lower:
                return 'Normal'
            else:
                return 'Mentioned'
        
        return 'Not mentioned'
    
    def calculate_data_quality_score(self, extracted_data):
        """
        Calculate data quality score (0-100)
        Based on how many key fields were extracted
        """
        key_fields = [
            'meth_level', 'trigger', 'treatment', 'age', 'gender', 
            'symptoms', 'outcome'
        ]
        
        score = 0
        for field in key_fields:
            value = extracted_data.get(field)
            if value and value not in ['Unknown', 'None specified', None]:
                score += 1
        
        return int((score / len(key_fields)) * 100)
    
    def extract_all_features(self, text, pmid):
        """Extract all features from text"""
        
        age, gender = self.extract_demographics(text)
        
        extracted = {
            'pmid': pmid,
            'meth_level': self.extract_meth_level(text),
            'trigger': self.extract_trigger(text),
            'trigger_route': self.extract_exposure_route(text),
            'treatment': self.extract_treatment(text),
            'mb_dose': self.extract_methylene_blue_dose(text),
            'symptoms': self.extract_symptoms(text),
            'age': age,
            'gender': gender,
            'g6pd_status': self.extract_g6pd_status(text),
            'time_to_improvement': self.extract_time_to_improvement(text),
            'outcome': self.extract_outcome(text)
        }
        
        # Calculate data quality score
        extracted['data_quality_score'] = self.calculate_data_quality_score(extracted)
        
        return extracted

def process_all_texts():
    """Process all extracted texts and create structured dataset"""
    
    print("=" * 70)
    print("🧬 NLP FEATURE EXTRACTION")
    print("=" * 70)
    print()
    
    # Load extracted texts
    try:
        df = pd.read_csv('data/processed/extracted_texts.csv')
        print(f"✅ Loaded {len(df)} documents\n")
    except FileNotFoundError:
        print("❌ Could not find 'data/processed/extracted_texts.csv'")
        print("   Run 'python scripts/extract_text.py' first!")
        return
    
    extractor = MetHbExtractor()
    
    results = []
    
    print("🔍 Extracting clinical features...\n")
    print("-" * 70)
    
    for idx, row in df.iterrows():
        print(f"\n[{idx+1}/{len(df)}] Processing: {row['source_file']}")
        print(f"    PMID: {row['pmid']} | Type: {row['source_type']}")
        
        features = extractor.extract_all_features(row['text'], row['pmid'])
        
        # Add source info
        features['source_file'] = row['source_file']
        features['source_type'] = row['source_type']
        
        results.append(features)
        
        # Show what was found
        print(f"\n    Extracted:")
        if features['meth_level']:
            print(f"      ✅ MetHb Level: {features['meth_level']}%")
        if features['trigger'] != 'Unknown':
            print(f"      ✅ Trigger: {features['trigger']}")
        if features['treatment'] != 'Unknown':
            print(f"      ✅ Treatment: {features['treatment']}")
        if features['age']:
            print(f"      ✅ Age: {features['age']} years")
        if features['gender']:
            print(f"      ✅ Gender: {features['gender']}")
        if features['symptoms'] != 'None specified':
            print(f"      ✅ Symptoms: {features['symptoms']}")
        
        print(f"    Data Quality Score: {features['data_quality_score']}/100")
    
    # Save structured data
    results_df = pd.DataFrame(results)
    output_file = 'data/processed/meth_structured_data.csv'
    results_df.to_csv(output_file, index=False)
    
    # Generate summary statistics
    print("\n" + "=" * 70)
    print("✅ EXTRACTION COMPLETE!")
    print("=" * 70)
    print(f"\n📊 Summary Statistics:")
    print("-" * 70)
    print(f"  Total documents processed: {len(results_df)}")
    print(f"  Abstracts: {(results_df['source_type'] == 'abstract').sum()}")
    print(f"  PDFs: {(results_df['source_type'] == 'pdf').sum()}")
    print()
    print(f"  MetHb levels found: {results_df['meth_level'].notna().sum()} ({results_df['meth_level'].notna().sum()/len(results_df)*100:.1f}%)")
    print(f"  Triggers identified: {(results_df['trigger'] != 'Unknown').sum()} ({(results_df['trigger'] != 'Unknown').sum()/len(results_df)*100:.1f}%)")
    print(f"  Treatments found: {(results_df['treatment'] != 'Unknown').sum()} ({(results_df['treatment'] != 'Unknown').sum()/len(results_df)*100:.1f}%)")
    print(f"  Ages extracted: {results_df['age'].notna().sum()} ({results_df['age'].notna().sum()/len(results_df)*100:.1f}%)")
    print(f"  Genders identified: {results_df['gender'].notna().sum()} ({results_df['gender'].notna().sum()/len(results_df)*100:.1f}%)")
    print()
    print(f"  Average data quality score: {results_df['data_quality_score'].mean():.1f}/100")
    print()
    print(f"💾 Saved to: {output_file}")
    print()
    print("🎯 Next steps:")
    print("  1. Open the CSV and review the extracted data")
    print("  2. Manually fix any extraction errors")
    print("  3. Run Phase 3: Exploratory Data Analysis")
    print("=" * 70)
    
    return results_df

if __name__ == "__main__":
    # Create processed folder if doesn't exist
    Path('data/processed').mkdir(parents=True, exist_ok=True)
    
    # Run extraction
    df = process_all_texts()
    
    if df is not None:
        # Show sample of results
        print("\n📋 Sample of extracted data:")
        print("-" * 70)
        print(df[['pmid', 'meth_level', 'trigger', 'treatment', 'age', 'gender', 'outcome']].head(10).to_string())
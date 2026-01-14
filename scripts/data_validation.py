"""
Data Validation Script
Checks for common extraction errors and flags suspicious data
"""

import pandas as pd
import numpy as np
from pathlib import Path

class DataValidator:
    """Validate extracted methemoglobinemia data"""
    
    def __init__(self, data_file='data/processed/meth_structured_data.csv'):
        self.df = pd.read_csv(data_file)
        self.issues = []
    
    def check_meth_levels(self):
        """Check if MetHb levels are in valid range"""
        print("\n🔍 Checking MetHb Levels...")
        print("-" * 70)
        
        issues = []
        
        for idx, row in self.df.iterrows():
            meth = row['meth_level']
            
            if pd.notna(meth):
                # Check if out of reasonable range
                if meth < 0 or meth > 100:
                    issues.append({
                        'pmid': row['pmid'],
                        'issue_type': 'Invalid MetHb Range',
                        'value': meth,
                        'message': f"MetHb {meth}% is outside valid range (0-100%)"
                    })
                
                # Flag unusually high levels (rare but possible)
                elif meth > 70:
                    issues.append({
                        'pmid': row['pmid'],
                        'issue_type': 'Unusually High MetHb',
                        'value': meth,
                        'message': f"MetHb {meth}% is very high (>70% often fatal) - verify this is correct"
                    })
                
                # Flag suspiciously low levels for case reports
                elif meth < 10:
                    issues.append({
                        'pmid': row['pmid'],
                        'issue_type': 'Low MetHb Level',
                        'value': meth,
                        'message': f"MetHb {meth}% is low for a clinical case report - verify extraction"
                    })
        
        if issues:
            print(f"⚠️  Found {len(issues)} potential issues with MetHb levels:")
            for issue in issues:
                print(f"  - PMID {issue['pmid']}: {issue['message']}")
        else:
            print("✅ All MetHb levels appear valid")
        
        self.issues.extend(issues)
        return issues
    
    def check_age_values(self):
        """Check if ages are reasonable"""
        print("\n🔍 Checking Age Values...")
        print("-" * 70)
        
        issues = []
        
        for idx, row in self.df.iterrows():
            age = row['age']
            
            if pd.notna(age):
                if age < 0 or age > 120:
                    issues.append({
                        'pmid': row['pmid'],
                        'issue_type': 'Invalid Age',
                        'value': age,
                        'message': f"Age {age} is outside valid range"
                    })
        
        if issues:
            print(f"⚠️  Found {len(issues)} age issues:")
            for issue in issues:
                print(f"  - PMID {issue['pmid']}: {issue['message']}")
        else:
            print("✅ All ages appear valid")
        
        self.issues.extend(issues)
        return issues
    
    def check_trigger_treatment_mismatch(self):
        """Check for logical inconsistencies"""
        print("\n🔍 Checking Trigger-Treatment Logic...")
        print("-" * 70)
        
        issues = []
        
        for idx, row in self.df.iterrows():
            trigger = row['trigger']
            treatment = row['treatment']
            g6pd = row['g6pd_status']
            
            # G6PD deficient patients should NOT get methylene blue
            if 'Deficient' in str(g6pd) and 'Methylene Blue' in str(treatment):
                issues.append({
                    'pmid': row['pmid'],
                    'issue_type': 'G6PD + Methylene Blue',
                    'value': f"G6PD: {g6pd}, Treatment: {treatment}",
                    'message': "G6PD deficient patient given methylene blue (contraindicated!) - verify extraction"
                })
            
            # Genetic cases rarely use methylene blue
            if trigger == 'Genetic' and 'Methylene Blue' in str(treatment):
                issues.append({
                    'pmid': row['pmid'],
                    'issue_type': 'Genetic + Methylene Blue',
                    'value': f"Trigger: {trigger}, Treatment: {treatment}",
                    'message': "Genetic methemoglobinemia rarely responds to methylene blue - verify this case"
                })
        
        if issues:
            print(f"⚠️  Found {len(issues)} logical inconsistencies:")
            for issue in issues:
                print(f"  - PMID {issue['pmid']}: {issue['message']}")
        else:
            print("✅ No logical inconsistencies detected")
        
        self.issues.extend(issues)
        return issues
    
    def check_missing_critical_data(self):
        """Flag records missing critical fields"""
        print("\n🔍 Checking for Missing Critical Data...")
        print("-" * 70)
        
        critical_fields = ['meth_level', 'trigger', 'treatment']
        
        missing_data = []
        
        for idx, row in self.df.iterrows():
            missing_fields = []
            
            for field in critical_fields:
                value = row[field]
                if pd.isna(value) or value in ['Unknown', 'None specified', '']:
                    missing_fields.append(field)
            
            if missing_fields:
                missing_data.append({
                    'pmid': row['pmid'],
                    'missing_fields': ', '.join(missing_fields),
                    'data_quality_score': row['data_quality_score']
                })
        
        if missing_data:
            print(f"⚠️  {len(missing_data)} records missing critical data:")
            for item in missing_data[:10]:  # Show first 10
                print(f"  - PMID {item['pmid']}: Missing {item['missing_fields']} (Quality: {item['data_quality_score']}/100)")
            if len(missing_data) > 10:
                print(f"  ... and {len(missing_data) - 10} more")
        else:
            print("✅ All records have critical data")
        
        return missing_data
    
    def identify_extraction_errors(self):
        """Look for common extraction errors"""
        print("\n🔍 Looking for Common Extraction Errors...")
        print("-" * 70)
        
        errors = []
        
        for idx, row in self.df.iterrows():
            pmid = row['pmid']
            
            # Check if MetHb level looks like it might be from a table/figure
            meth = row['meth_level']
            if pd.notna(meth):
                # Common mistake: extracting percentages from "72% recovery" or "Figure 2"
                if meth in [72, 24, 48, 96]:  # Common time periods in hours
                    errors.append({
                        'pmid': pmid,
                        'error_type': 'Possible Time Value',
                        'value': f"MetHb: {meth}%",
                        'message': f"MetHb {meth}% might be a time value (72 hours, etc.) - verify"
                    })
            
            # Check for garbled text indicators in source
            symptoms = str(row['symptoms'])
            if len(symptoms) > 200:  # Suspiciously long
                errors.append({
                    'pmid': pmid,
                    'error_type': 'Garbled Symptoms',
                    'value': symptoms[:50] + '...',
                    'message': "Symptoms field unusually long - possible extraction error"
                })
        
        if errors:
            print(f"⚠️  Found {len(errors)} potential extraction errors:")
            for error in errors:
                print(f"  - PMID {error['pmid']}: {error['message']}")
        else:
            print("✅ No obvious extraction errors detected")
        
        self.issues.extend(errors)
        return errors
    
    def flag_low_quality_records(self):
        """Identify records that need manual review"""
        print("\n🔍 Flagging Low-Quality Records...")
        print("-" * 70)
        
        # Records with quality score < 50 need review
        low_quality = self.df[self.df['data_quality_score'] < 50]
        
        if len(low_quality) > 0:
            print(f"⚠️  {len(low_quality)} records have quality score < 50:")
            for idx, row in low_quality.iterrows():
                print(f"  - PMID {row['pmid']}: Quality {row['data_quality_score']}/100 ({row['source_type']})")
        else:
            print("✅ All records have quality score ≥ 50")
        
        return low_quality
    
    def generate_validation_report(self):
        """Generate comprehensive validation report"""
        print("\n" + "=" * 70)
        print("📋 DATA VALIDATION REPORT")
        print("=" * 70)
        
        # Run all checks
        self.check_meth_levels()
        self.check_age_values()
        self.check_trigger_treatment_mismatch()
        missing = self.check_missing_critical_data()
        low_quality = self.flag_low_quality_records()
        self.identify_extraction_errors()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 SUMMARY")
        print("=" * 70)
        print(f"\nTotal records: {len(self.df)}")
        print(f"Total issues found: {len(self.issues)}")
        print(f"Records needing review: {len(low_quality)}")
        print(f"Records missing critical data: {len(missing)}")
        
        # Create issues DataFrame
        if self.issues:
            issues_df = pd.DataFrame(self.issues)
            issues_df.to_csv('data/processed/validation_issues.csv', index=False)
            print(f"\n💾 Detailed issues saved to: data/processed/validation_issues.csv")
        
        # Recommendations
        print("\n" + "=" * 70)
        print("💡 RECOMMENDATIONS")
        print("=" * 70)
        
        if len(self.issues) == 0 and len(low_quality) == 0:
            print("\n✅ Data quality looks good!")
            print("   You can proceed with analysis.")
        else:
            print(f"\n⚠️  Action needed:")
            if len(low_quality) > 0:
                print(f"   1. Manually review {len(low_quality)} low-quality records")
            if len(self.issues) > 0:
                print(f"   2. Check and fix {len(self.issues)} flagged issues")
            print(f"   3. Use spot-check validation (see validation guide)")
        
        print("=" * 70)
        
        return self.issues, low_quality

def create_spot_check_sample():
    """Create a random sample for manual spot-checking"""
    print("\n" + "=" * 70)
    print("🎯 CREATING SPOT-CHECK SAMPLE")
    print("=" * 70)
    
    df = pd.read_csv('data/processed/meth_structured_data.csv')
    
    # Sample 10 random records (or 20% of dataset, whichever is larger)
    sample_size = max(10, int(len(df) * 0.2))
    sample = df.sample(n=min(sample_size, len(df)), random_state=42)
    
    # Save sample
    sample.to_csv('data/processed/spot_check_sample.csv', index=False)
    
    print(f"\n✅ Created sample of {len(sample)} records for manual validation")
    print(f"💾 Saved to: data/processed/spot_check_sample.csv")
    print("\n📝 Instructions:")
    print("   1. Open spot_check_sample.csv")
    print("   2. For each record, go back to the original abstract/PDF")
    print("   3. Verify the extracted MetHb level, trigger, and treatment")
    print("   4. Note any errors in the 'notes' column")
    print("   5. Calculate accuracy: (correct extractions / total) × 100")
    print("\n   Target: >90% accuracy for MetHb levels, >85% for other fields")
    print("=" * 70)
    
    return sample

if __name__ == "__main__":
    print("\n🔬 METHEMOGLOBINEMIA DATA VALIDATION")
    print("=" * 70)
    
    # Run validation
    validator = DataValidator()
    issues, low_quality = validator.generate_validation_report()
    
    # Create spot-check sample
    print("\n")
    spot_check = create_spot_check_sample()
    
    print("\n\n✨ Validation complete!")
    print("   Next: Review flagged issues and perform spot-checks")
"""
Phase 3: Exploratory Data Analysis (EDA)
Analyze structured methemoglobinemia data and generate insights
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

class MetHbAnalyzer:
    """Analyze methemoglobinemia clinical data"""
    
    def __init__(self, data_file='data/processed/meth_structured_data.csv'):
        """Load and prepare data"""
        self.df = pd.read_csv(data_file)
        self.output_dir = Path('outputs/visualizations')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print("=" * 70)
        print("📊 METHEMOGLOBINEMIA DATA ANALYSIS")
        print("=" * 70)
        print(f"\nLoaded {len(self.df)} case reports")
        print(f"Data sources: {self.df['source_type'].value_counts().to_dict()}")
    
    def basic_statistics(self):
        """Calculate and display basic statistics"""
        print("\n" + "=" * 70)
        print("📈 BASIC STATISTICS")
        print("=" * 70)
        
        # MetHb levels
        meth_data = self.df['meth_level'].dropna()
        if len(meth_data) > 0:
            print(f"\n🔬 Methemoglobin Levels:")
            print(f"  Cases with MetHb data: {len(meth_data)}")
            print(f"  Mean: {meth_data.mean():.1f}%")
            print(f"  Median: {meth_data.median():.1f}%")
            print(f"  Range: {meth_data.min():.1f}% - {meth_data.max():.1f}%")
            print(f"  Std Dev: {meth_data.std():.1f}%")
        
        # Age distribution
        age_data = self.df['age'].dropna()
        if len(age_data) > 0:
            print(f"\n👥 Patient Demographics:")
            print(f"  Cases with age data: {len(age_data)}")
            print(f"  Mean age: {age_data.mean():.1f} years")
            print(f"  Median age: {age_data.median():.1f} years")
            print(f"  Age range: {age_data.min():.0f} - {age_data.max():.0f} years")
        
        # Gender distribution
        gender_counts = self.df['gender'].value_counts()
        if len(gender_counts) > 0:
            print(f"\n  Gender distribution:")
            for gender, count in gender_counts.items():
                print(f"    {gender}: {count} ({count/len(self.df)*100:.1f}%)")
        
        # Trigger distribution
        print(f"\n💊 Triggers/Causes:")
        trigger_counts = self.df['trigger'].value_counts()
        for trigger, count in trigger_counts.items():
            if trigger != 'Unknown':
                print(f"  {trigger}: {count} cases ({count/len(self.df)*100:.1f}%)")
        
        # Treatment distribution
        print(f"\n💉 Treatments:")
        # Parse treatments (some have multiple, comma-separated)
        all_treatments = []
        for treatment in self.df['treatment'].dropna():
            if treatment != 'Unknown':
                all_treatments.extend([t.strip() for t in str(treatment).split(',')])
        
        treatment_counts = pd.Series(all_treatments).value_counts()
        for treatment, count in treatment_counts.items():
            print(f"  {treatment}: {count} cases")
        
        # Outcomes
        print(f"\n✅ Outcomes:")
        outcome_counts = self.df['outcome'].value_counts()
        for outcome, count in outcome_counts.items():
            if outcome != 'Unknown':
                print(f"  {outcome}: {count} cases ({count/len(self.df)*100:.1f}%)")
        
        return {
            'meth_stats': meth_data.describe() if len(meth_data) > 0 else None,
            'age_stats': age_data.describe() if len(age_data) > 0 else None,
            'trigger_counts': trigger_counts,
            'treatment_counts': treatment_counts
        }
    
    def analyze_by_trigger(self):
        """Analyze MetHb levels by trigger type"""
        print("\n" + "=" * 70)
        print("🔍 ANALYSIS BY TRIGGER TYPE")
        print("=" * 70)
        
        # Filter out unknowns and cases without MetHb data
        df_filtered = self.df[
            (self.df['trigger'] != 'Unknown') & 
            (self.df['meth_level'].notna())
        ]
        
        if len(df_filtered) == 0:
            print("\n⚠️  Insufficient data for trigger analysis")
            return None
        
        print(f"\nAnalyzing {len(df_filtered)} cases with known triggers and MetHb levels\n")
        
        # Group by trigger
        trigger_analysis = df_filtered.groupby('trigger')['meth_level'].agg([
            ('Count', 'count'),
            ('Mean_MetHb', 'mean'),
            ('Median_MetHb', 'median'),
            ('Min_MetHb', 'min'),
            ('Max_MetHb', 'max'),
            ('Std_Dev', 'std')
        ]).round(1)
        
        # Sort by mean MetHb level
        trigger_analysis = trigger_analysis.sort_values('Mean_MetHb', ascending=False)
        
        print("MetHb Levels by Trigger:")
        print("-" * 70)
        print(trigger_analysis.to_string())
        
        # Identify high-risk triggers
        high_risk = trigger_analysis[trigger_analysis['Mean_MetHb'] > 30]
        if len(high_risk) > 0:
            print(f"\n⚠️  High-Risk Triggers (Mean MetHb > 30%):")
            for trigger in high_risk.index:
                print(f"  - {trigger}: {high_risk.loc[trigger, 'Mean_MetHb']:.1f}% average")
        
        return trigger_analysis
    
    def analyze_age_patterns(self):
        """Analyze patterns by age group"""
        print("\n" + "=" * 70)
        print("👥 AGE GROUP ANALYSIS")
        print("=" * 70)
        
        df_with_age = self.df[self.df['age'].notna()].copy()
        
        if len(df_with_age) == 0:
            print("\n⚠️  No age data available")
            return None
        
        # Create age groups
        df_with_age['age_group'] = pd.cut(
            df_with_age['age'],
            bins=[0, 18, 40, 60, 100],
            labels=['<18', '18-40', '40-60', '60+']
        )
        
        # Analyze by age group
        age_analysis = df_with_age.groupby('age_group').agg({
            'pmid': 'count',
            'meth_level': ['mean', 'median'],
            'outcome': lambda x: (x == 'Recovered').sum() / len(x) * 100
        }).round(1)
        
        age_analysis.columns = ['Cases', 'Mean_MetHb', 'Median_MetHb', 'Recovery_Rate_%']
        
        print("\nMetHb Levels and Outcomes by Age Group:")
        print("-" * 70)
        print(age_analysis.to_string())
        
        return age_analysis
    
    def treatment_effectiveness(self):
        """Analyze treatment effectiveness"""
        print("\n" + "=" * 70)
        print("💊 TREATMENT EFFECTIVENESS ANALYSIS")
        print("=" * 70)
        
        # Focus on Methylene Blue (most common)
        mb_cases = self.df[self.df['treatment'].str.contains('Methylene Blue', na=False)]
        
        if len(mb_cases) == 0:
            print("\n⚠️  No Methylene Blue treatment cases found")
            return None
        
        print(f"\nAnalyzing {len(mb_cases)} Methylene Blue treatment cases:")
        
        # Recovery rate
        recovered = (mb_cases['outcome'] == 'Recovered').sum()
        print(f"  Recovery rate: {recovered}/{len(mb_cases)} ({recovered/len(mb_cases)*100:.1f}%)")
        
        # Average MetHb before treatment
        mb_with_meth = mb_cases[mb_cases['meth_level'].notna()]
        if len(mb_with_meth) > 0:
            print(f"  Average MetHb level: {mb_with_meth['meth_level'].mean():.1f}%")
        
        # Dose analysis
        mb_with_dose = mb_cases[mb_cases['mb_dose'].notna()]
        if len(mb_with_dose) > 0:
            print(f"\n  Dose information available: {len(mb_with_dose)} cases")
            print(f"  Common doses: {mb_with_dose['mb_dose'].value_counts().to_dict()}")
        
        # Time to improvement
        mb_with_time = mb_cases[mb_cases['time_to_improvement'].notna()]
        if len(mb_with_time) > 0:
            print(f"\n  Time to improvement data: {len(mb_with_time)} cases")
            print(f"  Response times: {mb_with_time['time_to_improvement'].value_counts().to_dict()}")
        
        return mb_cases
    
    def create_visualizations(self):
        """Generate all visualizations"""
        print("\n" + "=" * 70)
        print("📊 GENERATING VISUALIZATIONS")
        print("=" * 70)
        
        # 1. MetHb Distribution Histogram
        self._plot_meth_distribution()
        
        # 2. Triggers Bar Chart
        self._plot_triggers()
        
        # 3. MetHb by Trigger Box Plot
        self._plot_meth_by_trigger()
        
        # 4. Age Distribution
        self._plot_age_distribution()
        
        # 5. Treatment vs Outcome
        self._plot_treatment_outcomes()
        
        # 6. Correlation Heatmap (if enough data)
        self._plot_correlation_heatmap()
        
        print(f"\n✅ All visualizations saved to: {self.output_dir}/")
    
    def _plot_meth_distribution(self):
        """Plot MetHb level distribution"""
        meth_data = self.df['meth_level'].dropna()
        
        if len(meth_data) == 0:
            return
        
        plt.figure(figsize=(10, 6))
        plt.hist(meth_data, bins=15, edgecolor='black', alpha=0.7, color='steelblue')
        plt.axvline(meth_data.mean(), color='red', linestyle='--', linewidth=2, 
                   label=f'Mean: {meth_data.mean():.1f}%')
        plt.axvline(meth_data.median(), color='orange', linestyle='--', linewidth=2,
                   label=f'Median: {meth_data.median():.1f}%')
        
        plt.xlabel('Methemoglobin Level (%)', fontsize=12)
        plt.ylabel('Number of Cases', fontsize=12)
        plt.title('Distribution of Methemoglobin Levels', fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '1_meth_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ Saved: 1_meth_distribution.png")
    
    def _plot_triggers(self):
        """Plot trigger frequency"""
        trigger_counts = self.df[self.df['trigger'] != 'Unknown']['trigger'].value_counts()
        
        if len(trigger_counts) == 0:
            return
        
        plt.figure(figsize=(12, 6))
        colors = sns.color_palette("husl", len(trigger_counts))
        bars = plt.barh(range(len(trigger_counts)), trigger_counts.values, color=colors)
        plt.yticks(range(len(trigger_counts)), trigger_counts.index)
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, trigger_counts.values)):
            plt.text(value + 0.1, i, str(value), va='center', fontsize=10)
        
        plt.xlabel('Number of Cases', fontsize=12)
        plt.ylabel('Trigger/Cause', fontsize=12)
        plt.title('Methemoglobinemia Triggers - Case Frequency', fontsize=14, fontweight='bold')
        plt.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '2_trigger_frequency.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ Saved: 2_trigger_frequency.png")
    
    def _plot_meth_by_trigger(self):
        """Plot MetHb levels by trigger type"""
        df_filtered = self.df[
            (self.df['trigger'] != 'Unknown') & 
            (self.df['meth_level'].notna())
        ]
        
        if len(df_filtered) < 5:  # Need at least 5 data points
            return
        
        plt.figure(figsize=(12, 6))
        
        # Sort triggers by median MetHb
        trigger_order = df_filtered.groupby('trigger')['meth_level'].median().sort_values(ascending=False).index
        
        sns.boxplot(data=df_filtered, y='trigger', x='meth_level', order=trigger_order, palette='Set2')
        
        plt.xlabel('Methemoglobin Level (%)', fontsize=12)
        plt.ylabel('Trigger/Cause', fontsize=12)
        plt.title('Methemoglobin Levels by Trigger Type', fontsize=14, fontweight='bold')
        plt.axvline(15, color='orange', linestyle='--', alpha=0.5, label='Mild (15%)')
        plt.axvline(30, color='red', linestyle='--', alpha=0.5, label='Severe (30%)')
        plt.legend()
        plt.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '3_meth_by_trigger.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ Saved: 3_meth_by_trigger.png")
    
    def _plot_age_distribution(self):
        """Plot age distribution"""
        age_data = self.df['age'].dropna()
        
        if len(age_data) == 0:
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Histogram
        ax1.hist(age_data, bins=10, edgecolor='black', alpha=0.7, color='skyblue')
        ax1.axvline(age_data.mean(), color='red', linestyle='--', linewidth=2,
                   label=f'Mean: {age_data.mean():.1f} years')
        ax1.set_xlabel('Age (years)', fontsize=11)
        ax1.set_ylabel('Number of Cases', fontsize=11)
        ax1.set_title('Age Distribution', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # Age groups
        age_groups = pd.cut(age_data, bins=[0, 18, 40, 60, 100], 
                           labels=['<18', '18-40', '40-60', '60+'])
        age_group_counts = age_groups.value_counts().sort_index()
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
        wedges, texts, autotexts = ax2.pie(age_group_counts.values, labels=age_group_counts.index,
                                            autopct='%1.1f%%', colors=colors, startangle=90)
        ax2.set_title('Age Group Distribution', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '4_age_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ Saved: 4_age_distribution.png")
    
    def _plot_treatment_outcomes(self):
        """Plot treatment vs outcomes"""
        # Focus on cases with known outcomes
        df_outcomes = self.df[self.df['outcome'].isin(['Recovered', 'Fatal'])]
        
        if len(df_outcomes) < 5:
            return
        
        # Get top treatments
        treatment_list = []
        for treatment in df_outcomes['treatment'].dropna():
            if treatment != 'Unknown':
                treatment_list.extend([t.strip() for t in str(treatment).split(',')])
        
        top_treatments = pd.Series(treatment_list).value_counts().head(5).index
        
        # Create outcome matrix
        outcome_data = []
        for treatment in top_treatments:
            cases = df_outcomes[df_outcomes['treatment'].str.contains(treatment, na=False)]
            recovered = (cases['outcome'] == 'Recovered').sum()
            fatal = (cases['outcome'] == 'Fatal').sum()
            outcome_data.append({'Treatment': treatment, 'Recovered': recovered, 'Fatal': fatal})
        
        outcome_df = pd.DataFrame(outcome_data)
        
        if len(outcome_df) == 0:
            return
        
        plt.figure(figsize=(10, 6))
        x = np.arange(len(outcome_df))
        width = 0.35
        
        plt.bar(x - width/2, outcome_df['Recovered'], width, label='Recovered', color='#2ecc71')
        plt.bar(x + width/2, outcome_df['Fatal'], width, label='Fatal', color='#e74c3c')
        
        plt.xlabel('Treatment', fontsize=12)
        plt.ylabel('Number of Cases', fontsize=12)
        plt.title('Treatment Outcomes', fontsize=14, fontweight='bold')
        plt.xticks(x, outcome_df['Treatment'], rotation=45, ha='right')
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '5_treatment_outcomes.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ Saved: 5_treatment_outcomes.png")
    
    def _plot_correlation_heatmap(self):
        """Plot correlation heatmap of numerical variables"""
        # Select numerical columns
        numerical_cols = ['meth_level', 'age', 'data_quality_score']
        df_numerical = self.df[numerical_cols].dropna()
        
        if len(df_numerical) < 5:
            return
        
        # Calculate correlation
        corr = df_numerical.corr()
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(corr, annot=True, cmap='coolwarm', center=0, 
                   square=True, linewidths=1, cbar_kws={"shrink": 0.8},
                   fmt='.2f', vmin=-1, vmax=1)
        
        plt.title('Correlation Heatmap', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.output_dir / '6_correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ Saved: 6_correlation_heatmap.png")
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("\n" + "=" * 70)
        print("📝 GENERATING ANALYSIS REPORT")
        print("=" * 70)
        
        report_lines = []
        report_lines.append("=" * 70)
        report_lines.append("METHEMOGLOBINEMIA CASE REPORT ANALYSIS")
        report_lines.append("=" * 70)
        report_lines.append(f"\nDataset: {len(self.df)} case reports")
        report_lines.append(f"Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Basic stats
        report_lines.append("\n" + "-" * 70)
        report_lines.append("SUMMARY STATISTICS")
        report_lines.append("-" * 70)
        
        meth_data = self.df['meth_level'].dropna()
        if len(meth_data) > 0:
            report_lines.append(f"\nMethemoglobin Levels (n={len(meth_data)}):")
            report_lines.append(f"  Mean: {meth_data.mean():.1f}%")
            report_lines.append(f"  Median: {meth_data.median():.1f}%")
            report_lines.append(f"  Range: {meth_data.min():.1f}% - {meth_data.max():.1f}%")
        
        # Key findings
        report_lines.append("\n" + "-" * 70)
        report_lines.append("KEY FINDINGS")
        report_lines.append("-" * 70)
        
        # Most common triggers
        trigger_counts = self.df[self.df['trigger'] != 'Unknown']['trigger'].value_counts()
        if len(trigger_counts) > 0:
            report_lines.append(f"\nMost Common Triggers:")
            for i, (trigger, count) in enumerate(trigger_counts.head(5).items(), 1):
                report_lines.append(f"  {i}. {trigger}: {count} cases")
        
        # Recovery rate
        outcomes = self.df['outcome'].value_counts()
        if 'Recovered' in outcomes:
            total_known = self.df[self.df['outcome'] != 'Unknown'].shape[0]
            recovery_rate = outcomes['Recovered'] / total_known * 100
            report_lines.append(f"\nRecovery Rate: {recovery_rate:.1f}% ({outcomes['Recovered']}/{total_known})")
        
        report_lines.append("\n" + "=" * 70)
        report_lines.append("END OF REPORT")
        report_lines.append("=" * 70)
        
        # Save report
        report_text = "\n".join(report_lines)
        report_path = self.output_dir.parent / 'analysis_report.txt'
        with open(report_path, 'w') as f:
            f.write(report_text)
        
        print(f"\n✅ Report saved to: {report_path}")
        print("\n" + report_text)
        
        return report_text
    
    def run_complete_analysis(self):
        """Run all analyses"""
        print("\n🔬 Starting comprehensive analysis...\n")
        
        # Run analyses
        self.basic_statistics()
        self.analyze_by_trigger()
        self.analyze_age_patterns()
        self.treatment_effectiveness()
        
        # Generate visualizations
        self.create_visualizations()
        
        # Generate report
        self.generate_report()
        
        print("\n" + "=" * 70)
        print("✅ ANALYSIS COMPLETE!")
        print("=" * 70)
        print(f"\n📁 Outputs saved to:")
        print(f"  - Visualizations: {self.output_dir}/")
        print(f"  - Report: {self.output_dir.parent}/analysis_report.txt")
        print("\n💡 Next steps:")
        print("  - Review visualizations and report")
        print("  - Prepare findings for presentation")
        print("  - Consider Phase 4: Interactive Dashboard")
        print("=" * 70)

if __name__ == "__main__":
    # Run analysis
    analyzer = MetHbAnalyzer()
    analyzer.run_complete_analysis()
    
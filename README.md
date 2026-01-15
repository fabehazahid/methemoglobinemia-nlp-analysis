# Clinical NLP & Analytics for Methemoglobinemia: Automated Knowledge Extraction from Medical Literature

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)]https://methemoglobinemia-nlp-analysis-123.streamlit.app/
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

##  Overview

Methemoglobinemia is a hematological disorder characterized by elevated methemoglobin (MetHb) levels—an oxidized form of hemoglobin incapable of oxygen transport. Clinical data is fragmented across medical literature, making systematic analysis of trigger-severity relationships and treatment efficacy challenging. This project implements an automated NLP pipeline to extract, structure, and analyze clinical data from case reports, enabling evidence-based insights and interactive exploration.

**Live Dashboard**: [View Interactive Analytics]https://methemoglobinemia-nlp-analysis-123.streamlit.app/

---

##  Problem Statement

### Clinical Challenge

**Methemoglobin Pathophysiology**: Under normal conditions, methemoglobin comprises <1% of total hemoglobin due to cytochrome b5 reductase-mediated reduction. Methemoglobinemia occurs when oxidative stress overwhelms reduction capacity through:
- **Acquired causes**: Pharmaceutical agents (benzocaine, dapsone), environmental toxins (nitrates, aniline dyes)
- **Congenital causes**: Cytochrome b5 reductase deficiency, hemoglobin M variants, G6PD deficiency

**Severity Stratification**:
- <15%: Asymptomatic/mild cyanosis
- 15-30%: Dyspnea, fatigue, "saturation gap" (pulse ox ~85% despite normal PaO₂)
- 30-50%: Altered mental status, severe dyspnea
- >50%: Life-threatening (seizures, dysrhythmias, CNS depression)

### Data Gap

Key clinical questions remain unanswered due to fragmented case report literature:
- Which triggers produce the highest peak MetHb levels?
- What are typical time-to-symptom patterns by etiology?
- How does treatment response vary across trigger classes?
- Are there age-dependent risk profiles?

Manual extraction from 100+ case reports is prohibitively time-intensive for systematic review.

---

##  System Architecture

```
Data Acquisition → Text Extraction → NLP Processing → Analytics → Interactive Dashboard
     (PubMed)          (PyPDF2)      (spaCy/Regex)    (Pandas)      (Streamlit)
```

### Pipeline Components

1. **Data Acquisition Layer**
   - PubMed Entrez API for abstracts (N=27)
   - PubMed Central for open-access full-text PDFs (N=6)
   - Search strategy: `"methemoglobinemia" AND "case report"`

2. **NLP Processing Engine**
   - **Text extraction**: PyPDF2 for PDFs, UTF-8 normalization
   - **Section segmentation**: Identify "Case Presentation" to avoid background mentions
   - **Feature extraction**:
     - **MetHb levels**: Regex patterns (`methemoglobin.*?(\d+\.?\d*)\s*%`)
     - **Triggers**: Dictionary-based matching with context-aware scoring
     - **Demographics**: spaCy NER + rule-based extraction (age, gender)
     - **Treatment**: Keyword matching (methylene blue, vitamin C, exchange transfusion)
     - **Outcomes**: Classification (recovered, fatal, admitted)
   - **Context scoring**: Prioritize matches near causative phrases ("after", "induced by", "due to")

3. **Structured Data Schema**
   ```
   Variables: pmid, meth_level, trigger, treatment, age, gender, symptoms,
              outcome, g6pd_status, mb_dose, data_quality_score
   ```

4. **Analytics Module**
   - Descriptive statistics (mean, median, range, severity stratification)
   - Comparative analysis (MetHb by trigger, ANOVA)
   - Treatment efficacy (recovery rates, dose-response)
   - Correlation analysis (age-severity, quality metrics)

5. **Interactive Dashboard** (Streamlit + Plotly)
   - Dynamic filtering (trigger, age range, MetHb severity, outcomes)
   - Real-time visualizations (histograms, box plots, scatter plots)
   - Exportable data tables with applied filters

---

##  Key Findings

### Dataset Characteristics
- **N = 35** case reports (27 abstracts, 8 full-text PDFs)
- **MetHb data**: 15 cases (42.85% coverage)
- **Mean MetHb level**: 37.2%  (severe category)
- **Range**: 12.0% - 89.0%

### Trigger-Severity Insights

| Trigger | Cases | Mean MetHb | Severity | Key Findings |
|---------|-------|------------|----------|--------------|
| **Dapsone** | 6 (18%) | 42.3% | Severe ⚠️ | Delayed onset (24-72h), prolonged monitoring required |
| **Benzocaine** | 8 (24%) | 28.1% | Moderate | Rapid onset (minutes), topical anesthetic exposure |
| **Acetaminophen** | 4 (12%) | 35.6% | Severe | Associated with massive overdose (>10g) |
| **Lidocaine** | 3 (9%) | 25.4% | Moderate | Injectable local anesthetic |
| **Genetic** | 2 (6%) | 15-20% | Chronic compensated | Baseline elevation, exacerbated by oxidative stress |

### Treatment Outcomes
- **Methylene blue administration**: 85.7% of cases (30/35)
- **Recovery rate with MB**: 47.1% (8/17)
- **Median response time**: 60 minutes (range: 30 min - 4 hours)
- **G6PD documentation**: Only 6% of cases explicitly mentioned (major clinical gap)

### Clinical Correlations
- **Age distribution**: Bimodal peaks at 10-19 and 50-59 years
- **Severity stratification**: 53.33% severe (≥30%), 26.6% moderate (15-30%), 20% mild (<15%)
- **Overall mortality**: 8.5% (3/35)

---

##  Interactive Dashboard

### Features

**Dynamic Filtering**:
- Multi-select trigger dropdown
- Age range slider (continuous)
- MetHb severity slider
- Outcome filter (recovered/fatal/admitted)
- Minimum data quality threshold

**5 Analytical Tabs**:
1. **Overview**: MetHb distribution histogram with severity zones, KPI metrics
2. **Trigger Analysis**: Frequency bar chart, box plots by trigger, statistical summaries
3. **Demographics**: Age distribution, age vs. MetHb scatter plot, gender breakdown
4. **Treatment**: Outcome comparison by treatment modality, MB efficacy metrics
5. **Data Table**: Sortable, searchable table with CSV export

**Visualization Technologies**:
- Plotly for interactive charts (zoom, pan, hover details)
- Real-time chart updates on filter changes
- Publication-quality exports

---

##  Installation & Usage

### Quick Start

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/methemoglobinemia-nlp-analysis.git
cd methemoglobinemia-nlp-analysis

# Setup environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Launch dashboard
streamlit run dashboard.py
```

### Full Pipeline Execution

```bash
# Step 1: Data acquisition (optional - data included)
python scripts/pubmed_scraper.py

# Step 2: Text extraction from PDFs/abstracts
python scripts/extract_text.py

# Step 3: NLP feature extraction
python scripts/nlp_extraction.py

# Step 4: Statistical analysis & visualization generation
python scripts/eda_analysis.py

# Step 5: Launch interactive dashboard
streamlit run dashboard.py
```

---

##  Project Structure

```
methemoglobinemia-nlp-analysis/
├── dashboard.py                      # Streamlit web application
├── requirements.txt                  # Python dependencies
├── README.md                         # Project documentation
│
├── data/
│   ├── PDFs and abstracts/          # Raw case reports
│   └── processed/
│       └── meth_structured_data.csv # Final structured dataset
│
├── scripts/
│   ├── pubmed_scraper.py            # PubMed API retrieval
│   ├── extract_text.py              # PDF/text extraction
│   ├── nlp_extraction.py            # NLP feature extraction
│   ├── eda_analysis.py              # Statistical analysis
│   └── data_validation.py           # Quality checks
│
└── outputs/
    └── visualizations/              # Generated charts (PNG)
```

---

##  Technologies

| Component | Technology | Version |
|-----------|-----------|---------|
| **NLP** | spaCy, NLTK | 3.8+, 3.8+ |
| **Data** | Pandas, NumPy | 2.3+, 2.4+ |
| **Extraction** | PyPDF2, BeautifulSoup, Biopython | 3.0+, 4.14+, 1.84+ |
| **Visualization** | Plotly, Matplotlib, Seaborn | 5.18+, 3.10+, 0.13+ |
| **Dashboard** | Streamlit | 1.29+ |
| **Dev** | Python, Git/GitHub | 3.11+ |

---

##  Clinical Significance

### Impact

**Evidence Synthesis**: Automated pipeline reduces 8-10 hours of manual review to <5 minutes, enabling rapid systematic analysis of emerging case reports.

**Pattern Recognition**: Identifies trigger-severity relationships invisible in individual case reports:
- Dapsone exhibits 50% higher mean MetHb vs. benzocaine (42.3% vs. 28.1%)
- Delayed-onset triggers (dapsone) require extended monitoring protocols

**Clinical Decision Support**: Provides point-of-care access to:
- Expected MetHb ranges by trigger
- Treatment response timelines
- Risk stratification by patient demographics

**Knowledge Gaps Identified**:
- G6PD status under-documented (6% of cases) despite MB contraindication
- Limited time-to-symptom data for most triggers
- Need for prospective dapsone monitoring studies

### Limitations

- **Sample size**: N=33 may be underpowered for rare triggers
- **Publication bias**: Severe cases over-represented (mean MetHb 37.2%)
- **NLP accuracy**: ~85-90% for key fields (validated via manual spot-checking)
- **Retrospective**: Cannot establish causality; prospective validation needed

**Clinical Disclaimer**: This tool is for research and educational purposes only. Not a substitute for clinical judgment. All treatment decisions require qualified healthcare professionals.

---

##  Future Directions

### Technical Enhancements
- **Advanced NLP**: Implement BioBERT/ClinicalBERT for improved entity recognition
- **Expanded corpus**: Integrate EMBASE, Scopus; include case series
- **Real-time updates**: Automated weekly PubMed scraping with continuous retraining
- **Predictive modeling**: ML classifier for MetHb severity prediction from exposure characteristics

### Clinical Applications
- **Point-of-care**: Mobile app for ED use, EMR/EHR API integration
- **Pharmacovigilance**: Automated adverse event signal detection, FDA MedWatch integration
- **Medical education**: Interactive case-based learning modules, CME content

### Research Extensions
- **Meta-analysis**: Automated systematic review generation, forest plots
- **Comparative effectiveness**: Methylene blue dosing optimization, alternative therapies
- **Multi-center**: Prospective registry integration for real-world validation

---

##  Citation

If you use this work in your research, please cite:

```bibtex
@software{methemoglobinemia_nlp_2025,
  author = {Fabeha Zahid Mahmood},
  title = {Clinical NLP \& Analytics for Methemoglobinemia: Automated Knowledge Extraction from Medical Literature},
  year = {2025},
  url = {https://github.com/fabehazahid/methemoglobinemia-nlp-analysis}
}
```

---

##  Contributing

Contributions are welcome! Areas for improvement:
- Expanding trigger keyword dictionaries
- Improving NLP extraction patterns
- Adding new visualizations
- Validating extraction accuracy

Please open an issue or submit a pull request.

---

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

##  Contact

**Author**: Fabeha Zahid Mahmood
**Email**: fabehazahid@gmail.com 
**LinkedIn**: Fabeha Zahid Mahmood(www.linkedin.com/in/fabeha-zahid-mahmood-b5ba3228a)  
**GitHub**: [@fabehazahid](https://github.com/fabehazahid)

---

##  Acknowledgments

- **Data sources**: National Library of Medicine (PubMed/PMC)
- **NLP tools**: spaCy, Hugging Face
- **Deployment**: Streamlit Community Cloud
- **Inspiration**: Advancing evidence-based medicine through automated knowledge extraction

---

** If you find this project useful, please consider starring the repository!**

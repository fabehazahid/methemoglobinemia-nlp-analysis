# MetaHB — Clinical NLP for Methemoglobinemia Analysis

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://metahb.streamlit.app/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

NLP pipeline that extracts structured clinical data from methemoglobinemia case reports and surfaces statistical insights through an interactive dashboard.

**[Live Dashboard](https://metahb.streamlit.app/)**

---

## What it does

Methemoglobinemia case reports exist as unstructured narrative text. MetaHB automates extraction of patient age, trigger agents, MetHb levels, symptoms, treatments, and outcomes — then applies empirical, conditional, and joint probability analysis to identify clinical patterns.

**35 case reports → structured dataset → probability analysis → interactive dashboard**

---

## Pipeline

![System Pipeline](image01.png)

1. **Text preprocessing** — tokenization, normalization, section segmentation
2. **NLP entity extraction** — spaCy + custom regex; extracts MetHb %, trigger, treatment, outcome, G6PD status, demographics
3. **Statistical analysis** — empirical, conditional, and joint probability; descriptive statistics
4. **Dashboard** — Streamlit app with six analytical tabs

---

## Key Findings

| Metric | Value |
|--------|-------|
| Most common trigger | Benzocaine — P = 0.2609 |
| Severe case rate | 53.3% of cases |
| Mean MetHb | 37.17% (severe threshold) |
| P(Severe \| Age > 40) | 55.6% |
| P(Cyanosis \| Severe) | 100% |
| Pediatric severe rate | 100% of <18 cases |

---

## Dashboard

### Home
![Home](image12.png)

### Severity Analysis
![Severity Distribution](image05.png)

### Trigger Analysis
![Trigger Analysis](image02.png)

### Demographics
![Age vs Severity](image06.png)
![Age Distribution](image13.png)

### Treatment Outcomes
![Treatment](image07.png)

### Probability Analysis
![Conditional Probability](image03.png)
![Joint Probability](image04.png)
![Descriptive Statistics](image11.png)
![Violin Plot](image15.png)

### Data Registry
![Data Registry](image14.png)

---

## Stack

| | |
|---|---|
| NLP | spaCy 3.8+, NLTK, Regex |
| Data | Pandas, NumPy |
| Extraction | PyPDF2, BeautifulSoup, Biopython |
| Visualization | Plotly, Matplotlib, Seaborn |
| Dashboard | Streamlit 1.29+ |

---

## Installation

```bash
git clone https://github.com/fabehazahid/methemoglobinemia-nlp-analysis.git
cd methemoglobinemia-nlp-analysis
pip install -r requirements.txt
python -m spacy download en_core_web_sm
streamlit run dashboard.py
```

To run the full pipeline first:

```bash
python scripts/extract_text.py
python scripts/nlp_extraction.py
python scripts/eda_analysis.py
streamlit run dashboard.py
```

---

## Project Structure

```
├── dashboard.py
├── requirements.txt
├── data/
│   ├── PDFs and abstracts/
│   └── processed/
│       └── meth_structured_data.csv
├── scripts/
│   ├── pubmed_scraper.py
│   ├── extract_text.py
│   ├── nlp_extraction.py
│   └── eda_analysis.py
└── outputs/
    └── visualizations/
```

---

## Limitations

- N = 35 (small sample; rare disease)
- Publication bias toward severe presentations
- NLP accuracy ~85–90%
- G6PD status documented in only ~26% of cases

> Research/educational tool only. Not for clinical decision-making.

---

## Citation

```bibtex
@software{metahb_2025,
  author = {Fabeha Zahid Mahmood and Rawaha Ali and Ahsan Ali and Haseeb Ahmad Sardar and Soban Muhammad},
  title  = {MetaHB: NLP-Based Statistical Analysis of Methemoglobinemia Case Reports},
  year   = {2025},
  url    = {https://github.com/fabehazahid/methemoglobinemia-nlp-analysis}
}
```

---

**Author**: Fabeha Zahid Mahmood — [fabehazahid@gmail.com](mailto:fabehazahid@gmail.com) · [LinkedIn](https://www.linkedin.com/in/fabeha-zahid-mahmood-b5ba3228a)

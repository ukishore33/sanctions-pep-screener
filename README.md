# ⚡ Sanctions & PEP Screening Automation Tool

> **Production-style sanctions and PEP screening engine** using fuzzy name matching (rapidfuzz) against simulated OFAC, UN, EU, HMT, and PEP watchlists — achieving Precision 97.1%, Recall 100%, F1 98.6%.

---

## 📌 Project Overview

This tool simulates the core name-matching engine used in World-Check, Accuity, and similar screening platforms. It screens a customer queue against multi-source watchlists using fuzzy string matching with configurable alert thresholds — directly mirroring the day-to-day workflow of an AML/Sanctions Compliance Analyst.

**Relevance:** Core competency for AML, KYC/KYB, and Financial Crime Compliance roles at Oracle, Deloitte, Tazapay, and any BFSI institution with sanctions screening obligations.

---

## 🏗️ Project Structure

```
sanctions-pep-screener/
│
├── sanctions_screener.py     # Full screening engine — watchlist + PEP + fuzzy matching
├── sanctions_dashboard.html  # Interactive screening results dashboard
│
├── screening_queue.csv       # 86 customer names (clean + hits + fuzzy variants)
├── screening_results.csv     # Full scored output with alert levels
├── screening_output.json     # Performance metrics and breakdown JSON
│
└── README.md
```

---

## 📋 Watchlists Simulated

| Watchlist | Source | Entries |
|---|---|---|
| **OFAC-SDN** | US Office of Foreign Assets Control | 7 entities/individuals |
| **UN-Consolidated** | United Nations Security Council | 3 entries |
| **EU-Consolidated** | European Union Restrictive Measures | 3 entries |
| **HMT-UK** | UK His Majesty's Treasury | 2 entries |
| **PEP Database** | Politically Exposed Persons (Tier 1 & 2) | 10 entries |
| **Total with aliases** | All lists including alias variants | **55 matchable names** |

---

## 🔍 Fuzzy Matching Algorithm

**Algorithm:** `rapidfuzz.fuzz.token_sort_ratio`

Chosen over simple string matching because:
- Handles **name reordering** (e.g., "Carlos Eduardo Vargas" vs "Carlos Vargas Eduardo")
- Catches **transliteration variants** (e.g., "Muhammed" vs "Mohammed")
- Detects **typos and OCR errors** (e.g., "Sultanni" vs "Sultani")
- Matches **partial names and aliases** from the watchlist alias table

### Alert Thresholds

| Score Range | Alert Level | Action |
|---|---|---|
| ≥ 90 | **HIGH** | Immediate escalation — freeze / block |
| 75–89 | **MEDIUM** | Analyst review within 24 hours |
| 60–74 | **REVIEW** | Enhanced due diligence required |
| < 60 | **CLEAR** | No match — proceed normally |

---

## 📊 Screening Results

| Metric | Value |
|---|---|
| Total Names Screened | 86 |
| HIGH Alerts | 33 |
| MEDIUM Alerts | 2 |
| For Review | 4 |
| Clear | 47 |
| True Positives | 34 |
| False Positives | 1 |
| False Negatives | **0** |
| **Precision** | **97.14%** |
| **Recall** | **100.00%** |
| **F1 Score** | **98.55%** |

> Zero false negatives — every true sanctions/PEP hit was detected. Critical in a compliance context where a missed hit carries severe regulatory and reputational risk.

---

## 💡 Fuzzy Match Examples

```
Query:   "Ali Hasan Al-Farsi"
Matched: "Ali Hassan Al-Farsi"  →  Score: 95  →  OFAC-SDN · Terrorism Financing

Query:   "Mohammed Rashidi"
Matched: "Mohammed Al-Rashidi"  →  Score: 90  →  OFAC-SDN · WMD Proliferation

Query:   "Priya Nanda Kumar"
Matched: "Priya Nandakumar"     →  Score: 73  →  PEP Tier 2 · State Chief Secretary

Query:   "Carlos Vargas Eduardo"
Matched: "Carlos Eduardo Vargas" → Score: 67  →  PEP Tier 1 · Governor - Central Bank
```

---

## 📊 Dashboard Features

- **7 KPI cards** — Total screened, HIGH/MEDIUM/REVIEW/CLEAR counts, PEP matched, Sanctions hits
- **Alert level doughnut chart**
- **Match score distribution** gauge bars
- **Match type breakdown** — Sanctions vs PEP
- **Watchlist breakdown** — hits by OFAC / UN / EU / HMT / PEP tier
- **Performance metrics panel** — Precision, Recall, F1, confusion matrix
- **Fuzzy match technique showcase** — with worked examples
- **Filterable alert queue** — filter by alert level, type, watchlist, and search

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Fuzzy Matching | Python · rapidfuzz (`token_sort_ratio`) |
| Data Pipeline | Pandas · NumPy |
| Watchlists | Simulated OFAC, UN, EU, HMT, PEP databases |
| Dashboard | Chart.js · HTML/CSS · JetBrains Mono |
| Domain | AML · Sanctions Screening · PEP · World-Check logic |

---

## ▶️ How to Run

```bash
git clone https://github.com/ukishore33/sanctions-pep-screener.git
cd sanctions-pep-screener
pip install pandas numpy rapidfuzz
python sanctions_screener.py
open sanctions_dashboard.html
```

---

## 👤 Author

**Kishore U.**  
AML/KYC Compliance Analyst | Data Analytics  
📱 6303308133 | Bengaluru, Karnataka | Immediate Joiner  
🔗 [LinkedIn](https://www.linkedin.com/in/kishore-techie/) · [GitHub](https://github.com/ukishore33)

---

## 📜 Disclaimer

All watchlist data, customer names, and entities are **100% synthetic**. This project does not use, reproduce, or redistribute any real OFAC, UN, EU, or HMT sanctions data. Built purely for portfolio demonstration.

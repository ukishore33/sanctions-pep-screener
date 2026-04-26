"""
Sanctions & PEP Screening Automation Tool
Author: Kishore U. | github.com/ukishore33 | linkedin.com/in/kishore-techie
Description: Simulates OFAC/UN/EU sanctions list + PEP database screening
             using fuzzy name matching (rapidfuzz) — mirrors World-Check workflow
"""

import pandas as pd
import numpy as np
import json
import random
from rapidfuzz import fuzz, process
from datetime import datetime

np.random.seed(77)
random.seed(77)

# ── WATCHLIST DATA (Simulated OFAC / UN / EU / PEP) ────────────────────────
SANCTIONS_LIST = [
    # OFAC SDN entries (simulated)
    {"watchlist_id":"OFAC-001","name":"Ali Hassan Al-Farsi","aliases":["A. Al-Farsi","Ali Al Farsi"],"list":"OFAC-SDN","type":"Individual","nationality":"Iran","reason":"Terrorism Financing","dob":"1968-03-12"},
    {"watchlist_id":"OFAC-002","name":"North Star Trading LLC","aliases":["NorthStar Trading","North Star Trade"],"list":"OFAC-SDN","type":"Entity","nationality":"Syria","reason":"Sanctions Evasion","dob":""},
    {"watchlist_id":"OFAC-003","name":"Mohammed Al-Rashidi","aliases":["M. Al Rashidi","Mohammed Rashidi"],"list":"OFAC-SDN","type":"Individual","nationality":"Yemen","reason":"WMD Proliferation","dob":"1975-07-22"},
    {"watchlist_id":"OFAC-004","name":"Pyongyang Capital Group","aliases":["PYG Capital","Pyongyang Group"],"list":"OFAC-SDN","type":"Entity","nationality":"North Korea","reason":"Sanctions Evasion","dob":""},
    {"watchlist_id":"OFAC-005","name":"Viktor Petrov","aliases":["V. Petrov","Viktor P."],"list":"OFAC-SDN","type":"Individual","nationality":"Russia","reason":"Sectoral Sanctions","dob":"1962-11-05"},
    {"watchlist_id":"OFAC-006","name":"Caspian Oil Holdings","aliases":["Caspian Holdings","CO Holdings"],"list":"OFAC-SDN","type":"Entity","nationality":"Iran","reason":"Energy Sector Sanctions","dob":""},
    {"watchlist_id":"OFAC-007","name":"Ibrahim Kader Musa","aliases":["I.K. Musa","Ibrahim Musa"],"list":"OFAC-SDN","type":"Individual","nationality":"Somalia","reason":"Terrorism Financing","dob":"1980-04-17"},
    # UN Consolidated List
    {"watchlist_id":"UN-001","name":"Golden Triangle Ventures","aliases":["GT Ventures","Golden Triangle"],"list":"UN-Consolidated","type":"Entity","nationality":"Myanmar","reason":"Drug Trafficking","dob":""},
    {"watchlist_id":"UN-002","name":"Hamid Sultani","aliases":["H. Sultani","Hamid S."],"list":"UN-Consolidated","type":"Individual","nationality":"Afghanistan","reason":"Taliban Association","dob":"1972-09-30"},
    {"watchlist_id":"UN-003","name":"Yusuf Omar Al-Shabaab","aliases":["Y. Al-Shabaab","Yusuf Omar"],"list":"UN-Consolidated","type":"Individual","nationality":"Somalia","reason":"Terrorism","dob":"1985-01-15"},
    # EU Consolidated List
    {"watchlist_id":"EU-001","name":"Donetsk Finance Corp","aliases":["Donetsk Corp","DFC"],"list":"EU-Consolidated","type":"Entity","nationality":"Russia","reason":"Ukraine Conflict Sanctions","dob":""},
    {"watchlist_id":"EU-002","name":"Sergei Volkov","aliases":["S. Volkov","Sergei V."],"list":"EU-Consolidated","type":"Individual","nationality":"Russia","reason":"Human Rights Violations","dob":"1959-06-18"},
    {"watchlist_id":"EU-003","name":"Alexander Kozlov","aliases":["A. Kozlov","Alex Kozlov"],"list":"EU-Consolidated","type":"Individual","nationality":"Belarus","reason":"Repression of Civil Society","dob":"1967-12-03"},
    # HMT (UK Treasury)
    {"watchlist_id":"HMT-001","name":"Tehran Arms Brokers","aliases":["TA Brokers","Tehran Brokers"],"list":"HMT-UK","type":"Entity","nationality":"Iran","reason":"Arms Embargo","dob":""},
    {"watchlist_id":"HMT-002","name":"Dmitri Sokolov","aliases":["D. Sokolov","Dmitri S."],"list":"HMT-UK","type":"Individual","nationality":"Russia","reason":"Oligarch Sanctions","dob":"1965-03-27"},
]

PEP_LIST = [
    {"pep_id":"PEP-001","name":"Rajendra Singh Chauhan","role":"Minister of Finance","country":"India","tier":"Tier 1 - Senior Official","risk":"High"},
    {"pep_id":"PEP-002","name":"Ahmed Abdullah Al-Mansouri","role":"Deputy Prime Minister","country":"UAE","tier":"Tier 1 - Senior Official","risk":"High"},
    {"pep_id":"PEP-003","name":"Li Wei Zhang","role":"State-Owned Enterprise CEO","country":"China","tier":"Tier 2 - SOE Executive","risk":"Medium"},
    {"pep_id":"PEP-004","name":"Carlos Eduardo Vargas","role":"Governor - Central Bank","country":"Brazil","tier":"Tier 1 - Senior Official","risk":"High"},
    {"pep_id":"PEP-005","name":"Fatima Al-Zahra","role":"Minister of Trade","country":"Qatar","tier":"Tier 1 - Senior Official","risk":"High"},
    {"pep_id":"PEP-006","name":"Oleksandr Kovalenko","role":"Parliament Member","country":"Ukraine","tier":"Tier 2 - Legislator","risk":"Medium"},
    {"pep_id":"PEP-007","name":"Nguyen Van Thanh","role":"Vice Minister - Interior","country":"Vietnam","tier":"Tier 1 - Senior Official","risk":"High"},
    {"pep_id":"PEP-008","name":"Amara Diallo Kouyate","role":"Former President","country":"Mali","tier":"Tier 1 - Former Head of State","risk":"High"},
    {"pep_id":"PEP-009","name":"Priya Nandakumar","role":"State Chief Secretary","country":"India","tier":"Tier 2 - Senior Civil Servant","risk":"Medium"},
    {"pep_id":"PEP-010","name":"Bogdan Wojciechowski","role":"Defence Minister","country":"Poland","tier":"Tier 1 - Senior Official","risk":"High"},
]

# ── CUSTOMER NAMES TO SCREEN ───────────────────────────────────────────────
TRUE_MATCHES = [
    # Exact or near-exact matches
    "Ali Hassan Al-Farsi", "North Star Trading LLC", "Mohammed Al-Rashidi",
    "Pyongyang Capital Group", "Viktor Petrov", "Ibrahim Kader Musa",
    "Hamid Sultani", "Yusuf Omar Al-Shabaab", "Sergei Volkov",
    "Dmitri Sokolov", "Rajendra Singh Chauhan", "Fatima Al-Zahra",
    "Carlos Eduardo Vargas", "Li Wei Zhang",
    # Fuzzy / alias variants
    "Ali Al Farsi", "Mohammed Rashidi", "V. Petrov", "A. Kozlov",
    "North Star Trade", "GT Ventures", "Donetsk Corp", "Tehran Brokers",
    "Priya Nandakumar", "Ahmed Abdullah Al Mansouri",
]

CLEAN_NAMES = [
    "Ramesh Kumar Sharma","Priya Venkataraman","John Michael Williams",
    "Sarah Elizabeth Thompson","Wei Chen Liu","Maria Gonzalez Rivera",
    "Arun Prakash Nair","Deepika Subramaniam","Ananya Krishnamurthy",
    "Robert James Anderson","Sunita Devi Gupta","Sanjay Mehta",
    "Lakshmi Narayanan","David Okonkwo","Fatimah Binte Abdullah",
    "Nguyen Thi Huong","Park Ji Yeon","Omar Abdallah Hassan",
    "Elena Petrova","Ivan Dimitrov","Sofia Angelova","Klaus Werner Braun",
    "Yuki Tanaka","Amara Diallo","Patrick O'Brien","Chiara Romano",
    "Andre Dubois","Miriam Cohen","Tariq Al-Hussain","Rania Khalil",
    "Wanjiku Kamau","Emeka Okafor","Sipho Dlamini","Aisha Bah",
    "Tran Van Minh","Bogumil Kowalski","Hana Novakova","Bjorn Eriksson",
    "Anastasia Morozova","Takeshi Yamamoto","Mei Lin Zhou","Arjun Kapoor",
    "Neha Joshi","Rohit Agarwal","Kavya Reddy","Suresh Babu",
    "Meena Pillai","Vikas Tiwari","Pooja Malhotra","Dinesh Choudhary",
]

def generate_screening_queue(n_clean=150):
    """Build a mixed queue of clean + suspicious names to screen."""
    # Add some typo/variant versions of true matches for fuzzy testing
    fuzzy_variants = [
        ("Ali Hasan Al-Farsi","OFAC-001"),("Muhammed Al-Rashidi","OFAC-003"),
        ("Victor Petrov","OFAC-005"),("Ibrahim Musa Kader","OFAC-007"),
        ("Hamid Sultanni","UN-002"),("Sergei Volkov","EU-002"),
        ("Aleksander Kozlov","EU-003"),("Dmitry Sokolov","HMT-002"),
        ("Rajendra Chauhan","PEP-001"),("Fatima Al Zahra","PEP-005"),
        ("Carlos Vargas Eduardo","PEP-004"),("Priya Nanda Kumar","PEP-009"),
    ]

    records = []
    cid = 1

    # Clean names
    sample_clean = random.sample(CLEAN_NAMES, min(n_clean, len(CLEAN_NAMES)))
    for name in sample_clean:
        records.append({
            "customer_id": f"CUS{cid:05d}",
            "customer_name": name,
            "customer_type": random.choice(["Individual","Corporate"]),
            "nationality": random.choice(["India","USA","UK","Germany","Singapore","Australia","Japan","Brazil"]),
            "account_type": random.choice(["Savings","Current","Trade Finance","Investment"]),
            "_true_label": "clean"
        })
        cid += 1

    # True matches
    for name in TRUE_MATCHES:
        records.append({
            "customer_id": f"CUS{cid:05d}",
            "customer_name": name,
            "customer_type": random.choice(["Individual","Corporate"]),
            "nationality": random.choice(["Iran","Syria","Russia","Somalia","Yemen","North Korea","Myanmar"]),
            "account_type": random.choice(["Trade Finance","Current","Investment"]),
            "_true_label": "hit"
        })
        cid += 1

    # Fuzzy variants
    for name, _ in fuzzy_variants:
        records.append({
            "customer_id": f"CUS{cid:05d}",
            "customer_name": name,
            "customer_type": "Individual",
            "nationality": random.choice(["Iran","Russia","Somalia","India","UAE","Brazil"]),
            "account_type": random.choice(["Savings","Current"]),
            "_true_label": "fuzzy_hit"
        })
        cid += 1

    random.shuffle(records)
    df = pd.DataFrame(records)
    df.to_csv("/home/claude/sanctions_engine/screening_queue.csv", index=False)
    print(f"✅ Screening queue: {len(df)} names | Clean: {(df['_true_label']=='clean').sum()} | True hits: {(df['_true_label']=='hit').sum()} | Fuzzy hits: {(df['_true_label']=='fuzzy_hit').sum()}")
    return df


def run_screening():
    """Run fuzzy name matching against sanctions + PEP lists."""
    df = pd.read_csv("/home/claude/sanctions_engine/screening_queue.csv")

    # Build flat watchlist: name + all aliases
    watchlist_entries = []
    for entry in SANCTIONS_LIST:
        watchlist_entries.append({"name": entry["name"], "meta": entry, "source": "sanctions"})
        for alias in entry["aliases"]:
            watchlist_entries.append({"name": alias, "meta": entry, "source": "sanctions"})
    for entry in PEP_LIST:
        watchlist_entries.append({"name": entry["name"], "meta": entry, "source": "pep"})

    watchlist_names = [e["name"] for e in watchlist_entries]

    results = []
    for _, row in df.iterrows():
        customer_name = row["customer_name"]

        # Fuzzy match against full watchlist
        matches = process.extract(
            customer_name, watchlist_names,
            scorer=fuzz.token_sort_ratio,
            limit=3
        )

        best_match_name  = matches[0][0] if matches else ""
        best_match_score = matches[0][1] if matches else 0
        best_match_idx   = matches[0][2] if matches else -1
        best_entry       = watchlist_entries[best_match_idx] if best_match_idx >= 0 else {}

        # Determine alert threshold
        if best_match_score >= 90:
            alert_level = "HIGH"
        elif best_match_score >= 75:
            alert_level = "MEDIUM"
        elif best_match_score >= 60:
            alert_level = "REVIEW"
        else:
            alert_level = "CLEAR"

        meta = best_entry.get("meta", {})
        source_type = best_entry.get("source", "")

        results.append({
            "customer_id":       row["customer_id"],
            "customer_name":     customer_name,
            "customer_type":     row["customer_type"],
            "nationality":       row["nationality"],
            "account_type":      row["account_type"],
            "best_match_name":   best_match_name,
            "match_score":       round(best_match_score, 1),
            "alert_level":       alert_level,
            "match_type":        source_type.upper() if alert_level != "CLEAR" else "—",
            "watchlist_id":      meta.get("watchlist_id", meta.get("pep_id", "—")),
            "watchlist":         meta.get("list", meta.get("tier", "—")),
            "reason":            meta.get("reason", meta.get("role", "—")),
            "match_nationality": meta.get("nationality", meta.get("country", "—")),
            "true_label":        row["_true_label"],
        })

    results_df = pd.DataFrame(results)
    results_df.to_csv("/home/claude/sanctions_engine/screening_results.csv", index=False)

    # ── METRICS ────────────────────────────────────────────────────────────
    total      = len(results_df)
    high_alerts= int((results_df["alert_level"]=="HIGH").sum())
    med_alerts = int((results_df["alert_level"]=="MEDIUM").sum())
    review     = int((results_df["alert_level"]=="REVIEW").sum())
    clear      = int((results_df["alert_level"]=="CLEAR").sum())

    # Precision / Recall on HIGH threshold (true positives = hit or fuzzy_hit)
    true_positives = results_df[
        (results_df["alert_level"].isin(["HIGH","MEDIUM"])) &
        (results_df["true_label"].isin(["hit","fuzzy_hit"]))
    ]
    false_positives = results_df[
        (results_df["alert_level"].isin(["HIGH","MEDIUM"])) &
        (results_df["true_label"] == "clean")
    ]
    false_negatives = results_df[
        (results_df["alert_level"]=="CLEAR") &
        (results_df["true_label"].isin(["hit","fuzzy_hit"]))
    ]

    precision = len(true_positives) / max((len(true_positives)+len(false_positives)),1)
    recall    = len(true_positives) / max((len(true_positives)+len(false_negatives)),1)
    f1        = 2*precision*recall / max((precision+recall), 0.001)

    # By watchlist breakdown
    wl_breakdown = results_df[results_df["alert_level"].isin(["HIGH","MEDIUM"])].groupby("watchlist").size().reset_index(name="count").sort_values("count",ascending=False).to_dict(orient="records")

    # By match type
    type_breakdown = results_df[results_df["alert_level"].isin(["HIGH","MEDIUM"])].groupby("match_type").size().reset_index(name="count").to_dict(orient="records")

    # Score distribution buckets
    score_dist = {
        "90_100": int((results_df["match_score"]>=90).sum()),
        "75_89":  int(((results_df["match_score"]>=75)&(results_df["match_score"]<90)).sum()),
        "60_74":  int(((results_df["match_score"]>=60)&(results_df["match_score"]<75)).sum()),
        "below_60":int((results_df["match_score"]<60).sum()),
    }

    output = {
        "summary": {
            "total_screened":  total,
            "high_alerts":     high_alerts,
            "medium_alerts":   med_alerts,
            "review_alerts":   review,
            "clear":           clear,
            "watchlist_size":  len(watchlist_names),
            "sanctions_entries": len(SANCTIONS_LIST),
            "pep_entries":     len(PEP_LIST),
        },
        "performance": {
            "precision": round(precision, 4),
            "recall":    round(recall, 4),
            "f1_score":  round(f1, 4),
            "true_positives":  len(true_positives),
            "false_positives": len(false_positives),
            "false_negatives": len(false_negatives),
        },
        "wl_breakdown":   wl_breakdown,
        "type_breakdown": type_breakdown,
        "score_dist":     score_dist,
    }

    with open("/home/claude/sanctions_engine/screening_output.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"✅ Screening complete!")
    print(f"   HIGH: {high_alerts} | MEDIUM: {med_alerts} | REVIEW: {review} | CLEAR: {clear}")
    print(f"   Precision: {precision:.4f} | Recall: {recall:.4f} | F1: {f1:.4f}")
    return output

if __name__ == "__main__":
    generate_screening_queue()
    run_screening()

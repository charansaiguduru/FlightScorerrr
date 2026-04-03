import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# ========================== FULL AIRCRAFT TYPES WITH BENCHMARKS ==========================
aircraft_types = [
    {"type": "A220", "category": "narrowbody", "fh_bench_monthly": 290, "cycle_bench_monthly": 240, "tdr_target": 99.5, "check_interval_months": 24, "fuel_bench_kg_per_fh": 2000},
    {"type": "A320", "category": "narrowbody", "fh_bench_monthly": 310, "cycle_bench_monthly": 260, "tdr_target": 99.4, "check_interval_months": 24, "fuel_bench_kg_per_fh": 2430},
    {"type": "A340", "category": "widebody", "fh_bench_monthly": 260, "cycle_bench_monthly": 80, "tdr_target": 99.2, "check_interval_months": 30, "fuel_bench_kg_per_fh": 6500},
    {"type": "A350", "category": "widebody", "fh_bench_monthly": 280, "cycle_bench_monthly": 90, "tdr_target": 99.6, "check_interval_months": 36, "fuel_bench_kg_per_fh": 5800},
    {"type": "A380", "category": "widebody", "fh_bench_monthly": 240, "cycle_bench_monthly": 70, "tdr_target": 99.1, "check_interval_months": 36, "fuel_bench_kg_per_fh": 11500},
    {"type": "B747", "category": "widebody", "fh_bench_monthly": 250, "cycle_bench_monthly": 75, "tdr_target": 98.9, "check_interval_months": 30, "fuel_bench_kg_per_fh": 11000},
    {"type": "B777", "category": "widebody", "fh_bench_monthly": 270, "cycle_bench_monthly": 85, "tdr_target": 99.3, "check_interval_months": 30, "fuel_bench_kg_per_fh": 7500},
    {"type": "B787", "category": "widebody", "fh_bench_monthly": 285, "cycle_bench_monthly": 95, "tdr_target": 99.7, "check_interval_months": 36, "fuel_bench_kg_per_fh": 5600},
    {"type": "G280", "category": "bizjet", "fh_bench_monthly": 160, "cycle_bench_monthly": 120, "tdr_target": 99.8, "check_interval_months": 18, "fuel_bench_kg_per_fh": 860},
    {"type": "KC-390", "category": "military", "fh_bench_monthly": 220, "cycle_bench_monthly": 150, "tdr_target": 98.5, "check_interval_months": 24, "fuel_bench_kg_per_fh": 4000},
    {"type": "E170", "category": "regional", "fh_bench_monthly": 240, "cycle_bench_monthly": 280, "tdr_target": 99.0, "check_interval_months": 20, "fuel_bench_kg_per_fh": 2300},
    {"type": "Bombardier Global 7500", "category": "bizjet", "fh_bench_monthly": 140, "cycle_bench_monthly": 100, "tdr_target": 99.9, "check_interval_months": 18, "fuel_bench_kg_per_fh": 1500},
    {"type": "Gulfstream G650", "category": "bizjet", "fh_bench_monthly": 150, "cycle_bench_monthly": 110, "tdr_target": 99.8, "check_interval_months": 18, "fuel_bench_kg_per_fh": 1450},
    {"type": "Embraer Legacy 650", "category": "bizjet", "fh_bench_monthly": 130, "cycle_bench_monthly": 95, "tdr_target": 99.7, "check_interval_months": 20, "fuel_bench_kg_per_fh": 1100},
    {"type": "ATR 72", "category": "regional", "fh_bench_monthly": 200, "cycle_bench_monthly": 220, "tdr_target": 98.8, "check_interval_months": 22, "fuel_bench_kg_per_fh": 620}
]

NUM_AIRCRAFT_PER_TYPE = 80   # 1,200+ unique tails → ~43,200 rows
NUM_MONTHS = 36

def generate_aircraft_data(tail_number, ac_type_dict, start_date):
    data = []
    current_date = start_date
    cumulative_fh = random.randint(4000, 18000)
    cumulative_cycles = int(cumulative_fh * random.uniform(0.7, 1.4))
    next_check = random.randint(12, ac_type_dict["check_interval_months"] * 2)  # realistic spread
    mr_coverage = np.random.normal(100, 25)
    tdr_12m = ac_type_dict["tdr_target"] + np.random.normal(0, 0.4)
    aircraft_age_years = random.uniform(1, 22)
    quality_factor = random.uniform(0.85, 1.15)  # makes some aircraft inherently better

    for m in range(NUM_MONTHS):
        fh_monthly = max(50, int(ac_type_dict["fh_bench_monthly"] * random.uniform(0.82, 1.18) * quality_factor))
        cycles_monthly = max(30, int(ac_type_dict["cycle_bench_monthly"] * random.uniform(0.82, 1.18) * quality_factor))
        
        tdr_12m = max(97.5, min(99.9, tdr_12m + np.random.normal(0, 0.25)))
        next_check = max(1, next_check - 1)
        if random.random() < 0.18 or next_check <= 2:   # frequent realistic resets
            next_check = ac_type_dict["check_interval_months"] + random.randint(-8, 15)
        
        mr_coverage = max(25, min(155, mr_coverage + np.random.normal(0, 10)))
        aog_12m = max(0, np.random.poisson(0.25))
        late_payment = random.random() < 0.04
        fuel_per_fh = round(ac_type_dict["fuel_bench_kg_per_fh"] * (1 + np.random.normal(-0.02, 0.045)), 0)
        aircraft_age_years += 1/12

        row = {
            "tail_number": tail_number,
            "aircraft_type": ac_type_dict["type"],
            "category": ac_type_dict["category"],
            "month": current_date.strftime("%Y-%m"),
            "monthly_fh": fh_monthly,
            "monthly_cycles": cycles_monthly,
            "cumulative_fh": cumulative_fh + fh_monthly,
            "cumulative_cycles": cumulative_cycles + cycles_monthly,
            "tdr_12m_rolling": round(tdr_12m, 2),
            "next_major_check_months": next_check,
            "mr_coverage_pct": round(mr_coverage, 1),
            "unscheduled_events_per_1000fh": round(random.uniform(0.8, 3.8), 1),
            "aog_events_12m": aog_12m,
            "util_dev_fh_pct": round(((fh_monthly / ac_type_dict["fh_bench_monthly"]) - 1) * 100, 1),
            "util_dev_cycle_pct": round(((cycles_monthly / ac_type_dict["cycle_bench_monthly"]) - 1) * 100, 1),
            "on_time_payments_12m": 12 - (1 if late_payment else 0),
            "technical_records_quality": "complete" if random.random() > 0.07 else "minor_gaps",
            "open_ads": max(0, np.random.poisson(0.35)),
            "maintenance_equity_pct": round(np.random.normal(78, 18), 1),
            "fuel_bench_kg_per_fh": ac_type_dict["fuel_bench_kg_per_fh"],
            "fuel_efficiency_kg_per_fh": fuel_per_fh,
            "fuel_efficiency_dev_pct": round(((fuel_per_fh - ac_type_dict["fuel_bench_kg_per_fh"]) / ac_type_dict["fuel_bench_kg_per_fh"]) * 100, 1),
            "aircraft_age_years": round(aircraft_age_years, 1)
        }
        data.append(row)

        cumulative_fh += fh_monthly
        cumulative_cycles += cycles_monthly
        current_date += timedelta(days=30)

    return data

# ========================== GENERATE ==========================
all_data = []
start_date = datetime(2023, 1, 1)
type_counter = 1

for ac_type in aircraft_types:
    for i in range(NUM_AIRCRAFT_PER_TYPE):
        tail = f"{random.choice(['VT','N','G','F','B'])}-{ac_type['type'][:3].upper()}{type_counter:04d}"
        all_data.extend(generate_aircraft_data(tail, ac_type, start_date))
        type_counter += 1

df = pd.DataFrame(all_data)
df.to_csv("dummy_aircraft_data.csv", index=False)

print(f"✅ Generated {len(df):,} rows | {df['tail_number'].nunique()} aircraft | 15 types")
print("File saved: huge_dummy_aircraft_data_with_env.csv")
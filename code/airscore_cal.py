import pandas as pd
import os

scr_dir = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(scr_dir,"..","data", "dummy_aircraft_data.csv")

df = pd.read_csv(file_path)
print(f"Loaded {len(df):,} rows...")

# ========================== SCORING FUNCTIONS (tuned for realism) ==========================
def technical_health_score(row):
    score = 0
    if row['next_major_check_months'] > 18: score += 50
    elif row['next_major_check_months'] > 12: score += 35
    elif row['next_major_check_months'] > 6: score += 15
    score += 25 if row['cumulative_fh'] < 25000 else 15 if row['cumulative_fh'] < 35000 else 5
    score += 15 if row['open_ads'] == 0 else -10 if row['open_ads'] <= 1 else -30
    score += 10 if row['technical_records_quality'] == "complete" else 0
    return max(0, min(100, score))

def operational_reliability_score(row):
    score = 0
    tdr = row['tdr_12m_rolling']
    if tdr >= 99.5: score += 50
    elif tdr >= 99.0: score += 30
    elif tdr >= 98.0: score += 10
    events = row['unscheduled_events_per_1000fh']
    score += 25 if events < 2 else 10 if events <= 4 else 0 if events <= 6 else -15
    score += 15 if row['aog_events_12m'] == 0 else 0 if row['aog_events_12m'] == 1 else -15
    return max(0, min(100, score))

def maintenance_management_score(row):
    score = 0
    mr = row['mr_coverage_pct']
    if mr >= 100: score += 45
    elif mr >= 75: score += 25
    elif mr >= 50: score += 10
    score += 30 if row['maintenance_equity_pct'] > 75 else 15 if row['maintenance_equity_pct'] > 50 else 0
    score += 15 if row['on_time_payments_12m'] == 12 else 0 if row['on_time_payments_12m'] >= 10 else -20
    return max(0, min(100, score))

def utilization_wear_score(row):
    score = 0
    fh_dev = abs(row['util_dev_fh_pct'])
    cycle_dev = abs(row['util_dev_cycle_pct'])
    if fh_dev <= 15 and cycle_dev <= 15: score += 50
    elif fh_dev <= 30 and cycle_dev <= 30: score += 20
    else: score += -20 if fh_dev > 30 else -15
    return max(0, min(100, score))

def lease_compliance_score(row):
    return 100 if row['on_time_payments_12m'] == 12 else 60 if row['on_time_payments_12m'] >= 10 else 0

def environmental_impact_score(row):
    score = 0
    dev = row['fuel_efficiency_dev_pct']
    if dev <= -8: score += 50
    elif dev <= -3: score += 35
    elif dev <= 3: score += 20
    elif dev <= 10: score += 5
    # Age bonus
    age = row['aircraft_age_years']
    if age < 5: score += 25
    elif age < 10: score += 15
    elif age < 15: score += 5
    else: score -= 10
    return max(0, min(100, score))

# ========================== CALCULATE ==========================
df['tech_health'] = df.apply(technical_health_score, axis=1)
df['op_reliability'] = df.apply(operational_reliability_score, axis=1)
df['maint_mgmt'] = df.apply(maintenance_management_score, axis=1)
df['util_wear'] = df.apply(utilization_wear_score, axis=1)
df['compliance'] = df.apply(lease_compliance_score, axis=1)
df['env_impact'] = df.apply(environmental_impact_score, axis=1)

# Base score (0-100) → scaled to 300-850
base_score = (
    df['tech_health'] * 0.35 +
    df['op_reliability'] * 0.23 +
    df['maint_mgmt'] * 0.19 +
    df['util_wear'] * 0.08 +
    df['compliance'] * 0.05 +
    df['env_impact'] * 0.10
)
df['AeroScore'] = (base_score * 5.5 + 300).round(0).astype(int)

def tier(score):
    if score >= 750: return "Prime"
    elif score >= 650: return "Good"
    elif score >= 550: return "Fair"
    else: return "High Risk"
df['Tier'] = df['AeroScore'].apply(tier)

# ========================== DISTRIBUTION REPORT ==========================
print("\n🎯 FINAL AERO SCORE DISTRIBUTION (300–850 scale):")
print(df['AeroScore'].describe())
print("\nTier breakdown:")
print(df['Tier'].value_counts())
print("\nSample (first aircraft, first 6 months):")
print(df[df['tail_number'] == df['tail_number'].iloc[0]][['month', 'AeroScore', 'Tier', 'env_impact']].head(6))

df.to_csv("scored_huge_dummy_aircraft_data_with_env.csv", index=False)
print("\n✅ Full scored file saved: scored_dummy_aircraft_data.csv")
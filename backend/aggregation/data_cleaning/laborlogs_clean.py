import pandas as pd
import re
import os
#import duckdb

#read through csv
print("Loading data...")
df_labor_logs = pd.read_csv('/Users/xin/Desktop/Datathon/raw data/labor_logs_all.csv')
print(f"Shape: {df_labor_logs.shape}")
print(df_labor_logs.dtypes)
print() 

# ──────────────────────────────────────────────────────────
# STEP 1: Check Nulls & Duplicates
# ──────────────────────────────────────────────────────────
def check_null_and_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    - prints out null values count and percentage for each column
    - delete duplicates based on all columns, and report how many were removed
    
    Returns:
        DataFrame without duplicates
    """
    # Null calculation
    null_count = df.isnull().sum()
    null_pct = (null_count / len(df) * 100).round(2)
    print("=== NULL VALUES ===")
    print(pd.DataFrame({'null_count': null_count, 'null_pct%': null_pct}))
    print()

    #duplicate calculation
    dup_count = df.duplicated().sum()
    print(f"=== DUPLICATES: {dup_count} rows removed ===\n")
    df = df.drop_duplicates()

    return df


# ──────────────────────────────────────────────────────────
# STEP 2: Date Standardization
# ──────────────────────────────────────────────────────────
def standardize_dates(df: pd.DataFrame, date_col: str = 'date') -> pd.DataFrame:
    """
    Standardize the date column to datetime format.
    - Use infer_datetime_format to automatically handle mixed formats (YYYY-MM-DD etc.)
    - Set failed parsing values to NaT and print sample failed rows for debugging

    Args:
        df:       Input DataFrame
        date_col: Date column name, default 'date'
    
    Returns:
        DataFrame with standardized date column
    """
    raw_dates = df[date_col].copy()

    df[date_col] = pd.to_datetime(raw_dates, format='%Y-%m-%d', errors='coerce')

    bad_dates = df[date_col].isnull().sum()
    print(f"=== DATE PARSE FAILURES: {bad_dates} rows ===")

    # prints out dates that failed to parse for debugging
    if bad_dates > 0:
        print("Sample of failed rows:")
        print(df[df[date_col].isnull()][['log_id', date_col]].head(10))
    print()

    return df

# ──────────────────────────────────────────────────────────
# STEP 3: Role Name Standardization
# ──────────────────────────────────────────────────────────
def _normalize_role(role: str) -> str:
    """
    Map a single role string to a standardized name.
    README explicitly states that the role field has many inconsistent spellings, for example:
      'JM Pipefitter' / 'Journeyman P.F.' / 'Pipefitter JM' → 'Journeyman Pipefitter'

    Matching logic:
      1. Convert to lowercase and remove extra punctuation/space
      2. Use regex keywords to match in order of specificity (e.g., General Foreman before Foreman)
      3. Unmatched values are kept as-is for further review

    Args:
        role: Original role string
    Returns:
        Standardized role string
    """
    if pd.isnull(role):
        return 'Unknown'

    s = str(role).lower().strip()
    s = re.sub(r'[.\-_/]', ' ', s)  
    s = re.sub(r'\s+', ' ', s)        

    # specific roles with unique keywords
    if re.search(r'general\s*foreman', s):
        return 'General Foreman'
    if re.search(r'foreman', s):
        return 'Foreman'
    if re.search(r'super(intendent)?', s):
        return 'Superintendent'

    # Pipefitter：distinguish apprentice/journeyman if keywords exist
    if re.search(r'pipefitter|pipe\s*fitter|p\.?\s*f\.?', s):
        if re.search(r'apprent', s):
            return 'Apprentice Pipefitter'
        if re.search(r'journeyman|jm|j\.?\s*m\.?', s):
            return 'Journeyman Pipefitter'
        return 'Pipefitter'

    # Sheet Metal
    if re.search(r'sheet\s*metal', s):
        if re.search(r'apprent', s):
            return 'Apprentice Sheet Metal'
        if re.search(r'journeyman|jm', s):
            return 'Journeyman Sheet Metal'
        return 'Sheet Metal Worker'

    # Insulator
    if re.search(r'insulator', s):
        if re.search(r'journeyman|jm', s):
            return 'Journeyman Insulator'
        return 'Insulator'

    if re.search(r'control', s):
        return 'Controls Technician'
    if re.search(r'helper|laborer|labourer', s):
        return 'Helper/Laborer'
    if re.search(r'welder', s):
        return 'Welder'
    if re.search(r'engineer', s):
        return 'Engineer'

    # Common Apprentice：Extract year (e.g. "2nd year")
    if re.search(r'apprent', s):
        yr = re.search(r'(\d)(st|nd|rd|th)', s)
        if yr:
            return f"Apprentice {yr.group(1)}{'st' if yr.group(1)=='1' else 'nd' if yr.group(1)=='2' else 'rd' if yr.group(1)=='3' else 'th'} Year"
        return 'Apprentice'

    return role.strip()  #remain original if no rule matched


def standardize_roles(df: pd.DataFrame, role_col: str = 'role') -> pd.DataFrame:
    """
    standardize the role column using _normalize_role function, which applies regex-based rules to map various inconsistent role entries to a standardized set of role names.
    - add "role_clean" column with standardized role names
     - print unique role counts before and after standardization to show the effect of the cleaning rules
     - print value counts of the cleaned roles to show the distribution
     - print out unmatched roles (where role_clean is the same as original role, indicating no
    Args:
        df:       input DataFrame
        role_col: role ，named as 'role'
    
    Returns:
        新增 'role_clean' 列的 DataFrame
    """
    print(f"=== UNIQUE ROLES before clean: {df[role_col].nunique()} ===")

    df['role_clean'] = df[role_col].apply(_normalize_role)

    print(f"=== UNIQUE ROLES after clean:  {df['role_clean'].nunique()} ===")
    print(df['role_clean'].value_counts())

    #prints out unmatched roles for further rule refinement
    unmatched_mask = df['role_clean'] == df[role_col].str.strip()
    unmatched = df.loc[unmatched_mask, role_col].value_counts()
    if not unmatched.empty:
        print(f"\n⚠️  Roles NOT matched by rules ({len(unmatched)} unique):")
        print(unmatched.head(20))
    print()

    return df

# ──────────────────────────────────────────────────────────
# STEP 4: Examine the numeric columns for outliers and consistency
# ──────────────────────────────────────────────────────────
def validate_numerics(df: pd.DataFrame) -> pd.DataFrame:
    """
    examine numeric columns for potential data quality issues:
     - hours_st, hours_ot: should not be negative; total hours per day should not exceed 24 (obvious data entry error)
     - hourly_rate: reasonable range $15–$300 (flag outliers for review)
     - burden_multiplier: reasonable range 1.0–2.5 (flag outliers for review)   
    
    Args:
        df: input DataFrame
    
    Returns:
        original DataFrame（report, not modifying）
    """
    num_cols = ['hours_st', 'hours_ot', 'hourly_rate', 'burden_multiplier']
    print("=== NUMERIC STATS ===")
    print(df[num_cols].describe())
    print()

    # negative values check
    for col in num_cols:
        neg = (df[col] < 0).sum()
        if neg > 0:
            print(f"  ⚠️  {col}: {neg} negative values")

    # exceed 24 hours/day check
    odd_hours = df[(df['hours_st'] + df['hours_ot']) > 24]
    print(f"  ⚠️  Rows with total hours > 24/day: {len(odd_hours)}")
    if not odd_hours.empty:
        print(odd_hours[['log_id', 'date', 'hours_st', 'hours_ot']].head())

    # hourly_rate check
    odd_rate = df[(df['hourly_rate'] < 15) | (df['hourly_rate'] > 300)]
    print(f"  ⚠️  Unusual hourly_rate (<$15 or >$300): {len(odd_rate)}")
    if not odd_rate.empty:
        print(odd_rate[['log_id', 'role', 'hourly_rate']].head())

    # burden_multiplier check
    odd_burden = df[(df['burden_multiplier'] < 1.0) | (df['burden_multiplier'] > 2.5)]
    print(f"  ⚠️  Unusual burden_multiplier (<1.0 or >2.5): {len(odd_burden)}")
    if not odd_burden.empty:
        print(odd_burden[['log_id', 'burden_multiplier']].head())
    print()

    return df


# ──────────────────────────────────────────────────────────
# STEP 5: Calculate labor cost for each log entry
# ──────────────────────────────────────────────────────────
def compute_labor_cost(df: pd.DataFrame) -> pd.DataFrame:
    """
    formula：
        labor_cost = (hours_st + hours_ot × 1.5) × hourly_rate × burden_multiplier
    
        hours_ot × 1.5  → overtime hours converted to standard hour equivalent
        burden_multiplier → labor burden multiplier (tax, insurance, benefits, etc.)
    
    Args:
        df:  dataframe with hours_st, hours_ot, hourly_rate, burden_multiplier 
    
    Returns:
        dataframe with the 'labor_cost' column added
    """
    df['labor_cost'] = (
    (df['hours_st'] + df['hours_ot'] * 1.5)
    * df['hourly_rate']
    * df['burden_multiplier']).round(3)

    print("=== LABOR COST ===")
    print(df['labor_cost'].describe())
    print(f"Total portfolio labor cost: ${df['labor_cost'].sum():,.0f}")
    print()

    return df

# ──────────────────────────────────────────────────────────
# STEP 6: Aggregate to SOV line level
# ──────────────────────────────────────────────────────────
def aggregate_by_sov_line(df: pd.DataFrame) -> pd.DataFrame:
    """
    combine labor logs to SOV line level (target: 6075 rows)
   Get the following aggregated features for each SOV line:

      - total_labor_cost 
      - total_hours_st   : total standard labor hours
      - total_hours_ot   : overtime hours
      - total_hours      : total hours (including overtime before conversion)
      - log_count        : log entry count (can be used to check data density)
      - unique_employees : number of employees involved in the SOV line
      - date_min / date_max : actual construction start and end dates for the SOV line
    
    Args:
        df: dataframe with cleaned labor logs, must include 'project_id', 'sov_line_id', 'labor_cost', 'hours_st', 'hours_ot', 'employee_id', 'date'
    
    Returns:
        combined dataframe at SOV line level with the above features
    """
    agg_df = df.groupby(['project_id', 'sov_line_id']).agg(
        total_labor_cost  = ('labor_cost',    'sum'),
        total_hours_st    = ('hours_st',      'sum'),
        total_hours_ot    = ('hours_ot',      'sum'),
        log_count         = ('log_id',        'count'),
        unique_employees  = ('employee_id',   'nunique'),
        date_min          = ('date',          'min'),
        date_max          = ('date',          'max'),
    ).reset_index()

    #calculate total_hours for later use (e.g. labor productivity analysis)
    agg_df['total_hours'] = agg_df['total_hours_st'] + agg_df['total_hours_ot']

    # examine the aggregation result
    expected_rows = 6075
    actual_rows = len(agg_df)
    if actual_rows != expected_rows:
        print(f"⚠️  Row count mismatch: expected {expected_rows}, got {actual_rows}")
        print("    Potential reason：Some SOV line is not recorded in labor_logs")
    else:
        print(f"✅ Aggregation looks correct: {actual_rows} rows ({actual_rows // 15} projects × 15 SOV lines)")

    print(agg_df.describe())
    print()
    return agg_df

# ──────────────────────────────────────────────────────────
# STEP 7: Save the cleaned and aggregated data for LLM analysis
# ──────────────────────────────────────────────────────────

def save_clean_data(df: pd.DataFrame, out_path: str) -> None:
    if os.path.isdir(out_path):
        out_path = os.path.join(out_path, "cleaned_labor_log.csv")
    
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    df.to_csv(out_path, index=False)
    print(f"✅ Saved → {out_path}")
    print(f"   Final shape: {df.shape}")

# ──────────────────────────────────────────────────────────
# Main Cleaning Process
# ──────────────────────────────────────────────────────────
df = check_null_and_duplicates(df_labor_logs)
df = standardize_dates(df)
df = standardize_roles(df)
df = validate_numerics(df)
df = df.dropna(subset=['hours_st', 'hours_ot', 'hourly_rate', 'burden_multiplier'])
df = compute_labor_cost(df)

df_sov_labor = aggregate_by_sov_line(df)

save_clean_data(df_sov_labor, '/Users/xin/The-HVAC-Margin-Rescue-Challenge/data/Cleaned data/cleaned_labor_log.csv')
print("Columns:", df_sov_labor.columns.tolist())
print(df_sov_labor.head(20))
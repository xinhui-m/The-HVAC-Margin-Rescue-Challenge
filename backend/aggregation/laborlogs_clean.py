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
    将单个 role 字符串映射到标准名称。
    README 明确指出 role 字段存在大量不一致写法，例如：
      'JM Pipefitter' / 'Journeyman P.F.' / 'Pipefitter JM' → 'Journeyman Pipefitter'
    
    匹配逻辑：
      1. 全小写 + 去除多余标点/空格
      2. 用正则关键词依次匹配，优先匹配更具体的（如 General Foreman 先于 Foreman）
      3. 无法匹配的保留原始值，留作后续排查
    
    Args:
        role: 原始 role 字符串
    
    Returns:
        标准化后的 role 字符串
    """
    if pd.isnull(role):
        return 'Unknown'

    s = str(role).lower().strip()
    s = re.sub(r'[.\-_/]', ' ', s)   # 统一标点为空格
    s = re.sub(r'\s+', ' ', s)        # 合并多余空格

    # 注意顺序：更具体的规则放前面
    if re.search(r'general\s*foreman', s):
        return 'General Foreman'
    if re.search(r'foreman', s):
        return 'Foreman'
    if re.search(r'super(intendent)?', s):
        return 'Superintendent'

    # Pipefitter：区分学徒 / 工匠 / 泛指
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

    # 通用 Apprentice：尝试提取年份（e.g. "2nd year"）
    if re.search(r'apprent', s):
        yr = re.search(r'(\d)(st|nd|rd|th)', s)
        if yr:
            return f"Apprentice {yr.group(1)}{'st' if yr.group(1)=='1' else 'nd' if yr.group(1)=='2' else 'rd' if yr.group(1)=='3' else 'th'} Year"
        return 'Apprentice'

    return role.strip()  # 匹配失败 → 保留原值，留作排查


def standardize_roles(df: pd.DataFrame, role_col: str = 'role') -> pd.DataFrame:
    """
    对 role 列批量应用标准化，并打印清洗前后对比。
    - 清洗后新增 'role_clean' 列，保留原始 role 列供审计
    - 打印未被规则覆盖的 role，方便补充匹配逻辑
    
    Args:
        df:       输入 DataFrame
        role_col: role 列名，默认 'role'
    
    Returns:
        新增 'role_clean' 列的 DataFrame
    """
    print(f"=== UNIQUE ROLES before clean: {df[role_col].nunique()} ===")

    df['role_clean'] = df[role_col].apply(_normalize_role)

    print(f"=== UNIQUE ROLES after clean:  {df['role_clean'].nunique()} ===")
    print(df['role_clean'].value_counts())

    # 打印仍未被规则匹配的 role（原值 == 清洗后值），方便补规则
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
    检验数值列的合理性，打印异常统计，不自动修改数据。
    检查项目：
      - hours_st / hours_ot：不应为负；单日总时长不应超过 24 小时
      - hourly_rate：正常范围 $15–$300（超出范围打印样本）
      - burden_multiplier：正常范围 1.0–2.5（超出范围打印样本）
    
    Args:
        df: 输入 DataFrame
    
    Returns:
        原始 DataFrame（本函数只报告，不修改）
    """
    num_cols = ['hours_st', 'hours_ot', 'hourly_rate', 'burden_multiplier']
    print("=== NUMERIC STATS ===")
    print(df[num_cols].describe())
    print()

    # 负值检查
    for col in num_cols:
        neg = (df[col] < 0).sum()
        if neg > 0:
            print(f"  ⚠️  {col}: {neg} negative values")

    # 单日总工时超过 24 小时（明显录入错误）
    odd_hours = df[(df['hours_st'] + df['hours_ot']) > 24]
    print(f"  ⚠️  Rows with total hours > 24/day: {len(odd_hours)}")
    if not odd_hours.empty:
        print(odd_hours[['log_id', 'date', 'hours_st', 'hours_ot']].head())

    # hourly_rate 异常（$15 以下或 $300 以上）
    odd_rate = df[(df['hourly_rate'] < 15) | (df['hourly_rate'] > 300)]
    print(f"  ⚠️  Unusual hourly_rate (<$15 or >$300): {len(odd_rate)}")
    if not odd_rate.empty:
        print(odd_rate[['log_id', 'role', 'hourly_rate']].head())

    # burden_multiplier 异常（正常约 1.25–1.65，放宽到 1.0–2.5）
    odd_burden = df[(df['burden_multiplier'] < 1.0) | (df['burden_multiplier'] > 2.5)]
    print(f"  ⚠️  Unusual burden_multiplier (<1.0 or >2.5): {len(odd_burden)}")
    if not odd_burden.empty:
        print(odd_burden[['log_id', 'burden_multiplier']].head())
    print()

    return df


# ──────────────────────────────────────────────────────────
# STEP 5: 计算 labor_cost 派生列
# ──────────────────────────────────────────────────────────
def compute_labor_cost(df: pd.DataFrame) -> pd.DataFrame:
    """
    按 README 公式计算每条记录的实际劳工成本，新增 'labor_cost' 列。
    
    公式：
        labor_cost = (hours_st + hours_ot × 1.5) × hourly_rate × burden_multiplier
    
    其中：
        hours_ot × 1.5  → 加班费溢价
        burden_multiplier → 劳工附加成本倍率（税、保险、福利等）
    
    Args:
        df: 包含 hours_st, hours_ot, hourly_rate, burden_multiplier 的 DataFrame
    
    Returns:
        新增 'labor_cost' 列的 DataFrame
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
# STEP 6: 按 sov_line_id 聚合 labor_cost
# ──────────────────────────────────────────────────────────
def aggregate_by_sov_line(df: pd.DataFrame) -> pd.DataFrame:
    """
    将明细级别的 labor_logs（1.2M 行）按 sov_line_id 聚合，
    生成 SOV 行级别的劳工成本汇总表（目标：6075 行）。
    
    聚合内容：
      - total_labor_cost : 该 SOV line 的总劳工成本
      - total_hours_st   : 正常工时合计
      - total_hours_ot   : 加班工时合计
      - total_hours      : 总工时（含加班折算前）
      - log_count        : 日志条目数（可用于检查数据密度）
      - unique_employees : 参与该 SOV line 的员工数
      - date_min / date_max : 该 SOV line 的实际施工起止日期
    
    Args:
        df: 已含 labor_cost 列的 DataFrame
    
    Returns:
        以 sov_line_id 为主键的聚合 DataFrame（6075 行）
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

    # 派生：总工时（未折算加班）
    agg_df['total_hours'] = agg_df['total_hours_st'] + agg_df['total_hours_ot']

    # examine the aggregation result
    expected_rows = 6075
    actual_rows = len(agg_df)
    if actual_rows != expected_rows:
        print(f"⚠️  Row count mismatch: expected {expected_rows}, got {actual_rows}")
        print("    可能原因：某些 SOV line 在 labor_logs 中没有记录，或 project 数量不足 405")
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
import pandas as pd
import numpy as np
from scipy import stats

def NUA(df):
    """
    Neuro-Urbanism Assessment (NUA) Index calculator
    Input: df = DataFrame with all raw participant data
    Output: NUA_Score = The NUA index score (%)
    """
    # --- Helper ---
    def ensure_series(x, df):
        """Convert float/int/np scalar to Series aligned with df index"""
        if isinstance(x, (int, float, np.float64)):
            return pd.Series([x] * len(df), index=df.index)
        return x

    # --- Force numeric ---
    numeric_cols = [
        "MM_Arousal","MM_Valence",
        "GA1","GA2","GA3","GA4","GA5","GA6","GA7",
        "PH1","PH2","PH3","PH4","PH5","PH6","PH7","PH8",
        "PS1","PS2","PS3","PS4","PS5","PS6","PS7","PS8","PS9","PS10",
        "Sleep Quality","Daily Time Outdoors",
        "BC1","BC2","BC3","BC4","BC5","BC6","BC7","BC8","WH9","WH15",
        "WH20","WH21","WH22","WH23","WH24","WH25","HL9_WD_HRS","HL9_WD_MIN",
        "HL9_WK_HRS","HL9_WK_MIN","HL10_WD_HRS","HL10_WD_MIN","HL10_WK_HRS","HL10_WK_MIN",
        "NP4","NP5","NP12","NP13","NP14","NP15","NP16","NP17","NP18","NP19","NP20",
        "NP21","NP22","NP23","NP24","NP25","NP26","NP27","NP28",
        "AlphaPeaks","HRV","CLM","Background Noise","Thermal Comfort","Air Quality"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # --- Well-being ---
    if df[["MM_Arousal", "MM_Valence"]].notna().any().any():
        MM_A = ((10 - df["MM_Arousal"]) / 9) * 100
        MM_V = ((6 - df["MM_Valence"]) / 5) * 100
        MM = (MM_A + MM_V) / 2
    else:
        MM = None

    gad_cols = ["GA1","GA2","GA3","GA4","GA5","GA6","GA7"]
    ph_cols = ["PH1","PH2","PH3","PH4","PH5","PH6","PH7","PH8"]

    if df[gad_cols].notna().any().any():
        GAD = ((4 - df[gad_cols]).sum(axis=1) / 21) * 100
    else:
        GAD = None

    if df[ph_cols].notna().any().any():
        PH = ((4 - df[ph_cols]).sum(axis=1) / 24) * 100
    else:
        PH = None

    if GAD is not None and PH is not None:
        Depression_Anxiety = (GAD + PH) / 2
    elif GAD is not None:
        Depression_Anxiety = GAD
    elif PH is not None:
        Depression_Anxiety = PH
    else:
        Depression_Anxiety = None

    ps_cols = ["PS1","PS2","PS3","PS4","PS5","PS6","PS7","PS8","PS9","PS10"]
    if df[ps_cols].notna().any().any():
        Stress = ((5 - df[["PS1","PS2","PS3","PS4","PS5","PS6"]]).sum(axis=1)
                  + df[["PS7","PS8","PS9","PS10"]].fillna(0).sum(axis=1)) / 40 * 100
    else:
        Stress = None

    wellbeing_parts = [MM, Depression_Anxiety, Stress]
    wellbeing_available = [ensure_series(p, df) for p in wellbeing_parts if p is not None]
    Wellbeing = pd.concat(wellbeing_available, axis=1).mean(axis=1) if wellbeing_available else None

    # --- Lifestyle ---
    if df["Sleep Quality"].notna().any():
        SQ = (df["Sleep Quality"] / 10) * 100
    else:
        SQ = None

    if df["HL9_WD_HRS"].notna().any() or df["HL10_WD_HRS"].notna().any():
        weekday_time = df["HL9_WD_HRS"].fillna(0) + df["HL10_WD_HRS"].fillna(0) \
                       + df["HL9_WD_MIN"].fillna(0) / 60 + df["HL10_WD_MIN"].fillna(0) / 60
        weekend_time = df["HL9_WK_HRS"].fillna(0) + df["HL10_WK_HRS"].fillna(0) \
                       + df["HL9_WK_MIN"].fillna(0) / 60 + df["HL10_WK_MIN"].fillna(0) / 60
        avg_daily_outdoor = ((weekday_time * 5) + (weekend_time * 2)) / 7
        outdoors = pd.cut(avg_daily_outdoor, bins=[-np.inf,0.5,1,np.inf], labels=[1,2,3]).astype(float)
        outdoors = (outdoors / 3) * 100
    else:
        outdoors = None

    lifestyle_parts = [SQ, outdoors]
    lifestyle_available = [ensure_series(p, df) for p in lifestyle_parts if p is not None]
    Lifestyle = pd.concat(lifestyle_available, axis=1).mean(axis=1) if lifestyle_available else None

    # --- Community Bonding ---
    bc_cols = ["BC1","BC2","BC3","BC4","BC5","BC6","BC7","BC8"]
    valid_bc_cols = [col for col in bc_cols if df[col].notna().any()]
    BC = (df[valid_bc_cols].fillna(0).sum(axis=1) / (5 * len(valid_bc_cols)) * 100) if valid_bc_cols else None

    sr_cols = ["WH20","WH21","WH22"]
    valid_sr_cols = [col for col in sr_cols if df[col].notna().any()]
    SR = (df[valid_sr_cols].fillna(0).sum(axis=1) / (5 * len(valid_sr_cols)) * 100) if valid_sr_cols else None

    sop_cols = ["NP4","NP5"]
    valid_sop_cols = [col for col in sop_cols if df[col].notna().any()]
    SOP = (df[valid_sop_cols].fillna(0).sum(axis=1) / (5 * len(valid_sop_cols)) * 100) if valid_sop_cols else None

    cb_parts = [BC, SR, SOP]
    cb_available = [ensure_series(p, df) for p in cb_parts if p is not None]
    CB = pd.concat(cb_available, axis=1).mean(axis=1) if cb_available else None

    # --- Neurophysiology using scipy.stats.linregress ---
    def age_correct_metric(metric_col):
        mask = df[metric_col].notna() & df['Age'].notna()
        if not mask.any():
            return None
        slope, intercept, _, _, _ = stats.linregress(df.loc[mask, 'Age'], df.loc[mask, metric_col])
        expected = df['Age'] * slope + intercept
        corrected = df[metric_col] - expected
        return corrected

    Neuro_metrics = []

    if "AlphaPeaks" in df.columns and "Age" in df.columns:
        alphapeaks = age_correct_metric("AlphaPeaks")
        if alphapeaks is not None:
            skew_alpha = stats.skew(alphapeaks.dropna())
            alpha_score = np.clip((1 - skew_alpha) * 100, 0, 100)
            Neuro_metrics.append(pd.Series([alpha_score]*len(df), index=df.index))

    if "HRV" in df.columns and "Age" in df.columns:
        hrv = age_correct_metric("HRV")
        if hrv is not None:
            skew_hrv = stats.skew(hrv.dropna())
            hrv_score = np.clip((1 - skew_hrv) * 100, 0, 100)
            Neuro_metrics.append(pd.Series([hrv_score]*len(df), index=df.index))

    Neurophysiology = pd.concat(Neuro_metrics, axis=1).mean(axis=1) if Neuro_metrics else None

    # --- Environmental Quality ---
    if df["CLM"].notna().any():
        CLM = (df["CLM"] / 6) * 100
    else:
        CLM = None

    # --- Background Noise ---
    if df["Background Noise"].notna().any():
      noise = np.interp(
        df["Background Noise"],
        [0, 40, 50, 55, 65, 75, 100],  # dB LAeq levels
        [100, 100, 80, 60, 40, 20, 0]  # comfort percentages
      )
      noise = pd.Series(noise, index=df.index)
    else:
      noise = None


    # --- Thermal Comfort (continuous function) ---
    if df["Thermal Comfort"].notna().any():
    # DI → comfort % mapping
      thermal = np.interp(
        df["Thermal Comfort"],
        [0, 21, 24, 27, 29, 50],   # DI values (extended a bit for safety)
        [100, 100, 75, 50, 25, 0]  # comfort percentages
    )
      thermal = pd.Series(thermal, index=df.index)
    else:
      thermal = None

    # --- Air Quality (continuous function) ---
    if df["Air Quality"].notna().any():
      air_quality = np.interp(
        df["Air Quality"],
        [0, 12, 35.4, 55.4, 150.4, 250.4, 500],  # PM2.5 µg/m³ levels
        [100, 100, 75, 50, 25, 10, 0]            # comfort percentages
      )
      air_quality = pd.Series(air_quality, index=df.index)
    else:
      air_quality = None

    if df["WH24"].notna().any():
        healthcare_access = (df["WH24"]/5)*100
    else:
        healthcare_access = None

    np_cols =["NP12","NP13","NP14","NP15","NP16","NP17","NP18","NP19","NP20","NP21",
              "NP22","NP23","NP24","NP25","NP26","NP27","NP28"]
    valid_np_cols = [col for col in np_cols if df[col].notna().any()]
    if valid_np_cols:
        max_val = 5
        reversed_np = (max_val + 1) - df[valid_np_cols]
        total_score = reversed_np.fillna(0).sum(axis=1)
        max_score = max_val * len(valid_np_cols)
        bluegreen_access = (total_score / max_score) * 100
    else:
        bluegreen_access = None

    if healthcare_access is not None and bluegreen_access is not None:
        Accessibility = (healthcare_access + bluegreen_access) / 2
    elif healthcare_access is not None:
        Accessibility = healthcare_access
    elif bluegreen_access is not None:
        Accessibility = bluegreen_access
    else:
        Accessibility = None

    mobility_cols = ["WH15","WH25"]
    valid_cols = [col for col in mobility_cols if df[col].notna().any()]
    if valid_cols:
        mobility = ((df[valid_cols].fillna(0).sum(axis=1)) / (len(valid_cols)*5)) * 100
    else:
        mobility = None

    QoLE_cols = ["WH9","WH23"]
    valid_cols = [col for col in QoLE_cols if df[col].notna().any()]
    if valid_cols:
        QoLE = ((df[valid_cols].fillna(0).sum(axis=1)) / (len(valid_cols)*5)) * 100
    else:
        QoLE = None
        
    env_parts = [CLM, noise,thermal,air_quality,QoLE,mobility,Accessibility]  # add other metrics if desired
    env_available = [ensure_series(p, df) for p in env_parts if p is not None]
    Environmental_Quality = pd.concat(env_available, axis=1).mean(axis=1) if env_available else None

    # --- Final NUA Score ---
    sections = [Wellbeing, Lifestyle, CB, Environmental_Quality, Neurophysiology]
    available_sections = [s for s in sections if s is not None]

    if available_sections:
        df_sections = pd.concat(available_sections, axis=1)
        NUA_per_participant = df_sections.mean(axis=1)
        NUA_Score_mean = NUA_per_participant.mean()
        NUA_Score_STD = NUA_per_participant.std()
        NUA_Score = [NUA_Score_mean, NUA_Score_STD]
    else:
        NUA_Score = pd.Series([np.nan] * len(df))

    return NUA_Score



import streamlit as st
import pandas as pd
from nua_module import NUA  # assuming you put your NUA function in nua_module.py

st.title("Neuro-Urbanism Assessment (NUA) Index Calculator")

# --- Provide a direct download button for the template ---
template_path = Path("NUA_template.xlsx")  # make sure this file is in your project folder

if template_path.exists():
    with open(template_path, "rb") as f:
        st.download_button(
            label="Download Excel Template",
            data=f,
            file_name="NUA_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.warning("NUA template file not found in the app folder.")

uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "xls"])

required_columns_df = [
    "MM_Arousal", "MM_Valence",
    "GA1","GA2","GA3","GA4","GA5","GA6","GA7",
    "PH1","PH2","PH3","PH4","PH5","PH6","PH7","PH8",
    "PS1","PS2","PS3","PS4","PS5","PS6","PS7","PS8","PS9","PS10",
    "Sleep Quality", "HL9_WD_HRS","HL9_WD_MIN","HL10_WD_HRS","HL10_WD_MIN",
    "HL9_WK_HRS","HL9_WK_MIN","HL10_WK_HRS","HL10_WK_MIN",
    "BC1","BC2","BC3","BC4","BC5","BC6","BC7","BC8",
    "WH9","WH15","WH20","WH21","WH22","WH23","WH24","WH25",
    "NP4","NP5","NP12","NP13","NP14","NP15","NP16","NP17","NP18","NP19","NP20",
    "NP21","NP22","NP23","NP24","NP25","NP26","NP27","NP28",
    "CLM","Background Noise","Thermal Comfort","Air Quality"]

required_columns_neuro = ["Participant","EEG","HRV","Site","Condition"]

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file,sheet_name="Indices",header=2)
    neuro = pd.read_excel(uploaded_file,sheet_name="Neurophysiology",header=2)
    st.write("### Preview of the data")
    st.dataframe(df.head())
    st.dataframe(neuro.head())
    
    # Check for missing columns
    missing_cols = [col for col in required_columns_df if col not in df.columns]
    if missing_cols:
        st.warning(
            "The following variables are missing from your data. "
            "The NUA calculation may not be complete fully representative or may fail:\n\n" +
            ", ".join(missing_cols)
        )
        
    missing_cols = [col for col in required_columns_neuro if col not in neuro.columns]
    if missing_cols:
        st.warning(
            "The following variables are missing from your neurophysiological data. "
            "The NUA calculation may not be complete fully representative or may fail:\n\n" +
            ", ".join(missing_cols)
        )

    st.write("### Calculating NUA Index...")
    try:
        nua_score = NUA(df,neuro)

        # Check if the result is empty or all NaN
        if (nua_score is None) or (isinstance(nua_score, pd.Series) and nua_score.isna().all()):
            st.error("NUA calculation could not be completed. The output is empty or all NaN.")
        else:
            st.write("NUA Index [Mean ± SD] calculated (0-100%):")
            st.write(nua_score)

    except Exception as e:
        st.error(f"Error during NUA calculation: {e}")








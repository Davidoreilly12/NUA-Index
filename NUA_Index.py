import streamlit as st
import pandas as pd
import io
from nua_module import NUA  # assuming you put your NUA function in nua_module.py

st.title("Neuro-Urbanism Assessment (NUA) Index Calculator")

# --- Input Options ---
option = st.radio(
    "Choose how to provide your data:",
    ["Upload Excel File", "Download Template + Upload", "Paste Data"]
)

# --- Required Columns ---
required_columns = [
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
    "AlphaPeaks","HRV","CLM","Background Noise","Thermal Comfort","Air Quality","Age"
]

df = None

# --- Option 1: Upload Excel ---
if option == "Upload Excel File":
    uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "xls"])
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file, sheet_name="Indices", header=2)

# --- Option 2: Download Template + Upload ---
elif option == "Download Template + Upload":
    st.markdown(
        """
        [📥 Download NUA Excel Template](https://github.com/your-username/your-repo/raw/main/path/to/NUA_template.xlsx)
        """,
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader("Upload your filled Excel file", type=["xlsx", "xls"])
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file, sheet_name="Indices", header=2)

# --- Option 3: Paste Data ---
elif option == "Paste Data":
    text_input = st.text_area(
        "Paste your data here (CSV format, with headers in the first row):",
        height=200,
        placeholder="Example:\nMM_Arousal,MM_Valence,GA1,GA2,...\n3.5,4.1,2,5,..."
    )
    if text_input:
        try:
            df = pd.read_csv(io.StringIO(text_input))
        except Exception as e:
            st.error(f"Could not read pasted data: {e}")

# --- Process if DataFrame exists ---
if df is not None:
    st.write("### Preview of the data")
    st.dataframe(df.head())

    # Check for missing columns
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        st.warning(
            "The following variables are missing from your data. "
            "The NUA calculation may not be complete or may fail:\n\n" +
            ", ".join(missing_cols)
        )

    st.write("### Calculating NUA Index...")
    try:
        nua_score = NUA(df)

        # Check if the result is empty or all NaN
        if (nua_score is None) or (isinstance(nua_score, pd.Series) and nua_score.isna().all()):
            st.error("NUA calculation could not be completed. The output is empty or all NaN.")
        else:
            st.write("NUA Index [Mean ± SD] calculated (0-100%):")
            st.write(nua_score)

    except Exception as e:
        st.error(f"Error during NUA calculation: {e}")


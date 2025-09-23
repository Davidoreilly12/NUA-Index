import streamlit as st
import pandas as pd
import io
from nua_module import NUA  # Your NUA function should be in nua_module.py

st.title("Neuro-Urbanism Assessment (NUA) Index Calculator")

option = st.radio("Select an action:", ["Download Template + Upload", "Calculate NUA"])

if option == "Download Template + Upload":
    st.markdown(
        """
        [📥 Download NUA Excel Template](https://github.com/Davidoreilly12/NUA-Index/raw/main/NUA_template.xlsx)
        """,
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader("Upload your filled Excel file", type=["xlsx", "xls"])

    if uploaded_file is not None:
        try:
            # Read Excel file (adjust sheet_name/header as per your template)
            df = pd.read_excel(uploaded_file, sheet_name="Indices", header=2)
            
            # Calculate NUA score
            nua_score = NUA(df)

            st.write("### NUA Index [Mean ± SD] (0-100%)")
            st.write(nua_score)


        except Exception as e:
            st.error(f"Error during NUA calculation: {e}")











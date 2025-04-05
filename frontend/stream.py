import streamlit as st
import requests

st.set_page_config(page_title="SHL Assessment Recommender", layout="wide")
st.title("🔍 AI-Powered SHL Assessment Recommender")

job_description = st.text_area("Enter job description or keywords")

if st.button("Get Recommendations"):
    with st.spinner("Analyzing and recommending..."):
        res = requests.post("https://genai-shl.onrender.com/recommend", json={"job_description": job_description})

        if res.status_code == 200:
            data = res.json()["recommendations"]

            if data:
                st.subheader("Top Assessment Matches")
                for item in data:
                    st.markdown(f"""
                    **[{item['Assessment Name']}]({item['Assessment URL']})**  
                    - 🕒 Duration: `{item['Duration']}`  
                    - 🧪 Test Type: `{item['Test Type']}`  
                    - 🧭 Remote Testing: `{item['Remote Testing']}`  
                    - 🎯 Adaptive/IRT: `{item['Adaptive/IRT']}`
                    """)
                    st.markdown("---")
            else:
                st.warning("No relevant assessments found.")
        else:
            st.error("Failed to fetch recommendations.")


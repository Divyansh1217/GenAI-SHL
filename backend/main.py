import streamlit as st
import requests
import json

st.set_page_config(page_title="SHL Assessment Recommender", layout="wide")
st.title("🔍 AI-Powered SHL Assessment Recommender")

job_description = st.text_area("Enter job description or keywords")

st.markdown("#### (Optional) Upload Evaluation File (JSON)")
uploaded_file = st.file_uploader("Upload a JSON file with ground_truth and predictions", type="json")

evaluation_data = None
if uploaded_file is not None:
    try:
        evaluation_data = json.load(uploaded_file)
        st.success("Evaluation data uploaded successfully!")
    except Exception as e:
        st.error(f"Error loading JSON: {e}")

if st.button("Get Recommendations"):
    with st.spinner("Analyzing and recommending..."):
        payload = {"job_description": job_description}
        if evaluation_data:
            payload["data"] = evaluation_data

        res = requests.post("https://shl-backend-982360791068.us-central1.run.app", json=payload)

        if res.status_code == 200:
            res_json = res.json()
            data = res_json["recommendations"]
            meanrecall = res_json["Mean Recall@3"]
            meanap = res_json["Mean Average Precision@3"]

            st.success("Recommendations fetched successfully!")

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

            if meanrecall is not None and meanap is not None:
                st.subheader("Accuracy Metrics")
                st.write(f"**Mean Recall@3:** {meanrecall:.2f}")
                st.write(f"**Mean Average Precision@3:** {meanap:.2f}")
        else:
            st.error("Failed to fetch recommendations.")

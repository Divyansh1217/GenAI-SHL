# main.py
from typing import Dict, List,Optional
import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util
import torch

app = FastAPI()

class EvaluationRequest(BaseModel):
    ground_truth: Dict[str, List[str]]
    predictions: Dict[str, List[str]]
# Evaluation functions
def mean_recall_at_3(gt, recs):
    recall_scores = []
    for job, relevant_tests in gt.items():
        top3_recs = recs.get(job, [])[:3]
        num_relevant_in_top3 = len(set(top3_recs) & set(relevant_tests))
        recall_scores.append(num_relevant_in_top3 / len(relevant_tests))
    return np.mean(recall_scores)

def map_at_3(gt, recs):
    ap_scores = []
    for job, relevant_tests in gt.items():
        top3_recs = recs.get(job, [])[:3]
        relevant_count = 0
        avg_precision = 0
        for i, rec in enumerate(top3_recs):
            if rec in relevant_tests:
                relevant_count += 1
                precision_at_k = relevant_count / (i + 1)
                avg_precision += precision_at_k
        if len(relevant_tests) > 0:
            ap_scores.append(avg_precision / min(3, len(relevant_tests)))
    return np.mean(ap_scores)


# Load CSV and model
df = pd.read_csv("shl_req.csv")
df["clean_description"] = df["Description"].fillna("").str.replace("\n", " ")
model = SentenceTransformer("all-MiniLM-L6-v2")  # lightweight and fast

# Embed descriptions once
corpus_embeddings = model.encode(df["clean_description"].tolist(), convert_to_tensor=True)

# Request model
class Query(BaseModel):
    job_description: str
    data:Optional[EvaluationRequest]=None

@app.post("/")
def recommend(query: Query):
    query_embedding = model.encode(query.job_description, convert_to_tensor=True)
    mean_recall = map_at_3_score = None
    if query.data:
        mean_recall = mean_recall_at_3(query.data.ground_truth, query.data.predictions)
        map_at_3_score = map_at_3(query.data.ground_truth, query.data.predictions)
    # Compute cosine similarity
    cos_scores = util.pytorch_cos_sim(query_embedding, corpus_embeddings)[0]
    top_results = torch.topk(cos_scores, k=20)  # take more in case of duplicates

    seen_names = set()
    recommendations = []

    for idx in top_results[1]:
        row = df.iloc[idx.item()]
        name = row["Assessment Name"]

        # Skip duplicates
        if name in seen_names:
            continue

        seen_names.add(name)

        recommendations.append({
            "Assessment Name": name,
            "Assessment URL": row["Assessment URL"],
            "Remote Testing": "Yes" if row["Remote Testing"] == "✔" else "No",
            "Adaptive/IRT": "Yes" if row["Adaptive/IRT"] == "✔" else "No",
            "Duration": row["Duration"],
            "Test Type": row["Test Types"]
        })

        if len(recommendations) == 10:
            break

    return {"recommendations": recommendations,
            "Mean Recall@3": mean_recall,
            "Mean Average Precision@3": map_at_3_score,}
if __name__=="__main__":
    import os
    import uvicorn
    port=int(os.environ.get("PORT", 8080))
    uvicorn.run(app,host="0.0.0.0"  ,port=port,workers=1)

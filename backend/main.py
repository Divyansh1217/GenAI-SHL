# main.py
import pandas as pd
from fastapi import FastAPI, Request
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util
import torch

app = FastAPI()

# Load CSV and model
df = pd.read_csv("shl_req.csv")
df["clean_description"] = df["Description"].fillna("").str.replace("\n", " ")
model = SentenceTransformer("all-MiniLM-L6-v2")  # lightweight and fast

# Embed descriptions once
corpus_embeddings = model.encode(df["clean_description"].tolist(), convert_to_tensor=True)

# Request model
class Query(BaseModel):
    job_description: str

@app.post("/recommend")
def recommend(query: Query):
    # Embed the query
    query_embedding = model.encode(query.job_description, convert_to_tensor=True)

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

    return {"recommendations": recommendations}

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0"  ,port=8000,workers=1)
Approach:
1. Collected the useful information by NLP webscraping by Beautifulsoup and request
2. Collected useful information such as Assessment name,url,description,time etc
3. then write the backend using sentence_transformer and pytorch.
4. Find the similarities using sin_cos_similarity to get the answers
5. We get top 20 similar roles and remove the duplicates for it
6. Frontend by Streamlit
7. Deploy both frontend and backend on the Cloud .
8. RAG can be implemented for Fast answering techniques as sentence_transformer takes time but to save space i have used this.

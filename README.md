# AI-Powered E-commerce Recommendation & Shopping Assistant

Capstone project combining Python, SQL, Big Data, ML, DL, GenAI, and Agentic AI —
deployed end-to-end (Vercel + Railway/Render).

## Tech Stack

| Layer        | Technology |
|--------------|------------|
| Frontend     | Next.js / React → Vercel |
| Backend      | Python (FastAPI) |
| Database     | MySQL |
| Big Data     | Pandas / PySpark |
| ML           | scikit-learn (collaborative + content-based filtering) |
| DL           | sentence-transformers (semantic embeddings) |
| GenAI        | LLM API (RAG over product catalog) |
| Agentic AI   | Custom tool-calling agent |
| Deployment   | Vercel (frontend) + Railway/Render (backend) + Railway/Aiven (MySQL) |

## Project Structure

```
ecommerce-ai-capstone/
├── backend/
│   ├── app/
│   │   ├── routes/        # FastAPI route handlers
│   │   ├── models/        # SQLAlchemy models / Pydantic schemas
│   │   ├── agents/        # Agentic AI logic + tools
│   │   └── services/      # Recommendation, embedding, LLM services
│   ├── data/               # Raw & processed dataset (gitignored)
│   ├── ml/                 # Training scripts, saved models
│   ├── notebooks/          # Exploration / big-data analysis notebooks
│   └── requirements.txt
├── frontend/                # Next.js app (scaffolded on Day 10)
└── README.md
```

## 14-Day Build Plan

**Week 1 — Data & Intelligence Core**
- Day 1: Repo setup, dataset selection, environment setup
- Day 2: MySQL schema design + data load
- Day 3: Big Data cleaning & aggregation (Pandas)
- Day 4: FastAPI backend — product/category/search endpoints
- Day 5: ML recommender (collaborative + content-based filtering)
- Day 6: DL embeddings — semantic similarity search
- Day 7: Wire recommendation logic into API + test

**Week 2 — AI Assistant, Frontend, Deployment**
- Day 8: GenAI — RAG over product catalog
- Day 9: Agentic AI — agent + tools
- Day 10: Frontend — product listing/detail pages
- Day 11: Frontend — chat assistant widget
- Day 12: Frontend — analytics dashboard
- Day 13: Deploy (Vercel + Railway/Render + MySQL host)
- Day 14: Polish, README, demo recording

## Stretch Goals (if time allows)
- Budget-constrained "reverse shopping" agent
- Explainable recommendations ("recommended because...")
- Seller-side analytics dashboard
- Visual search (CLIP embeddings)

## Dataset
[Olist Brazilian E-commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — Kaggle

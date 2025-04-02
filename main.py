from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

model = SentenceTransformer('all-MiniLM-L6-v2')
INDEX_PATH = "faiss_index.index"
TEXTS_PATH = "template_texts.csv"

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload(request: Request, file: UploadFile = File(...)):
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file.file)
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file.file)
        else:
            return templates.TemplateResponse("index.html", {"request": request, "error": "対応形式はCSVまたはExcelのみです。"})

        if '内容' not in df.columns:
            return templates.TemplateResponse("index.html", {"request": request, "error": "'内容'列が見つかりません。"})

        texts = df['内容'].fillna("").tolist()
        embeddings = model.encode(texts)

        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(np.array(embeddings))

        faiss.write_index(index, INDEX_PATH)
        df.to_csv(TEXTS_PATH, index=False)

        return templates.TemplateResponse("index.html", {"request": request, "success": True})

    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "error": str(e)})

@app.post("/search")
async def search(request: Request, query: str = Form(...)):
    try:
        if not os.path.exists(INDEX_PATH) or not os.path.exists(TEXTS_PATH):
            return templates.TemplateResponse("index.html", {"request": request, "error": "モデルがまだ構築されていません。"})

        index = faiss.read_index(INDEX_PATH)
        df = pd.read_csv(TEXTS_PATH)
        texts = df['内容'].fillna("").tolist()

        query_embedding = model.encode([query])
        _, indices = index.search(np.array(query_embedding), k=3)

        results = [texts[i] for i in indices[0]]

        return templates.TemplateResponse("index.html", {"request": request, "results": results, "query": query})

    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "error": str(e)})

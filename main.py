from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
import os

from routers import auth, planilha
from core.auth import get_current_user
from schemas.planilha import PlanilhaData

app = FastAPI(
    title="COPASA - Matriz de Patrocínios",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(planilha.router)

@app.post("/gerar", include_in_schema=False)
async def gerar_alias(dados: PlanilhaData, current_user: dict = Depends(get_current_user)):
    return await planilha.gerar_planilha_endpoint(dados, current_user)

@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_path = os.path.join(os.path.dirname(__file__), "template", "index.html")
    return FileResponse(index_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
import httpx
from core.ai import extrair_dados_planilha, analisar_planilha_com_ollama
from core.auth import get_current_user
from core.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/ai", tags=["Inteligência Artificial"])

@router.get("/status")
async def check_ollama_status(current_user: dict = Depends(get_current_user)):
    """Verifica a conectividade com o servidor Ollama e lista os modelos disponíveis."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if res.status_code == 200:
                models_info = res.json().get("models", [])
                model_names = [m.get("name") for m in models_info]
                return {
                    "status": "online",
                    "ollama_url": settings.OLLAMA_BASE_URL,
                    "modelo_configurado": settings.OLLAMA_MODEL,
                    "modelos_disponiveis": model_names
                }
            else:
                return {
                    "status": "offline",
                    "erro": f"Servidor Ollama retornou HTTP {res.status_code}"
                }
    except Exception as e:
        return {
            "status": "offline",
            "erro": f"Não foi possível conectar ao Ollama em {settings.OLLAMA_BASE_URL}: {str(e)}"
        }

@router.post("/analisar-planilha")
async def analisar_planilha_endpoint(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Recebe um arquivo .xlsx preenchido e retorna uma análise da IA com sugestões de melhoria de pontuação."""
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas arquivos .xlsx são permitidos."
        )

    try:
        contents = await file.read()
        dados_planilha = extrair_dados_planilha(contents)
        resultado = await analisar_planilha_com_ollama(dados_planilha)
        
        if not resultado.get("sucesso"):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=resultado.get("erro", "Falha na comunicação com o servidor de IA.")
            )

        return resultado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar e analisar a planilha: {str(e)}"
        )

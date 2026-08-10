from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
import httpx
from core.ai import extrair_dados_planilha, analisar_planilha_com_groq
from core.auth import get_current_user
from core.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/ai", tags=["Inteligência Artificial"])

@router.get("/status")
async def check_groq_status(current_user: dict = Depends(get_current_user)):
    """Verifica se a GROQ_API_KEY está configurada e se a API do Groq está respondendo."""
    if not settings.GROQ_API_KEY:
        return {
            "status": "offline",
            "erro": "GROQ_API_KEY não foi informada."
        }

    try:
        headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get("https://api.groq.com/openai/v1/models", headers=headers)
            if res.status_code == 200:
                return {
                    "status": "online",
                    "provedor": "Groq Cloud LPU",
                    "modelo_configurado": settings.GROQ_MODEL
                }
            else:
                return {
                    "status": "offline",
                    "erro": f"Groq API retornou HTTP {res.status_code}"
                }
    except Exception as e:
        return {
            "status": "offline",
            "erro": f"Não foi possível conectar à Groq API: {str(e)}"
        }

@router.post("/analisar-planilha")
async def analisar_planilha_endpoint(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Recebe um arquivo .xlsx preenchido e retorna uma análise da IA Groq com sugestões de melhoria."""
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas arquivos .xlsx são permitidos."
        )

    try:
        contents = await file.read()
        dados_planilha = extrair_dados_planilha(contents)
        resultado = await analisar_planilha_com_groq(dados_planilha)
        
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

from fastapi import APIRouter, Depends, Response, HTTPException, status
from schemas.planilha import PlanilhaData
from core.planilha import gerar_planilha
from core.auth import get_current_user

router = APIRouter(prefix="/planilha", tags=["Planilha"])

@router.post("/gerar")
async def gerar_planilha_endpoint(
    dados: PlanilhaData,
    current_user: dict = Depends(get_current_user)
):
    try:
        conteudo_excel = gerar_planilha(dados.model_dump())
        return Response(
            content=conteudo_excel,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": 'attachment; filename="Matriz_Patrocinios_Preenchida.xlsx"'},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar planilha: {str(e)}"
        )

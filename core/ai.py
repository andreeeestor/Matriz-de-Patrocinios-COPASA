import io
import json
import httpx
from openpyxl import load_workbook
from .config import get_settings
from .planilha import CELL_MAP

settings = get_settings()

# Notas máximas estimadas por critério para identificação de gap
MAX_SCORES = {
    "valores_organizacionais_nota": 20,
    "diversidade_inclusao_nota": 20,
    "sustentabilidade_nota": 20,
    "portfolio_nota": 25,
    "experiencia_incentivos_nota": 25,
    "capacidade_tecnica_nota": 25,
    "governanca_nota": 25,
    "recursos_humanos_nota": 25,
    "recursos_financeiros_nota": 25,
    "experiencia_resultados_nota": 25,
    "parcerias_nota": 25,
    "beneficiarios_diretos_nota": 30,
    "beneficiarios_indiretos_nota": 30,
    "educacao_nota": 30,
    "saude_nota": 30,
    "inclusao_nota": 30,
    "esg_nota": 30,
    "diferencial_artistico_nota": 30,
    "diferencial_social_nota": 30,
    "diferencial_originalidade_nota": 30,
    "diferencial_tecnico_nota": 30,
    "diferencial_relacionamento_nota": 30,
    "interesse_coletivo_nota": 30,
    "plano_comunicacao_nota": 20,
    "redes_sociais_nota": 20,
    "monitoramento_nota": 20,
    "conteudo_institucional_nota": 20,
    "ativacoes_marca_nota": 20,
    "direitos_imagem_nota": 20,
    "contrapartida_imagem_nota": 20,
    "site_oficial_nota": 20,
    "exibicao_video_nota": 20,
    "citacao_releases_nota": 20,
    "voluntariado_corporativo_nota": 15,
    "datas_comemorativas_nota": 15,
    "engajamento_comunitario_nota": 15,
    "captacao_nota": 15,
    "execucao_garantida_nota": 15,
    "cotas_nota": 15,
}

def extrair_dados_planilha(file_bytes: bytes) -> dict:
    """Lê uma planilha .xlsx enviada e extrai os campos e notas atribuídas."""
    wb = load_workbook(io.BytesIO(file_bytes), data_only=True)
    ws = wb.active

    dados_extraidos = {}
    notas_criterios = {}
    pontuacao_total = 0.0
    pontuacao_maxima = sum(MAX_SCORES.values())

    for campo, (linha, coluna) in CELL_MAP.items():
        val = ws.cell(row=linha, column=coluna).value
        dados_extraidos[campo] = val

        if campo.endswith("_nota"):
            try:
                nota_num = float(val) if val is not None else 0.0
            except (ValueError, TypeError):
                nota_num = 0.0
            
            nota_max = MAX_SCORES.get(campo, 20)
            notas_criterios[campo] = {
                "nota_obtida": nota_num,
                "nota_maxima": nota_max,
                "gap": max(0.0, nota_max - nota_num),
                "observacao": ws.cell(row=linha, column=coluna + 1).value or ""
            }
            pontuacao_total += nota_num

    return {
        "nome_projeto": dados_extraidos.get("nome_projeto", "Não informado"),
        "proponente": dados_extraidos.get("proponente", "Não informado"),
        "valor_solicitado": dados_extraidos.get("valor_solicitado_aporte", "Não informado"),
        "pontuacao_total_obtida": pontuacao_total,
        "pontuacao_maxima_possivel": pontuacao_maxima,
        "detalhes_criterios": notas_criterios,
    }

async def analisar_planilha_com_ollama(dados_planilha: dict) -> dict:
    """Envia o diagnóstico de pontuação para o Ollama gerar recomendações inteligentes em JSON."""
    
    system_prompt = (
        "Você é um consultor especialista em avaliação de projetos e patrocínios da COPASA. "
        "Sua tarefa é analisar os dados de pontuação extraídos de uma planilha de avaliação e gerar um diagnóstico executivo "
        "com oportunidades de melhoria para aumentar a pontuação da proposta.\n\n"
        "RESPONDA EXCLUSIVAMENTE EM FORMATO JSON VÁLIDO no seguinte esquema:\n"
        "{\n"
        '  "resumo_executivo": "Visão geral da pontuação e desempenho do projeto",\n'
        '  "pontos_fortes": ["lista de aspectos em que o projeto pontuou alto"],\n'
        '  "oportunidades_melhoria": [\n'
        "    {\n"
        '      "criterio": "Nome do critério com nota baixa/gap",\n'
        '      "nota_atual": 10,\n'
        '      "nota_maxima": 20,\n'
        '      "recomendacao": "Ação prática orientando o que melhorar no projeto ou na documentação para atingir a nota máxima"\n'
        "    }\n"
        "  ],\n"
        '  "conclusao": "Parecer final consultivo"\n'
        "}"
    )

    user_prompt = f"Dados do Projeto Avaliado:\n{json.dumps(dados_planilha, ensure_ascii=False, indent=2)}"

    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": f"{system_prompt}\n\n{user_prompt}",
        "stream": False,
        "format": "json"
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json=payload
            )

            if res.status_code == 200:
                res_data = res.json()
                response_text = res_data.get("response", "{}")
                try:
                    analise_json = json.loads(response_text)
                except json.JSONDecodeError:
                    analise_json = {
                        "resumo_executivo": response_text,
                        "pontos_fortes": [],
                        "oportunidades_melhoria": [],
                        "conclusao": "Resposta gerada mas formato não-JSON padrão."
                    }
                
                return {
                    "sucesso": True,
                    "modelo_usado": settings.OLLAMA_MODEL,
                    "dados_extraidos": {
                        "nome_projeto": dados_planilha["nome_projeto"],
                        "proponente": dados_planilha["proponente"],
                        "pontuacao_total_obtida": dados_planilha["pontuacao_total_obtida"],
                        "pontuacao_maxima_possivel": dados_planilha["pontuacao_maxima_possivel"],
                    },
                    "analise_ia": analise_json
                }
            else:
                return {
                    "sucesso": False,
                    "erro": f"Ollama respondeu com status {res.status_code}: {res.text}"
                }
    except Exception as e:
        return {
            "sucesso": False,
            "erro": f"Erro de conexão com o servidor Ollama ({settings.OLLAMA_BASE_URL}): {str(e)}"
        }

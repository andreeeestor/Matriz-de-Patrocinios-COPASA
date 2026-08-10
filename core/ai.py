import io
import json
import httpx
from openpyxl import load_workbook
from .config import get_settings
from .planilha import CELL_MAP

settings = get_settings()

MAX_SCORES = {
    "valores_organizacionais_nota": 20,  # Valor aproximado (não tem na planilha)
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
    
    "beneficiarios_diretos_nota": 36,  # CORRIGIDO
    "beneficiarios_indiretos_nota": 36,  # CORRIGIDO
    "educacao_nota": 36,  # CORRIGIDO
    "saude_nota": 36,  # CORRIGIDO
    "inclusao_nota": 36,  # CORRIGIDO
    "esg_nota": 36,  # CORRIGIDO
    "diferencial_artistico_nota": 36,
    "diferencial_social_nota": 36,
    "diferencial_originalidade_nota": 36,
    "diferencial_tecnico_nota": 36,
    "diferencial_relacionamento_nota": 36,
    "interesse_coletivo_nota": 0,  # Nota fixa 0 na planilha
    
    "plano_comunicacao_nota": 33,  # CORRIGIDO
    "redes_sociais_nota": 33,  # CORRIGIDO
    "monitoramento_nota": 33,  # CORRIGIDO
    "conteudo_institucional_nota": 33,  # CORRIGIDO
    "ativacoes_marca_nota": 33,  # CORRIGIDO
    "direitos_imagem_nota": 33,  # CORRIGIDO
    "contrapartida_imagem_nota": 33,  # CORRIGIDO
    "site_oficial_nota": 33,  # CORRIGIDO
    "exibicao_video_nota": 33,  # CORRIGIDO
    "citacao_releases_nota": 33,  # CORRIGIDO
    
    "voluntariado_corporativo_nota": 25,  # CORRIGIDO
    "datas_comemorativas_nota": 25,  # CORRIGIDO
    "engajamento_comunitario_nota": 25,  # CORRIGIDO
    
    "captacao_nota": 25,  # CORRIGIDO
    "execucao_garantida_nota": 25,  # CORRIGIDO
    "cotas_nota": 25,  # CORRIGIDO
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

async def analisar_planilha_com_groq(dados_planilha: dict) -> dict:
    """Envia o diagnóstico de pontuação para a API do Groq gerar recomendações inteligentes em JSON."""
    
    if not settings.GROQ_API_KEY:
        return {
            "sucesso": False,
            "erro": "GROQ_API_KEY não foi configurada no ambiente (.env ou variáveis do servidor)."
        }

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

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload
            )

            if res.status_code == 200:
                res_data = res.json()
                choices = res_data.get("choices", [])
                response_text = choices[0]["message"]["content"] if choices else "{}"
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
                    "modelo_usado": settings.GROQ_MODEL,
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
                    "erro": f"API do Groq respondeu com status {res.status_code}: {res.text}"
                }
    except Exception as e:
        return {
            "sucesso": False,
            "erro": f"Erro de conexão com a API do Groq: {str(e)}"
        }

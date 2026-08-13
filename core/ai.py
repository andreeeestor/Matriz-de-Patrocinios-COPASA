import io
import json
import httpx
from openpyxl import load_workbook
from .config import get_settings
from .planilha import CELL_MAP

settings = get_settings()

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
    
    "beneficiarios_diretos_nota": 25,
    "beneficiarios_indiretos_nota": 24,
    "educacao_nota": 24,
    "saude_nota": 24,
    "inclusao_nota": 24,
    "esg_nota": 24,
    "diferencial_artistico_nota": 23,
    "diferencial_social_nota": 23,
    "diferencial_originalidade_nota": 23,
    "diferencial_tecnico_nota": 23,
    "diferencial_relacionamento_nota": 23,
    "interesse_coletivo_nota": 0,
    
    "plano_comunicacao_nota": 33,
    "redes_sociais_nota": 33,
    "monitoramento_nota": 33,
    "conteudo_institucional_nota": 33,
    "ativacoes_marca_nota": 33,
    "direitos_imagem_nota": 33,
    "contrapartida_imagem_nota": 33,
    "site_oficial_nota": 33,
    "exibicao_video_nota": 33,
    "citacao_releases_nota": 33,
    
    "voluntariado_corporativo_nota": 25,
    "datas_comemorativas_nota": 25,
    "engajamento_comunitario_nota": 25,
    
    "captacao_nota": 25,
    "execucao_garantida_nota": 25,
    "cotas_nota": 25,
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
            nota_num = 0.0
            if val is not None:
                if isinstance(val, (int, float)):
                    nota_num = float(val)
                elif isinstance(val, str) and val.strip() != "":
                    # Tentar converter direto ou extrair o primeiro número
                    val_clean = val.replace(",", ".").strip()
                    try:
                        nota_num = float(val_clean)
                    except ValueError:
                        import re
                        match = re.search(r"(\d+(?:\.\d+)?)", val_clean)
                        if match:
                            nota_num = float(match.group(1))
                        else:
                            # Se for uma descrição de texto sem número fixo, atribuir a nota máxima do critério para a análise da planilha
                            nota_num = float(MAX_SCORES.get(campo, 20))
            
            nota_max = MAX_SCORES.get(campo, 20)
            notas_criterios[campo] = {
                "nota_obtida": nota_num,
                "nota_maxima": nota_max,
                "gap": max(0.0, nota_max - nota_num),
                "observacao": ws.cell(row=linha, column=coluna + 1).value or (val if isinstance(val, str) else "")
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

async def avaliar_formulario_com_groq(dados_form: dict) -> dict:
    """Recebe os dados textuais do formulário preenchido e utiliza a IA Groq para avaliar e atribuir notas a cada critério."""
    if not settings.GROQ_API_KEY:
        return {
            "sucesso": False,
            "erro": "GROQ_API_KEY não foi configurada."
        }

    system_prompt = (
        "Você é um comitê avaliador especialista em projetos e patrocínios da COPASA. "
        "Sua função é analisar as descrições, justificativas e informações prestadas pelo proponente e ATRIBUIR UMA NOTA JUSTA "
        "para cada critério de avaliação, respeitando rigorosamente a NOTA MÁXIMA de cada critério especificada abaixo:\n\n"
        f"LIMITES MÁXIMOS DE NOTA POR CRITÉRIO (MAX_SCORES):\n{json.dumps(MAX_SCORES, ensure_ascii=False, indent=2)}\n\n"
        "Regras para atribuição de notas:\n"
        "1. Para cada critério (ex: 'valores_organizacionais_nota', 'portfolio_nota', etc.), avalie a qualidade da informação fornecida.\n"
        "2. Atribua uma nota numérica entre 0 e a nota máxima do critério.\n"
        "3. Forneça uma breve justificativa/observação (ex: 'valores_organizacionais_obs') explicando o motivo da nota dada.\n"
        "4. O critério 'interesse_coletivo_nota' deve sempre receber nota 0.\n\n"
        "RESPONDA EXCLUSIVAMENTE EM FORMATO JSON VÁLIDO no seguinte formato:\n"
        "{\n"
        '  "notas": {\n'
        '     "valores_organizacionais_nota": 18,\n'
        '     "valores_organizacionais_obs": "Justificativa...",\n'
        '     "diversidade_inclusao_nota": 15,\n'
        '     "diversidade_inclusao_obs": "Justificativa..."\n'
        '     ... (incluir TODOS os 39 critérios terminados em _nota e seus _obs respectivos)\n'
        '  },\n'
        '  "resumo_avaliador": "Resumo geral da avaliação do comitê de IA",\n'
        '  "pontos_fortes": ["Destaques do projeto"],\n'
        '  "oportunidades_melhoria": ["Pontos em que o proponente pode melhorar"]\n'
        "}"
    )

    user_prompt = f"Informações do Formulário de Projeto Submetido:\n{json.dumps(dados_form, ensure_ascii=False, indent=2)}"

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
        "temperature": 0.2
    }

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
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
                    eval_json = json.loads(response_text)
                except json.JSONDecodeError:
                    eval_json = {"notas": {}, "resumo_avaliador": "Erro ao parsear JSON"}
                
                # Garantir limites máximos e calcular soma
                notas_dict = eval_json.get("notas", {})
                pontuacao_total = 0.0
                notas_ajustadas = {}

                for crit, max_val in MAX_SCORES.items():
                    val_dado = notas_dict.get(crit, 0)
                    try:
                        val_num = float(val_dado)
                    except (ValueError, TypeError):
                        val_num = 0.0
                    val_num = max(0.0, min(val_num, float(max_val)))
                    notas_ajustadas[crit] = val_num
                    pontuacao_total += val_num
                    
                    obs_key = crit.replace("_nota", "_obs")
                    notas_ajustadas[obs_key] = notas_dict.get(obs_key, "")

                return {
                    "sucesso": True,
                    "modelo_usado": settings.GROQ_MODEL,
                    "pontuacao_total_obtida": round(pontuacao_total, 2),
                    "pontuacao_maxima_possivel": sum(MAX_SCORES.values()),
                    "notas_atribuidas": notas_ajustadas,
                    "resumo_avaliador": eval_json.get("resumo_avaliador", ""),
                    "pontos_fortes": eval_json.get("pontos_fortes", []),
                    "oportunidades_melhoria": eval_json.get("oportunidades_melhoria", [])
                }
            else:
                return {
                    "sucesso": False,
                    "erro": f"API do Groq respondeu com status {res.status_code}: {res.text}"
                }
    except Exception as e:
        return {
            "sucesso": False,
            "erro": f"Erro ao comunicar com a IA da Groq: {str(e)}"
        }

from pydantic import BaseModel
from typing import Optional, Any

class PlanilhaData(BaseModel):
    # Proponente & Endereço
    proponente: Optional[str] = None
    razao_social: Optional[str] = None
    cnpj: Optional[str] = None
    rua: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    email: Optional[str] = None
    redes_sociais: Optional[str] = None

    # Representante Legal
    rep_nome: Optional[str] = None
    rep_cargo: Optional[str] = None
    rep_documento: Optional[str] = None
    rep_telefone: Optional[str] = None
    rep_celular: Optional[str] = None
    rep_email: Optional[str] = None

    # Projeto
    lei_incentivo: Optional[str] = None
    nome_projeto: Optional[str] = None
    codigo_aprovacao: Optional[str] = None
    artigo_aprovacao: Optional[str] = None
    data_publicacao: Optional[str] = None
    data_prorrogacao: Optional[str] = None
    data_final_captacao: Optional[str] = None
    valor_total_aprovacao: Optional[str] = None
    valor_solicitado_aporte: Optional[str] = None
    local_realizacao: Optional[str] = None
    periodo_realizacao: Optional[str] = None
    objetivo: Optional[str] = None
    publico_alvo: Optional[str] = None
    detalhamento_atividades: Optional[str] = None
    cronograma: Optional[str] = None

    # Dados Bancários
    banco: Optional[str] = None
    agencia: Optional[str] = None
    conta_corrente: Optional[str] = None
    operacao: Optional[str] = None

    # Avaliação - Notas e Observações
    valores_organizacionais_nota: Optional[Any] = None
    valores_organizacionais_obs: Optional[str] = None
    diversidade_inclusao_nota: Optional[Any] = None
    diversidade_inclusao_obs: Optional[str] = None
    sustentabilidade_nota: Optional[Any] = None
    sustentabilidade_obs: Optional[str] = None
    portfolio_nota: Optional[Any] = None
    portfolio_obs: Optional[str] = None
    experiencia_incentivos_nota: Optional[Any] = None
    experiencia_incentivos_obs: Optional[str] = None
    capacidade_tecnica_nota: Optional[Any] = None
    capacidade_tecnica_obs: Optional[str] = None
    governanca_nota: Optional[Any] = None
    governanca_obs: Optional[str] = None
    recursos_humanos_nota: Optional[Any] = None
    recursos_humanos_obs: Optional[str] = None
    recursos_financeiros_nota: Optional[Any] = None
    recursos_financeiros_obs: Optional[str] = None
    experiencia_resultados_nota: Optional[Any] = None
    experiencia_resultados_obs: Optional[str] = None
    parcerias_nota: Optional[Any] = None
    parcerias_obs: Optional[str] = None
    beneficiarios_diretos_nota: Optional[Any] = None
    beneficiarios_diretos_obs: Optional[str] = None
    beneficiarios_indiretos_nota: Optional[Any] = None
    beneficiarios_indiretos_obs: Optional[str] = None
    educacao_nota: Optional[Any] = None
    educacao_obs: Optional[str] = None
    saude_nota: Optional[Any] = None
    saude_obs: Optional[str] = None
    inclusao_nota: Optional[Any] = None
    inclusao_obs: Optional[str] = None
    esg_nota: Optional[Any] = None
    esg_obs: Optional[str] = None
    diferencial_artistico_nota: Optional[Any] = None
    diferencial_artistico_obs: Optional[str] = None
    diferencial_social_nota: Optional[Any] = None
    diferencial_social_obs: Optional[str] = None
    diferencial_originalidade_nota: Optional[Any] = None
    diferencial_originalidade_obs: Optional[str] = None
    diferencial_tecnico_nota: Optional[Any] = None
    diferencial_tecnico_obs: Optional[str] = None
    diferencial_relacionamento_nota: Optional[Any] = None
    diferencial_relacionamento_obs: Optional[str] = None
    interesse_coletivo_nota: Optional[Any] = None
    interesse_coletivo_obs: Optional[str] = None
    plano_comunicacao_nota: Optional[Any] = None
    plano_comunicacao_obs: Optional[str] = None
    redes_sociais_nota: Optional[Any] = None
    redes_sociais_obs: Optional[str] = None
    monitoramento_nota: Optional[Any] = None
    monitoramento_obs: Optional[str] = None
    conteudo_institucional_nota: Optional[Any] = None
    conteudo_institucional_obs: Optional[str] = None
    ativacoes_marca_nota: Optional[Any] = None
    ativacoes_marca_obs: Optional[str] = None
    direitos_imagem_nota: Optional[Any] = None
    direitos_imagem_obs: Optional[str] = None
    contrapartida_imagem_nota: Optional[Any] = None
    contrapartida_imagem_obs: Optional[str] = None
    site_oficial_nota: Optional[Any] = None
    site_oficial_obs: Optional[str] = None
    exibicao_video_nota: Optional[Any] = None
    exibicao_video_obs: Optional[str] = None
    citacao_releases_nota: Optional[Any] = None
    citacao_releases_obs: Optional[str] = None
    voluntariado_corporativo_nota: Optional[Any] = None
    voluntariado_corporativo_obs: Optional[str] = None
    datas_comemorativas_nota: Optional[Any] = None
    datas_comemorativas_obs: Optional[str] = None
    engajamento_comunitario_nota: Optional[Any] = None
    engajamento_comunitario_obs: Optional[str] = None

    # Negocial
    inclusao_material: Optional[str] = None
    cessao_convites: Optional[str] = None
    estande: Optional[str] = None
    palestrantes: Optional[str] = None
    cortesias_escolas: Optional[str] = None
    citacao_evento: Optional[str] = None

    # Viabilidade
    captacao_nota: Optional[Any] = None
    captacao_obs: Optional[str] = None
    execucao_garantida_nota: Optional[Any] = None
    execucao_garantida_obs: Optional[str] = None
    cotas_nota: Optional[Any] = None
    cotas_obs: Optional[str] = None

    # Resumo do Avaliador (IA) para o painel executivo da planilha
    resumo_avaliador: Optional[str] = None

    class Config:
        extra = "allow"

# Matriz de Patrocínios COPASA

![Status](https://img.shields.io/badge/status-em_desenvolvimento-yellow)
![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)
![License](https://img.shields.io/badge/licença-Proprietária-red)

Sistema corporativo de avaliação e gestão de patrocínios da COPASA, desenvolvido para automatizar o processo de preenchimento de propostas, cálculo em tempo real de pontuação e geração padronizada da planilha oficial da Matriz Integrada de Avaliação de Patrocínios.

---

## 📋 Sumário

- [Sobre o Projeto](#sobre-o-projeto)
- [Arquitetura](#arquitetura)
- [Tecnologias](#tecnologias)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Configuração](#instalação-e-configuração)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Endpoints da API](#endpoints-da-api)
- [Fluxo de Autenticação](#fluxo-de-autenticação)
- [Front-end](#front-end)
- [Roadmap](#roadmap)
- [Contribuição](#contribuição)
- [Licença e Contato](#licença-e-contato)

---

## 🎯 Sobre o Projeto

A **Matriz de Patrocínios COPASA** é uma solução corporativa que digitaliza e otimiza o fluxo de avaliação de projetos culturais, sociais e esportivos submetidos à COPASA. O sistema substitui o preenchimento manual de planilhas locais, oferecendo:

* **Formulário Digital Integrado:** Interface amigável com validação dos campos obrigatórios em tempo real.
* **Cálculo Automatizado:** Determinação instantânea de pontuação e classificação final (de *Zero* a *Excelente* em escala de até 722 pontos).
* **Consistência de Dados:** Geração de relatórios em Excel padronizados exatamente conforme o modelo oficial da companhia.
* **Segurança:** Controle de acesso autenticado via tokens JWT.
* **Integração WCM:** Layout responsivo pronto para embutimento no portal WCM da COPASA.

---

## 🏗️ Arquitetura

O projeto adota uma arquitetura cliente-servidor desacoplada:

```mermaid
flowchart TB
    subgraph Frontend["Front-end"]
        FE["Portal WCM / HTML5 + JS"]
    end

    subgraph Backend["Back-end (FastAPI)"]
        API["API Engine"]
        AUTH["Serviço de Autenticação (JWT)"]
        XL["Gerador OpenPyXL"]
    end

    subgraph Storage["Modelos & Artefatos"]
        MODEL["modelo.xlsx"]
    end

    FE -->|POST /auth/token| AUTH
    FE -->|POST /planilha/gerar| API
    AUTH -->|Valida Credenciais| API
    API --> XL
    XL -->|Injeta dados| MODEL
```

---

## 🛠️ Tecnologias

### Back-end
| Tecnologia | Versão | Finalidade |
| :--- | :---: | :--- |
| **FastAPI** | `^0.141` | Framework web assíncrono de alta performance |
| **Uvicorn** | `^0.52` | Servidor de aplicação ASGI |
| **HTTPX** | `^0.28` | Cliente HTTP assíncrono para comunicação com a API do Ollama |
| **Python-JOSE** | `^3.5` | Implementação e validação de tokens JWT |
| **Passlib** | `^1.7` | Hashing seguro de senhas (PBKDF2-SHA256) |
| **OpenPyXL** | `^3.1` | Leitura, escrita e extração de dados de modelos Excel |
| **Pydantic-Settings** | `^2.14` | Gerenciamento e validação de variáveis de ambiente |

### Inteligência Artificial Local
| Tecnologia | Finalidade |
| :--- | :--- |
| **Ollama** | Servidor local/remoto de LLMs (ex: `llama3`, `qwen2.5`, `mistral`) para diagnóstico de propostas |

### Front-end
| Tecnologia | Finalidade |
| :--- | :--- |
| **HTML5 / CSS3** | Estrutura semântica, responsividade e menu de navegação estilo *Segmented Control* |
| **JavaScript (ES6+)** | Lógica de formulário, calculador dinâmico de pontuação e upload para análise via IA |

### Gerenciamento de Dependências
| Ferramenta | Finalidade |
| :--- | :--- |
| **UV** | Gerenciador de pacotes e ambientes virtuais Python de alta velocidade |

---

## 📦 Pré-requisitos

* **Python 3.12** ou superior
* **UV** (recomendado) ou `pip`
* **Ollama** instalado e executando (`ollama run llama3`)
* **Git**

### Instalando o UV (recomendado)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## ⚙️ Instalação e Configuração

### 1. Clonar o Repositório
```bash
git clone https://github.com/seu-usuario/matriz-patrocinio.git
cd matriz-patrocinio
```

### 2. Criar o Ambiente Virtual e Instalar Dependências
Com o **UV**:
```bash
uv sync
```

Ou com **pip**:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou
.venv\Scripts\activate     # Windows

pip install -r pyproject.toml
```

### 3. Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto com as configurações desejadas:

```env
SECRET_KEY=sua_chave_secreta_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

### 4. Executar o Servidor Ollama (para recursos de IA)
Certifique-se de que o Ollama está rodando localmente com o modelo desejado:
```bash
ollama run llama3
```

### 5. Planilha Modelo
Verifique se o arquivo `modelo.xlsx` (template oficial da matriz) está presente no diretório raiz da aplicação.

### 6. Executar o Servidor FastAPI
```bash
uv run python main.py
# ou com ambiente ativado:
python main.py
```

A API estará disponível em `http://localhost:8000`.

### 7. Credenciais de Acesso Padrão
Para testes locais, utilize as credenciais abaixo na tela de login:
* **Usuário:** `carmem`
* **Senha:** `querida`

### 8. Documentação Interativa
* **Swagger UI:** `http://localhost:8000/docs`
* **ReDoc:** `http://localhost:8000/redoc`

---

## 📁 Estrutura do Projeto

```text
matriz-patrocinio/
├── main.py                 # Ponto de entrada da aplicação FastAPI
├── core/                   # Módulos centrais da aplicação
│   ├── __init__.py
│   ├── ai.py               # Leitura de planilhas .xlsx e integração HTTP com Ollama LLM
│   ├── auth.py             # Lógica de segurança e autenticação JWT
│   ├── config.py           # Carregamento de variáveis de ambiente (Ollama, Secret Key)
│   └── planilha.py         # Processamento e geração da planilha Excel
├── routers/                # Controladores / Endpoints da API
│   ├── __init__.py
│   ├── ai.py               # Endpoints de status da IA e análise inteligente de planilhas
│   ├── auth.py             # Endpoints de login e perfil
│   └── planilha.py         # Endpoint para geração de relatórios
├── schemas/                # Modelos de validação Pydantic
│   ├── __init__.py
│   └── planilha.py         # Schemas do formulário de entrada
├── template/               # Arquivos estáticos de visualização
│   └── index.html          # Interface Single Page com navegação Segmented Control por Abas
├── db/                     # Camada reservada para persistência (Banco de Dados)
│   └── __init__.py
├── modelo.xlsx             # Template da planilha oficial da Matriz COPASA
├── pyproject.toml          # Definição do projeto e dependências
├── uv.lock                 # Trava de versões das dependências (UV)
├── .env                    # Variáveis de ambiente locais
└── .gitignore
```

---

## 🔗 Endpoints da API

### 🔐 Autenticação

#### `POST /auth/token`
Autentica o usuário e retorna o token de acesso JWT.

* **Headers:** `Content-Type: application/x-www-form-urlencoded`
* **Body:**
  ```form-data
  username=carmem
  password=querida
  ```
* **Resposta (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1Ni...",
    "token_type": "bearer"
  }
  ```

#### `GET /auth/me`
Retorna as informações do usuário autenticado.

* **Headers:** `Authorization: Bearer <seu_token_jwt>`

---

### 📊 Planilha

#### `POST /planilha/gerar`
Gera a planilha Excel preenchida a partir das respostas submetidas.

* **Headers:** 
  * `Authorization: Bearer <seu_token_jwt>`
  * `Content-Type: application/json`
* **Resposta (200 OK):**
  * Retorno do arquivo binário `.xlsx` (`Matriz_Patrocinios_Preenchida.xlsx`) para download.

---

### 🤖 Inteligência Artificial (Ollama)

#### `GET /ai/status`
Verifica se o servidor Ollama está ativo e lista os modelos disponíveis.

* **Headers:** `Authorization: Bearer <seu_token_jwt>`
* **Resposta (200 OK):**
  ```json
  {
    "status": "online",
    "ollama_url": "http://localhost:11434",
    "modelo_configurado": "llama3",
    "modelos_disponiveis": ["llama3:latest", "qwen2.5:latest"]
  }
  ```

#### `POST /ai/analisar-planilha`
Recebe o upload de um arquivo `.xlsx` preenchido e retorna um diagnóstico executivo gerado pela IA com recomendações de como aumentar a pontuação.

* **Headers:** `Authorization: Bearer <seu_token_jwt>`
* **Body:** `multipart/form-data` contendo `file: <arquivo.xlsx>`
* **Resposta (200 OK):**
  ```json
  {
    "sucesso": true,
    "modelo_usado": "llama3",
    "dados_extraidos": {
      "nome_projeto": "Festival Cultural",
      "proponente": "Associação Arte",
      "pontuacao_total_obtida": 450.0,
      "pontuacao_maxima_possivel": 940.0
    },
    "analise_ia": {
      "resumo_executivo": "O projeto apresenta boa aderência aos valores organizacionais...",
      "pontos_fortes": ["Alta capacidade técnica comprovada", "Bom plano de sustentabilidade"],
      "oportunidades_melhoria": [
        {
          "criterio": "voluntariado_corporativo_nota",
          "nota_atual": 5,
          "nota_maxima": 15,
          "recomendacao": "Detalhar ações de engajamento dos colaboradores da COPASA no evento."
        }
      ],
      "conclusao": "Proposta viável com alto potencial de otimização de nota."
    }
  }
  ```

---

## 🔄 Fluxo de Autenticação e Geração

```mermaid
sequenceDiagram
    autonumber
    actor FE as Front-end
    participant API as FastAPI Router
    participant AUTH as Auth Service (JWT)
    participant XL as Excel Engine

    FE->>API: POST /auth/token (credenciais)
    API->>AUTH: Autenticar usuário
    AUTH-->>API: Retornar token JWT
    API-->>FE: access_token

    FE->>API: POST /planilha/gerar (Header: Bearer token + Payload JSON)
    API->>AUTH: Validar token JWT
    AUTH-->>API: Token válido
    API->>XL: Processar modelo.xlsx com payload
    XL-->>API: Planilha populada
    API-->>FE: Stream download (Matriz_Patrocinios_Preenchida.xlsx)
```

---

## 🌐 Hospedagem no Render & Uptime

A API backend está hospedada no serviço **Render**:
* **URL de Produção:** `https://matriz-patrocinios-copasa.onrender.com`
* **Documentação Swagger (Produção):** `https://matriz-patrocinios-copasa.onrender.com/docs`

### Como Evitar o "Sleep" do Render (Free Tier)
O plano gratuito do Render desliga a instância após 15 minutos sem uso. Para manter o serviço 100% ativo:
1. Cadastre-se no [UptimeRobot](https://uptimerobot.com/).
2. Crie um monitor do tipo **HTTP(s)** apontando para `https://matriz-patrocinios-copasa.onrender.com/`.
3. Defina o intervalo de monitoramento para **5 minutos**.

---

## 🖥️ Front-end & Integração WCM HCL

O front-end é uma solução *Single Page* leve e responsiva construída em HTML5/CSS3/JS puro:

* **Dinâmico:** Campos renderizados automaticamente com base no esquema de perguntas.
* **Cálculo Local de Pontuação:** Atualização dinâmica da pontuação total e classificação (de *Zero* a *Excelente*).
* **Feedback ao usuário:** Barras de progresso e notificações *toast*.
* **Suporte Híbrido (Local / Produção):** O código detecta automaticamente o ambiente (`localhost` vs servidor de produção no Render).

### Procedimento para Embutir no WCM HCL da COPASA
1. Abra o arquivo `template/index.html`.
2. Copie todo o código HTML contido no arquivo.
3. No portal **WCM HCL**, adicione um componente do tipo **HTML Element** ou **Custom Script Component** e cole o código.
4. O script já está pré-configurado para comunicar com o backend hospedado em `https://matriz-patrocinios-copasa.onrender.com`.

---

## 🚀 Roadmap de Desenvolvimento

- [ ] **Fase 1: Inteligência Artificial & Automação**
  - [ ] Assistente para sugestão automática de notas por critério (LangChain + LLM local).
  - [ ] Sumarização automática do projeto com destaques dos pontos fortes.
  - [ ] Verificação automática de riscos e inconformidades no formulário.
  - [ ] Chatbot de RAG para suporte ao avaliador sobre normas de patrocínio.

- [ ] **Fase 2: Dashboard & Analytics**
  - [ ] Painel executivo de acompanhamento das propostas recebidas.
  - [ ] Relatórios analíticos exportáveis para Power BI.

- [ ] **Fase 3: Persistência & SSO**
  - [ ] Banco de dados relacional para guardar o histórico das avaliações.
  - [ ] Integração com Single Sign-On (SSO / Active Directory COPASA).

- [ ] **Fase 4: Expansão Mobile**
  - [ ] PWA para preenchimento com suporte offline.

---

## 🤝 Contribuição

1. Faça o **Fork** do repositório.
2. Crie uma branch para sua feature (`git checkout -b feature/minha-feature`).
3. Faça o **Commit** de suas alterações (`git commit -m 'feat: adiciona nova funcionalidade'`).
4. Envie para a branch remota (`git push origin feature/minha-feature`).
5. Abra um **Pull Request**.

---

## 📄 Licença e Contato

Direitos reservados à **COPASA - Companhia de Saneamento de Minas Gerais**. Uso interno exclusivo.

Para dúvidas ou suporte, entre em contato com a equipe de TI / Comunicação Corporativa.
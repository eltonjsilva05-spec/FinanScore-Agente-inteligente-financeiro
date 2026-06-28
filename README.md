# 📊 FinanScore — Agente Inteligente Financeiro

O **FinanScore** é um ecossistema SaaS B2B moderno e de alta performance desenvolvido em **Python** e **Streamlit**. Ele foi projetado para o gerenciamento inteligente de fluxos de caixa corporativos, centralização de contas bancárias de clientes e análise preditiva de saúde financeira.

A plataforma conta com uma arquitetura visual premium em Dark Mode, controle robusto de persistência de dados local (SQLite) e um ecossistema completo de monetização simulada por meio de travas de planos comerciais.

---

## 🚀 Funcionalidades Principais

### 🎨 1. Interface Premium & UX Avançada
* **Design Exclusivo:** Interface otimizada em Dark Mode utilizando a biblioteca nativa do Streamlit combinada com injeções de folhas de estilo customizadas (CSS).
* **Efeito Glassmorphism:** Cards de monitoramento bancário translúcidos com bordas responsivas e realce em Verde Esmeralda (`#2ecc71`).
* **Legibilidade:** Tipografia moderna integrada diretamente via Google Fonts (Inter Font Family).

### 🧠 2. Inteligência Corporativa & Diagnóstico
* **Termômetro de Saúde Orçamentária:** O sistema calcula em tempo real o índice de comprometimento financeiro com base na relação entre receitas e despesas operacionais.
* **Alertas Dinâmicos:** Classificação visual e analítica do status financeiro:
    * 🟢 **Excelente:** Margem saudável para investimentos (comprometimento $\le$ 50%).
    * 🟡 **Atenção:** Custos consumindo mais da metade do faturamento (comprometimento entre 51% e 75%).
    * 🔴 **Alerta Crítico:** Risco iminente de déficit de fluxo (comprometimento > 75%).

### 💼 3. Governança e Controle de Planos SaaS (Modelo B2B)
O sistema possui uma lógica integrada de restrição de recursos que simula um software comercial:
* ⚪ **Plano Gratuito:** Permite apenas o controle essencial de fluxo de caixa global. Bloqueia recursos avançados de conciliação e monitoramento bancário.
* 👑 **Plano Mensal / Anual (Premium):** Libera a integração automatizada de arquivos, gestão de caixa reserva e espelhamento de contas correntes de terceiros.
* 👑 **Modo Administrador (Admin):** Concede acesso a uma aba exclusiva de **Console de Governança**, permitindo alterar em tempo real o nível de acesso e o plano de qualquer usuário cadastrado no banco de dados.

### 🏦 4. Conciliação Automatizada e Módulo Bancário
* **Upload de Extratos:** Processamento em massa e integração de lançamentos financeiros via arquivos `.CSV`.
* **Centralização B2B:** Vinculação e cálculo dinâmico de saldos para diferentes contas e instituições financeiras de clientes ou fornecedores.

---

## 📂 Estrutura do Projeto

O repositório está organizado de forma limpa e modular:

```text
FinanScore/
│
├── .streamlit/
│   └── config.toml------# Definições de cores e tema Dark Mode Premium
│
├── app.py---------------# Arquivo principal (Interface, Abas e Regras de Negócio)
├── database.py----------# Engine de persistência SQLite, Criptografia e Consultas SQL
├── README.md------------# Documentação oficial do projeto
└── requisitos.txt-------# Dependências de bibliotecas do ecossistema

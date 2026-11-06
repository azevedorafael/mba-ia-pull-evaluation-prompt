# Otimização e Avaliação de Prompts

Projeto para transformar relatos de bugs em histórias de usuário claras e testáveis. O prompt é publicado no LangSmith Prompt Hub e avaliado com um dataset de 15 exemplos.

## Como Executar

### Pré-requisitos

- Python 3.10 ou superior
- Conta e chave de API do LangSmith
- Chave de API do Google Gemini ou da OpenAI

### Instalação e configuração

Na primeira configuração, abra um terminal na pasta raiz do repositório e crie o ambiente virtual:

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

**Windows (PowerShell)**

```powershell
py -3 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

**Windows (Prompt de Comando / CMD)**

```bat
py -3 -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
copy .env.example .env
```

O ambiente está ativo quando o nome `venv` aparece no início do prompt do terminal. Se abrir outro terminal ou reiniciar a sessão, entre novamente na pasta do repositório e ative o ambiente já criado:

```bash
# macOS / Linux
source venv/bin/activate
```

```powershell
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

```bat
REM Windows (Prompt de Comando / CMD)
venv\Scripts\activate.bat
```

Para sair do ambiente virtual, execute `deactivate` no terminal. Não é necessário recriar o ambiente nem reinstalar as dependências ao reabri-lo.

Preencha o `.env` local com as credenciais e configurações necessárias. Não versione esse arquivo. Configure `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, `USERNAME_LANGSMITH_HUB`, `LLM_PROVIDER`, `LLM_MODEL` e `EVAL_MODEL`; adicione a chave correspondente em `GOOGLE_API_KEY` ou `OPENAI_API_KEY`.

O prompt foi avaliado com o provider `google` e `gemini-3.8-flash` tanto para geração quanto para avaliação. Consulte a disponibilidade atual do modelo no provedor antes de executar.

### Fluxo de execução

Execute os comandos na raiz do repositório, com o ambiente virtual ativado:

```bash
# Baixa o prompt semente do LangSmith para prompts/bug_to_user_story_v1.yml
python src/pull_prompts.py

# Publica prompts/bug_to_user_story_v2.yml no LangSmith Prompt Hub
python src/push_prompts.py

# Avalia a versão publicada no dataset existente de 15 exemplos
python src/evaluate.py

# Executa os testes de validação
pytest tests/test_prompts.py tests/test_push_prompts.py
```

## Técnicas Aplicadas (Fase 2)

### Role Prompting

**O que define:** atribui ao modelo um papel e um contexto de atuação.

**Por que foi aplicada:** a perspectiva de Product Owner ajuda a identificar a necessidade da pessoa usuária e o benefício esperado, sem reduzir a resposta a uma proposta de implementação.

**Exemplo do prompt:**

```text
Você é um Product Owner experiente em transformar relatos de defeitos em histórias de usuário claras, úteis e testáveis para equipes de produto e engenharia.
```

### Few-shot Learning

**O que define:** demonstra a tarefa com exemplos de entrada e saída.

**Por que foi aplicada:** os exemplos mostram como cobrir resultados observáveis em relatos simples, validação, interface, dashboard, modais e problemas complexos sem deixar detalhes importantes implícitos. O prompt contém seis exemplos completos.

**Exemplo do prompt:**

```text
Entrada:
O botão "Adicionar ao Carrinho" não faz nada na página do produto. O cliente não vê confirmação e o contador do carrinho continua igual.

Saída:
**História de Usuário**
Como um cliente visualizando um produto, eu quero adicioná-lo ao carrinho, para que eu possa comprá-lo ao finalizar minhas compras.

**Critérios de Aceitação**
- Dado que estou visualizando um produto, quando clico em "Adicionar ao Carrinho", então o produto deve ser adicionado ao carrinho.
- Após a inclusão, devo ver uma confirmação e o contador do carrinho deve ser atualizado.
```

### Skeleton of Thought

**O que define:** organiza a resposta em seções predefinidas.

**Por que foi aplicada:** uma estrutura consistente facilita a revisão e mantém critérios, fatos técnicos, requisitos técnicos, tarefas e métricas nos lugares apropriados. Seções condicionais evitam perguntas ou conteúdo técnico sem necessidade.

**Exemplo do formato definido no prompt:**

```text
**História de Usuário**
Como [persona], eu quero [necessidade], para que [benefício].

**Critérios de Aceitação**
- Dado que [contexto], quando [ação], então [resultado verificável].

**Critérios Técnicos**
- [Especificação técnica explícita no relato.]

**Tarefas Técnicas Sugeridas**
- [Tarefa agrupada na fase correspondente.]

**Métricas de Sucesso**
- [Indicador: valor atual → meta.]
```

## Resultados Finais

A avaliação final usou o dataset original de 15 exemplos, sem alterações. O critério adotado é estrito: **cada uma das cinco métricas em cada exemplo deve ser igual ou superior a 0.8**. A média agregada, sozinha, não determina aprovação.

| Métrica | Média final | Menor nota individual | Limite |
|---|---:|---:|---:|
| Helpfulness | 0.98 | 0.965 | 0.8 |
| Correctness | 0.94 | 0.8971 | 0.8 |
| F1-Score | 0.90 | 0.8242 | 0.8 |
| Clarity | 0.98 | 0.96 | 0.8 |
| Precision | 0.99 | 0.95 | 0.8 |

Foram conferidas as 75 notas individuais (cinco métricas em cada um dos 15 exemplos); todas atingiram o limite.

### Comparação entre o prompt original e o otimizado

O prompt original ([v1](./prompts/bug_to_user_story_v1.yml)) tinha instruções genéricas, repetia `{bug_report}` no system e no user prompt, não definia uma persona clara e não apresentava exemplos nem critérios de aceitação verificáveis.

O prompt otimizado ([v2](./prompts/bug_to_user_story_v2.yml)) separa instruções de sistema do relato do usuário, define a persona de Product Owner, estabelece regras para preservar fatos e tratar lacunas, exige critérios observáveis e inclui exemplos para diferentes tipos e níveis de complexidade. Também orienta a preservar especificações, tarefas e métricas fornecidas no relato, distinguindo requisitos de recomendações.

#### Jornada de otimização do prompt v2

O histórico registra a versão inicial e quatro iterações de refinamento. Cada snapshot permite conferir como as instruções e os exemplos mudaram:

| Versão | Ajustes feitos com base nos resultados e no histórico |
|---|---|
| [Iteração 0 — baseline](./prompts/history/bug_to_user_story_v2_iteration_0.yml) | Primeira versão avaliada do prompt otimizado. Na primeira avaliação válida, obteve Helpfulness 0,98, Correctness 0,86, F1-Score 0,75, Clarity 0,98 e Precision 0,97. O F1 abaixo de 0,8 apontou a necessidade de cobrir melhor as informações esperadas. |
| [Iteração 1](./prompts/history/bug_to_user_story_v2_iteration_1.yml) | Tornou os critérios de aceitação mais completos, pediu a preservação de passos, valores e estados, limitou perguntas a lacunas essenciais e adicionou uma revisão de cobertura. Também incluiu um exemplo de carrinho. O F1 subiu de 0,75 para 0,79; Correctness foi de 0,86 para 0,89 e Precision de 0,97 para 0,98. O F1 ainda não atingia o limite. |
| [Iteração 2](./prompts/history/bug_to_user_story_v2_iteration_2.yml) | Passou a separar fatos de recomendações, organizar relatos com vários componentes, preservar metas explícitas e incluir plano técnico quando pertinente. O exemplo de webhook demonstrou como manter endpoint, erro e resultado esperado. As médias ficaram acima de 0,8, mas a revisão passou a exigir que cada nota individual também atingisse o limite; a média, sozinha, não comprovava isso. |
| [Iteração 3](./prompts/history/bug_to_user_story_v2_iteration_3.yml) | Especializou instruções para contagens de dashboard e modais em telas pequenas, acrescentando exemplos de consistência entre contagem e lista, interação com controles e verificações de acessibilidade. A avaliação individual ainda encontrou F1 de 0,7355 no caso complexo de sincronização offline, indicando omissões de requisitos técnicos detalhados. |
| [Iteração 4](./prompts/history/bug_to_user_story_v2_iteration_4.yml) | Reforçou o inventário e a preservação de requisitos, números, protocolos, endpoints, payloads, algoritmos, limites, stack, tarefas por fase e métricas. Incluiu seções próprias para critérios técnicos, tarefas e métricas de sucesso, além de um exemplo complexo de sincronização offline. Na avaliação final, as 75 notas — cinco métricas em cada um dos 15 exemplos — ficaram todas em pelo menos 0,8. |

#### Como as mudanças se refletem nas métricas

Helpfulness e Correctness são métricas derivadas no avaliador do projeto: Helpfulness é a média entre Clarity e Precision; Correctness é a média entre F1-Score e Precision. As outras três são avaliadas diretamente. Portanto, melhorar cobertura pode elevar F1 e Correctness, enquanto fatos inventados ou detalhes irrelevantes podem reduzir Precision e, por consequência, Helpfulness e Correctness.

| Métrica | Média: baseline → final | Menor nota final por exemplo | Como os ajustes do prompt se relacionam com a métrica |
|---|---:|---:|---|
| Helpfulness | 0,98 → 0,98 | 0,965 | Depende de Clarity e Precision. A organização por seções e a redução de perguntas desnecessárias ajudam a manter respostas claras e focadas; a média agregada permaneceu estável após o refinamento. |
| Correctness | 0,86 → 0,94 | 0,8971 | É a média de F1-Score e Precision. Preservar mais requisitos da referência melhora a cobertura, enquanto separar fatos de recomendações ajuda a evitar afirmações sem suporte. |
| F1-Score | 0,75 → 0,90 | 0,8242 | Equilibra Precision e Recall. Critérios mais completos, preservação de valores e cenários e exemplos complexos reduzem omissões sem incentivar conteúdo irrelevante. |
| Clarity | 0,98 → 0,98 | 0,96 | Considera organização, linguagem direta, ausência de ambiguidade e concisão. O formato em Markdown e as seções específicas ajudam a organizar respostas mais completas sem perder legibilidade; a média permaneceu estável. |
| Precision | 0,97 → 0,99 | 0,95 | Considera ausência de alucinações, foco e correção factual. As regras para não transformar hipóteses em fatos e identificar sugestões como propostas ajudam a manter as respostas pertinentes e verificáveis. |

Os valores de baseline e final são médias arredondadas do conjunto. A relação descrita é coerente com as mudanças e os resultados observados, mas não isola o efeito causal de cada instrução: várias regras mudaram entre versões, e as notas são atribuídas pelo avaliador LLM. O critério final foi aplicado por exemplo, não apenas sobre as médias.

### Evidências no LangSmith

- [Dataset público de avaliação — 15 exemplos e experimentos](https://smith.langchain.com/public/8bda8e60-d51c-4649-a23f-b850b4f59cde/d)
- [Prompt publicado no LangSmith Prompt Hub](https://smith.langchain.com/prompts/bug_to_user_story_v2/5dc7a4f3?organizationId=b910c5c3-128f-49f1-990b-135157bcf4b4)

O dashboard abaixo mostra o dataset, os experimentos registrados, os cinco indicadores de feedback e a execução final concluída em 15/15 exemplos. A tabela de resultados acima informa os menores valores individuais; os traces públicos permitem inspecionar cada execução em detalhe.

![Dashboard do LangSmith com os experimentos, métricas e progresso da avaliação final](./langsmith-final-evaluation.png)

Os três traces públicos abaixo mostram exemplos de diferentes níveis de complexidade. Cada página permite consultar a árvore de execução, a entrada, a saída e os feedbacks das cinco métricas:

- [Exemplo simples — inclusão de produto no carrinho](https://smith.langchain.com/public/a39ccea5-efb3-47c0-98b6-46f5f28546ee/r)
- [Exemplo médio — webhook de pagamento](https://smith.langchain.com/public/539f3c11-c01d-422b-b12d-2ff271956c57/r)
- [Exemplo complexo — sincronização offline](https://smith.langchain.com/public/c7a2d5e1-a0ff-45bb-b667-2026e205e164/r)

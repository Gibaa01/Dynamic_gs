<div align="center">

# SAFS — Surface Autonomous Fleet System

<br/>

> Sistema de roteamento e triagem de resposta a enchentes, modelado sobre um  
> **grafo de municípios do RS**, com **Estruturas de Dados**, **Algoritmos Gulosos** e **Força Bruta** em Python puro.

**FIAP · Global Solution 2026 · 1º Semestre**  
Disciplina: Dynamic Programming, Algorithms and Data Structures | Turma: 2ESPH

</div>

---

## Índice

- [Contexto de Negócio](#-contexto-de-negócio)
- [Arquitetura do Projeto](#-arquitetura-do-projeto)
- [Estruturas de Dados Implementadas](#-estruturas-de-dados-implementadas)
- [Algoritmos Implementados](#-algoritmos-implementados)
- [Análise de Desempenho](#-análise-de-desempenho)
- [Estrutura de Pacotes](#-estrutura-de-pacotes)
- [Como Executar](#-como-executar)
- [Testes Automatizados](#-testes-automatizados)
- [Visualizações Geradas](#-visualizações-geradas)
- [Créditos](#-créditos)

---

## Contexto de Negócio

As **enchentes no Rio Grande do Sul em 2024** expuseram a fragilidade da logística de resposta a desastres: sem rotas otimizadas e sem triagem por risco, equipes de socorro chegam tarde demais aos municípios mais vulneráveis.

O módulo **Dynamic GS** do SAFS resolve esse problema modelando 12 municípios gaúchos como um **grafo ponderado**, onde cada aresta representa o tempo de deslocamento em horas. A partir desse grafo, o sistema responde a duas perguntas críticas:

1. **Qual a rota de cobertura mínima** que conecta todos os municípios com o menor custo total? → *Algoritmo de Prim (MST)*
2. **Qual o caminho mais rápido** até os municípios de alto risco a partir do hub de Porto Alegre? → *Dijkstra + BST de triagem*

```
                ┌─────────────────────────────────────┐
                │     Hub Central — Porto Alegre      │  ← Origem das rotas
                └──────────────────┬──────────────────┘
                                   │
                ┌──────────────────▼──────────────────┐
                │   Grafo de Municípios do RS          │  ← Este sistema
                │   12 vértices · 15 arestas           │
                └──────────────────┬──────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
     ┌────────▼───────┐  ┌─────────▼──────┐  ┌──────────▼─────┐
     │  Prim (MST)    │  │   Dijkstra     │  │  Força Bruta   │
     │  cobertura     │  │   caminhos     │  │  backtracking  │
     │  mínima        │  │   mínimos      │  │  + análise O() │
     └────────────────┘  └────────────────┘  └────────────────┘
```

---

## Arquitetura do Projeto

O projeto separa claramente dados, algoritmos, análise e visualização:

```
┌──────────────────────────────────────────────────────────────────┐
│                      VISUALIZAÇÕES                               │
│         Matplotlib · NetworkX · Figuras PNG exportadas           │
│                   src/visualizations.py                          │
├──────────────────────────────────────────────────────────────────┤
│                   MONITOR DE DESEMPENHO                          │
│         Comparativo Força Bruta × Guloso · Gap de Otimalidade    │
│                 src/performance_monitor.py                       │
├──────────────────────────────────────────────────────────────────┤
│                      ALGORITMOS                                  │
│   Prim · Dijkstra · Força Bruta com Backtracking                 │
│           src/greedy.py · src/brute_force.py                     │
├──────────────────────────────────────────────────────────────────┤
│                   ESTRUTURAS DE DADOS                            │
│         GrafoMunicipios · BST · FilaPrioridade · Conjuntos       │
│                  src/data_structures.py                          │
└──────────────────────────────────────────────────────────────────┘
```

| Módulo | Responsabilidade | Depende de |
|---|---|---|
| **data_structures** | Grafo, BST, FilaPrioridade, dados dos municípios | — |
| **greedy** | Prim (MST) e Dijkstra com instrumentação | data_structures |
| **brute_force** | Backtracking exaustivo + análise de escala | data_structures |
| **performance_monitor** | Comparativo de tempo, memória e operações | greedy, brute_force |
| **visualizations** | Geração dos 4 gráficos em PNG | todos os anteriores |

> **Regra de ouro:** `data_structures.py` não importa nenhum outro módulo do projeto — é a base da pirâmide.

---

## Estruturas de Dados Implementadas

Termos do domínio mapeados diretamente nas classes:

| Termo do Domínio | Classe / Tipo | Estereótipo | Descrição |
|------------------|---------------|-------------|-----------|
| **Município** | `tuple` (id, nome, risco, custo, pop) | Vértice | Nó do grafo com índice de risco e custo de atendimento |
| **Rota** | `aresta (u, v, peso)` | Aresta ponderada | Conexão entre municípios com tempo em horas |
| **Grafo de Municípios** | `GrafoMunicipios` | Grafo não-dirigido | Lista de adjacência com BFS, DFS e serialização JSON |
| **Fila de Prioridade** | `FilaPrioridade` | Min-Heap | Wrapper sobre `heapq` para os algoritmos gulosos |
| **Árvore de Triagem** | `BinarySearchTree` | BST por risco | Ordena municípios pelo índice de risco; busca por intervalo |
| **Conjunto de Visitados** | `set[int]` | Conjunto hash | Controle de nós processados em BFS, DFS e backtracking |

### Estruturas — Invariantes e Propriedades

```
┌───────────────────────────────────────────────────────────────────┐
│  Estruturas principais e suas garantias                           │
├────────────────┬──────────────────────────┬───────────────────────┤
│ GrafoMunicipios│  FilaPrioridade          │  BinarySearchTree     │
│────────────────│──────────────────────────│───────────────────────│
│ adj: dict      │  _heap: list[tuple]      │  chave: risco (float) │
│ vertices: dict │  baseada em heapq        │  in-order = crescente │
│────────────────│──────────────────────────│───────────────────────│
│ BFS / DFS      │  extrair_min() → O(logN) │  buscar_intervalo()   │
│ alcançam todos │  inserir()    → O(logN)  │  remover() recursivo  │
│ (grafo conexo) │  → sem duplicatas visuais│  → sucessor in-order  │
└────────────────┴──────────────────────────┴───────────────────────┘
```

---

## Algoritmos Implementados

### 1. Algoritmo de Prim — `AlgoritmoPrim`

Constrói a **Árvore Geradora Mínima (MST)** do grafo, representando a rede de cobertura de custo mínimo que conecta todos os municípios:

```python
# Esqueleto do Prim com heap e instrumentação
custo[origem] = 0.0
heap = [(0.0, origem)]

while heap:
    peso_min, u = heapq.heappop(heap)       # Extrai o menor custo disponível
    na_arvore.add(u)
    for vizinho, peso in grafo.vizinhos(u): # Relaxa arestas adjacentes
        if vizinho not in na_arvore and peso < custo[vizinho]:
            custo[vizinho] = peso
            heapq.heappush(heap, (peso, vizinho))
```

```
         Prim executar(origem)
                    │
    ┌───────────────▼───────────────┐
    │   1. Inicializar custos ∞     │  ← custo[origem] = 0
    ├───────────────────────────────┤
    │   2. Extrair mínimo do heap   │  ← O(log N) por operação
    ├───────────────────────────────┤
    │   3. Adicionar à MST          │  ← Registra aresta e predecessor
    ├───────────────────────────────┤
    │   4. Relaxar vizinhos         │  ← Atualiza heap se peso < custo atual
    └───────────────────────────────┘
    Complexidade: O((V + E) log V)
```

---

### 2. Algoritmo de Dijkstra — `AlgoritmoDijkstra`

Calcula os **caminhos mínimos** de Porto Alegre a todos os demais municípios. Combinado com a BST, gera a lista de **rotas de atendimento prioritário** para municípios de alto risco:

```python
# Dijkstra com reconstrução de caminho
dist[origem] = 0.0

while heap:
    d_u, u = heapq.heappop(heap)
    for vizinho, peso in grafo.vizinhos(u):
        nova_dist = dist[u] + peso          # Relaxamento
        if nova_dist < dist[vizinho]:
            dist[vizinho] = nova_dist
            predecessor[vizinho] = u        # Para reconstrução do caminho
            heapq.heappush(heap, (nova_dist, vizinho))
```

```
   BST (índice de risco)          Dijkstra (distâncias mínimas)
┌────────────────────┐           ┌────────────────────────────┐
│  buscar_intervalo  │           │  executar(hub=POA)         │
│  (0.65, 1.0)       │──────────►│  reconstruir_caminho()     │
│  → alto risco      │  filtra   │  → rota + custo em horas   │
└────────────────────┘           └────────────────────────────┘
```

---

### 3. Força Bruta com Backtracking — `ForcaBruta`

Enumera **todos os caminhos simples** entre dois municípios por backtracking recursivo. Serve como referência de optimalidade para avaliar o gap do algoritmo guloso:

```python
def _backtrack(self, atual, destino, visitados, caminho, custo_acumulado):
    if atual == destino:
        # Avalia e registra o caminho encontrado
        if custo_acumulado < self.melhor_custo:
            self.melhor_custo = custo_acumulado
        return

    if custo_acumulado >= self.melhor_custo:   # Poda por custo
        return

    for vizinho, peso in self.grafo.vizinhos(atual):
        if vizinho not in visitados:
            visitados.add(vizinho)
            self._backtrack(vizinho, destino, visitados, ...)
            visitados.remove(vizinho)          # Backtrack
```

```
         Backtracking com poda
                    │
    ┌───────────────▼───────────────┐
    │   Chegou ao destino?          │  → Registra caminho
    ├───────────────────────────────┤
    │   Custo ≥ melhor conhecido?   │  → Poda (prune)
    ├───────────────────────────────┤
    │   Para cada vizinho não vis.  │  → Expande recursivamente
    ├───────────────────────────────┤
    │   Remove do conjunto          │  → Backtrack (desfaz escolha)
    └───────────────────────────────┘
    Complexidade: O(N!) no pior caso
```

---

## Análise de Desempenho

O módulo `performance_monitor.py` executa os três algoritmos sobre subgrafos de tamanho crescente (N = 3 a 12) e mede tempo, memória e número de operações:

```
 N    │  FB (ms)   │  Prim (ms) │  Dijkstra (ms) │   FB ops
──────┼────────────┼────────────┼────────────────┼──────────
  3   │     <0.1   │     <0.1   │         <0.1   │        5
  5   │     <0.1   │     <0.1   │         <0.1   │       18
  8   │     ~2.0   │     <0.1   │         <0.1   │      210
 10   │    ~25.0   │     <0.1   │         <0.1   │     1890
 12   │   ~300+    │     <0.1   │         <0.1   │    20000+
```

| Algoritmo | Complexidade de Tempo | Complexidade de Espaço | Garante ótimo? |
|---|---|---|---|
| **Força Bruta** | O(N!) no pior caso | O(N) pilha de recursão | ✅ Sim |
| **Prim (MST)** | O((V + E) log V) | O(V + E) | ✅ Para MST |
| **Dijkstra** | O((V + E) log V) | O(V) | ✅ Sim |

> **Ponto de cruzamento:** para N ≤ 8 a Força Bruta é tolerável (< 100 ms). Para N > 10 o tempo cresce de forma fatorial e os algoritmos gulosos são até 1000× mais rápidos.

---

## Estrutura de Pacotes

```
Dynamic_gs/
│
├── src/                                 ← Código-fonte principal
│   ├── data_structures.py               ─ GrafoMunicipios · BST · FilaPrioridade
│   │                                      Dados dos 12 municípios e 15 arestas do RS
│   ├── greedy.py                        ─ AlgoritmoPrim (MST) + AlgoritmoDijkstra
│   │                                      Rota de atendimento prioritário
│   ├── brute_force.py                   ─ ForcaBruta com backtracking e poda
│   │                                      Análise de crescimento por subgrafo
│   ├── performance_monitor.py           ─ Comparativo Força Bruta × Guloso
│   │                                      Métricas: tempo, memória, operações, gap
│   └── visualizations.py               ─ Geração dos 4 gráficos em PNG
│                                          Usa Matplotlib e NetworkX
│
├── tests/
│   └── test_algorithms.py              ─ 30+ testes com pytest
│                                          Grafo · BST · Heap · FB · Prim · Dijkstra
│
├── DATA/
│   └── processed/
│       ├── fig1_grafo_mst.png           ─ Grafo RS com MST destacada
│       ├── fig2_bst.png                 ─ Árvore BST por índice de risco
│       ├── fig3_tempo_vs_n.png          ─ Curvas de tempo × N (escala log)
│       ├── fig4_gap_otimalidade.png     ─ Gap % entre FB e Prim por N
│       ├── grafo_rs.json               ─ Grafo serializado
│       ├── metricas_desempenho.json     ─ Resultados do comparativo
│       └── gap_otimalidade.json         ─ Gap de otimalidade por N
│
├── notebooks/
│   └── analise_resultados.ipynb        ─ Análise exploratória dos resultados
│
└── requirements.txt                    ─ Dependências Python
```

---

## Como Executar

### Pré-requisitos

**Python 3.10+** instalado. As bibliotecas de visualização são opcionais para os módulos principais.

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd Dynamic_gs
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Executar os módulos

```bash
# Estruturas de dados e travessias BFS/DFS
python src/data_structures.py

# Algoritmos gulosos: Prim (MST) e Dijkstra
python src/greedy.py

# Força bruta com backtracking e análise de escala
python src/brute_force.py

# Comparativo de desempenho e gap de otimalidade
python src/performance_monitor.py

# Gerar as 4 figuras PNG em DATA/processed/
python src/visualizations.py
```

### Via Jupyter Notebook

```bash
jupyter notebook notebooks/analise_resultados.ipynb
```

---

## Testes Automatizados

O projeto conta com **30+ testes** organizados em 6 classes cobrindo todas as estruturas e algoritmos:

```bash
# Executar todos os testes
pytest tests/ -v

# Executar com cobertura
pytest tests/ -v --tb=short
```

| Classe de Teste | O que valida |
|---|---|
| **TestGrafo** | Número de vértices e arestas, vizinhos, BFS/DFS atingem todos os nós |
| **TestBST** | In-order crescente, busca por intervalo, inserção/remoção, propriedade BST |
| **TestFilaPrioridade** | Propriedade min-heap, estado de vazia |
| **TestForcaBruta** | Caminho encontrado, custo ótimo, instrumentação, backtrack, subgrafo |
| **TestPrim** | MST com N−1 arestas, custo positivo, instrumentação do heap |
| **TestDijkstra** | Distância zero na origem, sem negativos, caminho reconstruído, todos alcançados |

---

## Visualizações Geradas

O módulo `visualizations.py` produz 4 figuras salvas em `DATA/processed/`:

| Figura | Arquivo | Descrição |
|---|---|---|
| **Fig. 1** | `fig1_grafo_mst.png` | Grafo completo do RS com arestas da MST em vermelho e vértices coloridos por índice de risco |
| **Fig. 2** | `fig2_bst.png` | Árvore BST com municípios organizados por risco (verde = baixo, vermelho = alto) |
| **Fig. 3** | `fig3_tempo_vs_n.png` | Curvas de tempo × N em escala logarítmica, destacando a explosão combinatorial da Força Bruta |
| **Fig. 4** | `fig4_gap_otimalidade.png` | Gap percentual entre o ótimo (Força Bruta) e o guloso (Prim) para cada tamanho de subgrafo |

---

## Créditos

<div align="center">

| Nome | RM |
|---|---|
| Bruno Lobosque | 561254 |
| Giovanni Tarzoni | 564014 |
| Enrico Gianni | 561400 |
| Jean Carlos | 566439 |

<br/>

Projeto desenvolvido para a **Global Solution FIAP 2026 · 1º Semestre**

*"Um algoritmo guloso não garante o ótimo global — mas chega lá em tempo polinomial."*

</div>

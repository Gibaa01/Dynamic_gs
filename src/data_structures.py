import heapq
import json
import pickle
from pathlib import Path


MUNICIPIOS_RS = [
    (4314902, "Porto Alegre",        0.72, 1850.0, 1332570),
    (4300406, "Alegrete",            0.58, 620.0,   77653),
    (4307005, "Caxias do Sul",       0.41, 980.0,  435545),
    (4316808, "Santa Maria",         0.65, 740.0,  261031),
    (4313409, "Pelotas",             0.55, 810.0,  328275),
    (4309209, "Ijuí",                0.48, 530.0,   78915),
    (4318705, "Uruguaiana",          0.60, 590.0,  125435),
    (4310801, "Lajeado",             0.78, 420.0,   80439),
    (4320008, "Venâncio Aires",      0.82, 390.0,   65000),
    (4303103, "Canoas",              0.69, 900.0,  347437),
    (4305108, "Cruz Alta",           0.44, 510.0,   57542),
    (4322608, "Bagé",                0.50, 640.0,  116794),
]

ARESTAS_RS = [
    (4314902, 4300406, 5.5),
    (4314902, 4316808, 2.8),
    (4314902, 4303103, 0.5),
    (4314902, 4313409, 2.5),
    (4316808, 4309209, 2.0),
    (4316808, 4305108, 1.5),
    (4316808, 4318705, 3.0),
    (4300406, 4318705, 2.2),
    (4300406, 4322608, 2.0),
    (4313409, 4322608, 2.8),
    (4307005, 4310801, 1.2),
    (4307005, 4303103, 1.5),
    (4310801, 4320008, 0.6),
    (4309209, 4305108, 1.8),
    (4303103, 4310801, 1.0),
]


class GrafoMunicipios:
    def __init__(self):
        self.adj: dict[int, list[tuple[int, float]]] = {}
        self.vertices: dict[int, tuple] = {}

    def adicionar_vertice(self, vertice: tuple) -> None:
        id_municipio = vertice[0]
        self.vertices[id_municipio] = vertice
        if id_municipio not in self.adj:
            self.adj[id_municipio] = []

    def adicionar_aresta(self, u: int, v: int, peso: float) -> None:
        self.adj[u].append((v, peso))
        self.adj[v].append((u, peso))

    def vizinhos(self, u: int) -> list[tuple[int, float]]:
        return self.adj.get(u, [])

    def bfs(self, origem: int) -> list[int]:
        from collections import deque

        visitados: set[int] = set()
        fila: deque[int] = deque([origem])
        ordem: list[int] = []

        visitados.add(origem)

        while fila:
            no = fila.popleft()
            ordem.append(no)

            for vizinho, _ in self.adj.get(no, []):
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    fila.append(vizinho)

        return ordem

    def dfs(self, origem: int) -> list[int]:
        visitados: set[int] = set()
        pilha: list[int] = [origem]
        ordem: list[int] = []

        while pilha:
            no = pilha.pop()
            if no not in visitados:
                visitados.add(no)
                ordem.append(no)
                for vizinho, _ in self.adj.get(no, []):
                    if vizinho not in visitados:
                        pilha.append(vizinho)

        return ordem

    def serializar(self, caminho: str) -> None:
        dados = {
            "vertices": {str(k): list(v) for k, v in self.vertices.items()},
            "adj": {str(k): v for k, v in self.adj.items()},
        }
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        print(f"[Grafo] Serializado em '{caminho}'")

    def __repr__(self) -> str:
        return (
            f"GrafoMunicipios(V={len(self.vertices)}, "
            f"E={sum(len(v) for v in self.adj.values()) // 2})"
        )


class FilaPrioridade:
    def __init__(self):
        self._heap: list[tuple[float, int]] = []

    def inserir(self, custo: float, no: int) -> None:
        heapq.heappush(self._heap, (custo, no))

    def extrair_min(self) -> tuple[float, int]:
        return heapq.heappop(self._heap)

    def vazia(self) -> bool:
        return len(self._heap) == 0

    def __len__(self) -> int:
        return len(self._heap)


class Node:
    def __init__(self, dados: tuple):
        self.chave: float = dados[2]
        self.dados: tuple = dados
        self.esquerda: "Node | None" = None
        self.direita: "Node | None" = None


class BinarySearchTree:
    def __init__(self):
        self.raiz: Node | None = None

    def inserir(self, dados: tuple) -> None:
        no = Node(dados)
        if self.raiz is None:
            self.raiz = no
            return
        atual = self.raiz
        while True:
            if no.chave < atual.chave:
                if atual.esquerda is None:
                    atual.esquerda = no
                    break
                atual = atual.esquerda
            else:
                if atual.direita is None:
                    atual.direita = no
                    break
                atual = atual.direita

    def buscar_intervalo(self, r_min: float, r_max: float) -> list[tuple]:
        resultados: list[tuple] = []
        self._buscar_intervalo_rec(self.raiz, r_min, r_max, resultados)
        return resultados

    def _buscar_intervalo_rec(
        self, no: Node | None, r_min: float, r_max: float, acc: list
    ) -> None:
        if no is None:
            return
        if no.chave > r_min:
            self._buscar_intervalo_rec(no.esquerda, r_min, r_max, acc)
        if r_min <= no.chave <= r_max:
            acc.append(no.dados)
        if no.chave < r_max:
            self._buscar_intervalo_rec(no.direita, r_min, r_max, acc)

    def percurso_in_order(self) -> list[tuple]:
        resultado: list[tuple] = []
        self._in_order_rec(self.raiz, resultado)
        return resultado

    def _in_order_rec(self, no: Node | None, acc: list) -> None:
        if no is None:
            return
        self._in_order_rec(no.esquerda, acc)
        acc.append(no.dados)
        self._in_order_rec(no.direita, acc)

    def altura(self) -> int:
        return self._altura_rec(self.raiz)

    def _altura_rec(self, no: Node | None) -> int:
        if no is None:
            return 0
        return 1 + max(self._altura_rec(no.esquerda), self._altura_rec(no.direita))

    def esta_balanceada(self) -> bool:
        return self._balanceada_rec(self.raiz) != -1

    def _balanceada_rec(self, no: Node | None) -> int:
        if no is None:
            return 0
        h_esq = self._balanceada_rec(no.esquerda)
        if h_esq == -1:
            return -1
        h_dir = self._balanceada_rec(no.direita)
        if h_dir == -1:
            return -1
        if abs(h_esq - h_dir) > 1:
            return -1
        return 1 + max(h_esq, h_dir)

    def remover(self, id_municipio: int) -> None:
        self.raiz = self._remover_rec(self.raiz, id_municipio)

    def _remover_rec(self, no: Node | None, id_alvo: int) -> Node | None:
        if no is None:
            return None
        if no.dados[0] == id_alvo:
            if no.esquerda is None and no.direita is None:
                return None
            if no.esquerda is None:
                return no.direita
            if no.direita is None:
                return no.esquerda
            sucessor = self._minimo(no.direita)
            no.chave = sucessor.chave
            no.dados = sucessor.dados
            no.direita = self._remover_rec(no.direita, sucessor.dados[0])
        else:
            no.esquerda = self._remover_rec(no.esquerda, id_alvo)
            no.direita = self._remover_rec(no.direita, id_alvo)
        return no

    def _minimo(self, no: Node) -> Node:
        while no.esquerda is not None:
            no = no.esquerda
        return no

    def exibir(self) -> None:
        print("\n=== BST — Municípios por Índice de Risco (in-order) ===")
        for m in self.percurso_in_order():
            print(f"  risco={m[2]:.2f} | {m[1]:<20} | custo=R${m[3]:,.0f}k | pop={m[4]:,}")
        print(f"\n  Altura: {self.altura()} | Balanceada: {self.esta_balanceada()}")


def construir_grafo_rs() -> GrafoMunicipios:
    grafo = GrafoMunicipios()
    for municipio in MUNICIPIOS_RS:
        grafo.adicionar_vertice(municipio)
    for u, v, peso in ARESTAS_RS:
        grafo.adicionar_aresta(u, v, peso)
    return grafo


def construir_bst_rs(grafo: GrafoMunicipios) -> BinarySearchTree:
    bst = BinarySearchTree()
    for municipio in grafo.vertices.values():
        bst.inserir(municipio)
    return bst


def main():
    print("=" * 60)
    print("  Global Solution 2026 — Estruturas de Dados")
    print("  Cenário A: Enchentes RS 2024")
    print("=" * 60)

    grafo = construir_grafo_rs()
    print(f"\n[Grafo] {grafo}")
    print(f"[Grafo] Vizinhos de Porto Alegre (4314902): {grafo.vizinhos(4314902)}")

    bfs_ordem = grafo.bfs(4314902)
    print(f"[BFS] Ordem de visita a partir de POA: {bfs_ordem}")

    dfs_ordem = grafo.dfs(4314902)
    print(f"[DFS] Ordem de visita a partir de POA: {dfs_ordem}")

    raiz_projeto = Path(__file__).resolve().parent.parent
    pasta_processado = raiz_projeto / "data" / "processed"
    pasta_processado.mkdir(parents=True, exist_ok=True)
    grafo.serializar(str(pasta_processado / "grafo_rs.json"))

    bst = construir_bst_rs(grafo)
    bst.exibir()

    print("\n[BST] Municípios com risco entre 0.60 e 0.80:")
    for m in bst.buscar_intervalo(0.60, 0.80):
        print(f"  {m[1]:<20} risco={m[2]:.2f}")

    print("\n[Heap] Simulando fila de prioridade do Guloso:")
    fila = FilaPrioridade()
    for municipio in MUNICIPIOS_RS:
        fila.inserir(-municipio[2], municipio[0])

    print("  Ordem de atendimento (maior risco primeiro):")
    temp = []
    while not fila.vazia():
        custo, id_m = fila.extrair_min()
        nome = grafo.vertices[id_m][1]
        print(f"    risco={-custo:.2f} | {nome}")
        temp.append((custo, id_m))

    visitados: set[int] = set()
    visitados.add(4314902)
    visitados.add(4303103)
    print(f"\n[Set] Nós visitados (exemplo): {visitados}")
    print(f"[Set] 4314902 visitado? {4314902 in visitados}")

    print("\n[OK] data_structures.py executado com sucesso.")


if __name__ == "__main__":
    main()
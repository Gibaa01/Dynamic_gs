import heapq
import time
import tracemalloc
from data_structures import (
    GrafoMunicipios,
    BinarySearchTree,
    construir_grafo_rs,
    construir_bst_rs,
)


class AlgoritmoPrim:
    def __init__(self, grafo: GrafoMunicipios):
        self.grafo = grafo
        self.insercoes_heap: int = 0
        self.extrações_heap: int = 0

    def executar(self, origem: int) -> dict:
        vertices = list(self.grafo.vertices.keys())

        custo: dict[int, float] = {v: float("inf") for v in vertices}
        predecessor: dict[int, int | None] = {v: None for v in vertices}
        na_arvore: set[int] = set()
        ordem_visita: list[int] = []

        custo[origem] = 0.0

        heap: list[tuple[float, int]] = [(0.0, origem)]
        self.insercoes_heap = 1
        self.extrações_heap = 0

        mst_arestas: list[tuple[int, int, float]] = []

        while heap:
            peso_min, u = heapq.heappop(heap)
            self.extrações_heap += 1

            if u in na_arvore:
                continue

            na_arvore.add(u)
            ordem_visita.append(u)

            if predecessor[u] is not None:
                mst_arestas.append((predecessor[u], u, peso_min))

            for vizinho, peso in self.grafo.vizinhos(u):
                if vizinho not in na_arvore and peso < custo[vizinho]:
                    custo[vizinho] = peso
                    predecessor[vizinho] = u
                    heapq.heappush(heap, (peso, vizinho))
                    self.insercoes_heap += 1

        custo_total = sum(p for _, _, p in mst_arestas)

        return {
            "mst_arestas": mst_arestas,
            "custo_total": custo_total,
            "predecessores": predecessor,
            "ordem_visita": ordem_visita,
            "insercoes_heap": self.insercoes_heap,
            "extracoes_heap": self.extrações_heap,
        }


class AlgoritmoDijkstra:
    def __init__(self, grafo: GrafoMunicipios):
        self.grafo = grafo
        self.arestas_relaxadas: int = 0
        self.insercoes_heap: int = 0

    def executar(self, origem: int) -> dict:
        vertices = list(self.grafo.vertices.keys())

        dist: dict[int, float] = {v: float("inf") for v in vertices}
        predecessor: dict[int, int | None] = {v: None for v in vertices}
        finalizado: set[int] = set()
        ordem_visita: list[int] = []

        dist[origem] = 0.0
        heap: list[tuple[float, int]] = [(0.0, origem)]
        self.insercoes_heap = 1
        self.arestas_relaxadas = 0

        while heap:
            d_u, u = heapq.heappop(heap)

            if u in finalizado:
                continue

            finalizado.add(u)
            ordem_visita.append(u)

            for vizinho, peso in self.grafo.vizinhos(u):
                self.arestas_relaxadas += 1
                nova_dist = dist[u] + peso
                if nova_dist < dist[vizinho]:
                    dist[vizinho] = nova_dist
                    predecessor[vizinho] = u
                    heapq.heappush(heap, (nova_dist, vizinho))
                    self.insercoes_heap += 1

        return {
            "dist": dist,
            "predecessor": predecessor,
            "ordem_visita": ordem_visita,
            "arestas_relaxadas": self.arestas_relaxadas,
            "insercoes_heap": self.insercoes_heap,
        }

    def reconstruir_caminho(self, predecessor: dict, destino: int) -> list[int]:
        caminho: list[int] = []
        atual = destino
        while atual is not None:
            caminho.append(atual)
            atual = predecessor[atual]
        caminho.reverse()
        return caminho


def municipios_alto_risco(bst: BinarySearchTree, limiar: float = 0.65) -> list[tuple]:
    return bst.buscar_intervalo(limiar, 1.0)


def rota_atendimento_prioritario(
    grafo: GrafoMunicipios,
    bst: BinarySearchTree,
    hub: int,
    limiar_risco: float = 0.65,
) -> dict:
    dijkstra = AlgoritmoDijkstra(grafo)
    resultado_dijkstra = dijkstra.executar(hub)

    alvos = municipios_alto_risco(bst, limiar_risco)

    rotas = {}
    for municipio in alvos:
        id_m = municipio[0]
        custo = resultado_dijkstra["dist"].get(id_m, float("inf"))
        caminho = dijkstra.reconstruir_caminho(resultado_dijkstra["predecessor"], id_m)
        rotas[id_m] = {
            "nome": municipio[1],
            "risco": municipio[2],
            "custo_horas": custo,
            "caminho": caminho,
        }

    rotas_ordenadas = dict(
        sorted(rotas.items(), key=lambda x: -x[1]["risco"])
    )

    return {
        "hub": hub,
        "limiar_risco": limiar_risco,
        "rotas": rotas_ordenadas,
        "arestas_relaxadas": dijkstra.arestas_relaxadas,
    }


def main():
    print("=" * 65)
    print("  Global Solution 2026 — Algoritmos Gulosos")
    print("  Cenário A: Enchentes RS 2024")
    print("=" * 65)

    grafo = construir_grafo_rs()
    bst   = construir_bst_rs(grafo)

    print("\n[PRIM] Construindo Árvore Geradora Mínima...")
    prim = AlgoritmoPrim(grafo)

    tracemalloc.start()
    t0 = time.perf_counter()
    resultado_prim = prim.executar(4314902)
    t1 = time.perf_counter()
    _, pico_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"  Custo total da MST : {resultado_prim['custo_total']:.2f} horas")
    print(f"  Arestas na MST     : {len(resultado_prim['mst_arestas'])}")
    print(f"  Inserções no heap  : {resultado_prim['insercoes_heap']}")
    print(f"  Extrações do heap  : {resultado_prim['extracoes_heap']}")
    print(f"  Tempo              : {(t1 - t0) * 1000:.3f} ms")
    print(f"  Memória            : {pico_mem / 1024:.1f} KB")

    print("\n  Arestas da MST (rota de cobertura mínima):")
    for u, v, peso in resultado_prim["mst_arestas"]:
        nome_u = grafo.vertices[u][1]
        nome_v = grafo.vertices[v][1]
        print(f"    {nome_u:<20} → {nome_v:<20} | {peso:.1f}h")

    print("\n[DIJKSTRA] Caminhos mínimos a partir de Porto Alegre...")
    dijkstra = AlgoritmoDijkstra(grafo)

    tracemalloc.start()
    t0 = time.perf_counter()
    resultado_dijkstra = dijkstra.executar(4314902)
    t1 = time.perf_counter()
    _, pico_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"  Arestas relaxadas  : {resultado_dijkstra['arestas_relaxadas']}")
    print(f"  Inserções no heap  : {resultado_dijkstra['insercoes_heap']}")
    print(f"  Tempo              : {(t1 - t0) * 1000:.3f} ms")
    print(f"  Memória            : {pico_mem / 1024:.1f} KB")

    print("\n  Distâncias mínimas de Porto Alegre:")
    for id_m, custo in sorted(resultado_dijkstra["dist"].items(), key=lambda x: x[1]):
        nome = grafo.vertices[id_m][1]
        caminho = dijkstra.reconstruir_caminho(resultado_dijkstra["predecessor"], id_m)
        nomes = [grafo.vertices[n][1] for n in caminho]
        print(f"    {nome:<20} | {custo:.2f}h | {' → '.join(nomes)}")

    print("\n[BST + DIJKSTRA] Rotas de atendimento prioritário (risco >= 0.65):")
    rotas = rota_atendimento_prioritario(grafo, bst, hub=4314902, limiar_risco=0.65)

    for id_m, info in rotas["rotas"].items():
        nomes = [grafo.vertices[n][1] for n in info["caminho"]]
        print(
            f"  {info['nome']:<20} risco={info['risco']:.2f} | "
            f"custo={info['custo_horas']:.2f}h | {' → '.join(nomes)}"
        )

    print("\n[OK] greedy.py executado com sucesso.")


if __name__ == "__main__":
    main()
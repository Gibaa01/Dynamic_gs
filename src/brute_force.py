import time
import tracemalloc
from itertools import permutations

from data_structures import (
    GrafoMunicipios,
    construir_grafo_rs,
    MUNICIPIOS_RS,
    ARESTAS_RS,
)


class ForcaBruta:
    def __init__(self, grafo: GrafoMunicipios):
        self.grafo = grafo
        self.chamadas_recursivas: int = 0
        self.caminhos_avaliados: int = 0
        self.melhor_custo: float = float("inf")
        self.melhor_caminho: list[int] = []
        self._todos_caminhos: list[tuple[float, list[int]]] = []

    def _resetar(self) -> None:
        self.chamadas_recursivas = 0
        self.caminhos_avaliados = 0
        self.melhor_custo = float("inf")
        self.melhor_caminho = []
        self._todos_caminhos = []

    def _backtrack(
        self,
        atual: int,
        destino: int,
        visitados: set,
        caminho: list,
        custo_acumulado: float,
    ) -> None:
        self.chamadas_recursivas += 1

        if atual == destino:
            self.caminhos_avaliados += 1
            self._todos_caminhos.append((custo_acumulado, list(caminho)))
            if custo_acumulado < self.melhor_custo:
                self.melhor_custo = custo_acumulado
                self.melhor_caminho = list(caminho)
            return

        if custo_acumulado >= self.melhor_custo:
            return

        for vizinho, peso in self.grafo.vizinhos(atual):
            if vizinho not in visitados:
                visitados.add(vizinho)
                caminho.append(vizinho)
                self._backtrack(vizinho, destino, visitados, caminho, custo_acumulado + peso)
                caminho.pop()
                visitados.remove(vizinho)

    def caminho_minimo(self, origem: int, destino: int) -> dict:
        self._resetar()

        visitados: set[int] = {origem}
        caminho: list[int] = [origem]

        self._backtrack(origem, destino, visitados, caminho, 0.0)

        self._todos_caminhos.sort(key=lambda x: x[0])

        return {
            "melhor_caminho": self.melhor_caminho,
            "melhor_custo": self.melhor_custo,
            "caminhos_avaliados": self.caminhos_avaliados,
            "chamadas_recursivas": self.chamadas_recursivas,
            "todos_caminhos": self._todos_caminhos,
        }


def subgrafo_n_nos(grafo_completo: GrafoMunicipios, n: int) -> GrafoMunicipios:
    ids_selecionados = list(grafo_completo.vertices.keys())[:n]
    ids_set = set(ids_selecionados)

    sub = GrafoMunicipios()
    for id_m in ids_selecionados:
        sub.adicionar_vertice(grafo_completo.vertices[id_m])

    for u in ids_selecionados:
        for v, peso in grafo_completo.vizinhos(u):
            if v in ids_set and u < v:
                sub.adicionar_aresta(u, v, peso)

    return sub


def analisar_crescimento(grafo_completo: GrafoMunicipios, tamanhos: list[int]) -> list[dict]:
    ids = list(grafo_completo.vertices.keys())
    resultados = []

    for n in tamanhos:
        if n > len(ids):
            continue

        sub = subgrafo_n_nos(grafo_completo, n)
        origem  = list(sub.vertices.keys())[0]
        destino = list(sub.vertices.keys())[-1]

        if destino == origem:
            continue

        fb = ForcaBruta(sub)

        tracemalloc.start()
        t0 = time.perf_counter()
        resultado = fb.caminho_minimo(origem, destino)
        t1 = time.perf_counter()
        _, pico_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        tempo_ms = (t1 - t0) * 1000
        mem_kb  = pico_mem / 1024

        print(
            f"  N={n:>3} | caminhos={resultado['caminhos_avaliados']:>6} | "
            f"chamadas={resultado['chamadas_recursivas']:>8} | "
            f"tempo={tempo_ms:>8.3f} ms | mem={mem_kb:>6.1f} KB"
        )

        resultados.append({
            "N": n,
            "caminhos_avaliados": resultado["caminhos_avaliados"],
            "chamadas_recursivas": resultado["chamadas_recursivas"],
            "tempo_ms": tempo_ms,
            "mem_kb": mem_kb,
            "melhor_custo": resultado["melhor_custo"],
        })

    return resultados


def main():
    print("=" * 65)
    print("  Global Solution 2026 — Força Bruta")
    print("  Cenário A: Enchentes RS 2024")
    print("=" * 65)

    grafo = construir_grafo_rs()

    POA   = 4314902
    PELOTAS = 4313409

    print(f"\n[FB] Enumerando caminhos: Porto Alegre → Pelotas")
    fb = ForcaBruta(grafo)

    tracemalloc.start()
    t0 = time.perf_counter()
    resultado = fb.caminho_minimo(POA, PELOTAS)
    t1 = time.perf_counter()
    _, pico_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    tempo_ms = (t1 - t0) * 1000
    mem_kb  = pico_mem / 1024

    print(f"  Melhor caminho : {resultado['melhor_caminho']}")
    print(f"  Custo ótimo    : {resultado['melhor_custo']:.2f} horas")
    print(f"  Caminhos avaliados  : {resultado['caminhos_avaliados']}")
    print(f"  Chamadas recursivas : {resultado['chamadas_recursivas']}")
    print(f"  Tempo de execução   : {tempo_ms:.3f} ms")
    print(f"  Memória alocada     : {mem_kb:.1f} KB")

    print("\n  Top-5 caminhos encontrados:")
    for i, (custo, caminho) in enumerate(resultado["todos_caminhos"][:5], 1):
        nomes = [grafo.vertices[id_m][1] for id_m in caminho]
        print(f"    {i}. custo={custo:.2f}h | {' → '.join(nomes)}")

    print("\n[FB] Análise de crescimento do espaço de busca:")
    print(f"  {'N':>3} | {'caminhos':>8} | {'chamadas':>10} | {'tempo(ms)':>10} | {'mem(KB)':>8}")
    print("  " + "-" * 55)

    tamanhos = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    dados_escala = analisar_crescimento(grafo, tamanhos)

    print("\n[FB] Interpretação:")
    print("  A Força Bruta cresce exponencialmente/fatorial com N.")
    print("  Para N ≤ 8 é tolerável; para N > 10 o tempo se torna proibitivo.")
    print("  O ponto de cruzamento com o Guloso será exibido em performance_monitor.py")

    return dados_escala


if __name__ == "__main__":
    main()
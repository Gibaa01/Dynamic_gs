import json
import time
import tracemalloc
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

from data_structures import (
    construir_grafo_rs,
    construir_bst_rs,
    GrafoMunicipios,
    BinarySearchTree,
    Node,
    MUNICIPIOS_RS,
)
from brute_force import ForcaBruta, subgrafo_n_nos
from greedy import AlgoritmoPrim, AlgoritmoDijkstra
from performance_monitor import rodar_comparativo, calcular_gap


PASTA_FIGS = Path(__file__).resolve().parent.parent / "data" / "processed"
PASTA_FIGS.mkdir(parents=True, exist_ok=True)


def figura_grafo_mst(grafo: GrafoMunicipios) -> None:
    prim = AlgoritmoPrim(grafo)
    resultado = prim.executar(list(grafo.vertices.keys())[0])
    mst_set = {(u, v) for u, v, _ in resultado["mst_arestas"]}
    mst_set |= {(v, u) for u, v, _ in resultado["mst_arestas"]}

    G = nx.Graph()
    for id_m, dados in grafo.vertices.items():
        G.add_node(id_m, nome=dados[1], risco=dados[2])

    arestas_mst    = []
    arestas_outras = []
    pesos_mst      = []
    pesos_outras   = []

    for u, vizinhos in grafo.adj.items():
        for v, peso in vizinhos:
            if u < v:
                if (u, v) in mst_set:
                    arestas_mst.append((u, v))
                    pesos_mst.append(f"{peso:.1f}h")
                else:
                    arestas_outras.append((u, v))
                    pesos_outras.append(f"{peso:.1f}h")

    G.add_edges_from(arestas_mst)
    G.add_edges_from(arestas_outras)

    pos = nx.spring_layout(G, seed=42, k=2.5)

    riscos = [grafo.vertices[n][2] for n in G.nodes()]
    cores  = [plt.cm.RdYlGn_r(r) for r in riscos]

    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_facecolor("#f8f9fa")
    fig.patch.set_facecolor("#f8f9fa")

    nx.draw_networkx_edges(G, pos, edgelist=arestas_outras,
                           edge_color="#cccccc", width=1.2, alpha=0.6, ax=ax)
    nx.draw_networkx_edges(G, pos, edgelist=arestas_mst,
                           edge_color="#e63946", width=3.0, ax=ax)
    nx.draw_networkx_nodes(G, pos, node_color=cores, node_size=900,
                           edgecolors="#333333", linewidths=1.2, ax=ax)

    labels = {n: grafo.vertices[n][1].split()[0] for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=7, font_weight="bold", ax=ax)

    edge_labels_mst = {(u, v): f"{p:.1f}h" for (u, v), p in
                       zip(arestas_mst, [w for _, _, w in resultado["mst_arestas"]])}
    nx.draw_networkx_edge_labels(G, pos, edge_labels_mst,
                                 font_size=6.5, font_color="#e63946", ax=ax)

    sm = plt.cm.ScalarMappable(cmap=plt.cm.RdYlGn_r, norm=plt.Normalize(0, 1))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, shrink=0.6, pad=0.02)
    cbar.set_label("Índice de Risco", fontsize=10)

    patch_mst   = mpatches.Patch(color="#e63946", label=f"MST — Prim (custo={resultado['custo_total']:.1f}h)")
    patch_outras = mpatches.Patch(color="#cccccc", label="Demais arestas")
    ax.legend(handles=[patch_mst, patch_outras], loc="upper left", fontsize=9)

    ax.set_title(
        "Figura 1 — Grafo de Municípios do RS com MST (Prim) Destacada\n"
        "Vértices coloridos por índice de risco (verde=baixo, vermelho=alto)",
        fontsize=12, fontweight="bold", pad=15
    )
    ax.axis("off")

    caminho = PASTA_FIGS / "fig1_grafo_mst.png"
    plt.tight_layout()
    plt.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  [Figura 1] Salva em {caminho}")


def _posicionar_bst(no: Node | None, x: float, y: float, dx: float,
                    pos: dict, arestas: list) -> None:
    if no is None:
        return
    pos[id(no)] = (x, y, no)
    if no.esquerda:
        arestas.append((id(no), id(no.esquerda)))
        _posicionar_bst(no.esquerda, x - dx, y - 1.2, dx / 2, pos, arestas)
    if no.direita:
        arestas.append((id(no), id(no.direita)))
        _posicionar_bst(no.direita, x + dx, y - 1.2, dx / 2, pos, arestas)


def figura_bst(bst: BinarySearchTree) -> None:
    pos: dict = {}
    arestas: list = []
    _posicionar_bst(bst.raiz, 0, 0, 3.5, pos, arestas)

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_facecolor("#f8f9fa")
    fig.patch.set_facecolor("#f8f9fa")

    for (id_pai, id_filho) in arestas:
        x1, y1, _ = pos[id_pai]
        x2, y2, _ = pos[id_filho]
        ax.plot([x1, x2], [y1, y2], color="#aaaaaa", linewidth=1.5, zorder=1)

    for key, (x, y, no) in pos.items():
        cor = plt.cm.RdYlGn_r(no.chave)
        circulo = plt.Circle((x, y), 0.45, color=cor, ec="#333333", lw=1.5, zorder=2)
        ax.add_patch(circulo)
        nome_curto = no.dados[1].split()[0][:8]
        ax.text(x, y + 0.12, f"{no.chave:.2f}", ha="center", va="center",
                fontsize=7.5, fontweight="bold", zorder=3)
        ax.text(x, y - 0.18, nome_curto, ha="center", va="center",
                fontsize=6, zorder=3)

    ax.set_xlim(-8, 8)
    ax.set_ylim(-6, 1.5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(
        "Figura 2 — Árvore Binária de Busca (BST) de Municípios por Índice de Risco\n"
        f"Altura={bst.altura()} | Balanceada={bst.esta_balanceada()} | "
        "Chave=índice de risco | Verde=baixo risco, Vermelho=alto risco",
        fontsize=11, fontweight="bold", pad=12
    )

    caminho = PASTA_FIGS / "fig2_bst.png"
    plt.tight_layout()
    plt.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  [Figura 2] Salva em {caminho}")


def figura_tempo_vs_n() -> None:
    tamanhos = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    fb_res, prim_res, dijkstra_res = rodar_comparativo(tamanhos)

    ns_fb   = [r["N"] for r in fb_res]
    ts_fb   = [r["tempo_ms"] for r in fb_res]
    ns_pr   = [r["N"] for r in prim_res]
    ts_pr   = [r["tempo_ms"] for r in prim_res]
    ns_dj   = [r["N"] for r in dijkstra_res]
    ts_dj   = [r["tempo_ms"] for r in dijkstra_res]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_facecolor("#f8f9fa")
    fig.patch.set_facecolor("#f8f9fa")

    ax.plot(ns_fb, ts_fb, "o-", color="#e63946", linewidth=2.5,
            markersize=7, label="Força Bruta (backtracking)")
    ax.plot(ns_pr, ts_pr, "s-", color="#2a9d8f", linewidth=2.5,
            markersize=7, label="Prim — MST (Guloso)")
    ax.plot(ns_dj, ts_dj, "^-", color="#457b9d", linewidth=2.5,
            markersize=7, label="Dijkstra (Guloso)")

    ax.set_xlabel("Número de vértices (N)", fontsize=12)
    ax.set_ylabel("Tempo de execução (ms)", fontsize=12)
    ax.set_title(
        "Figura 3 — Comparativo de Desempenho: Tempo × N\n"
        "Força Bruta vs Algoritmos Gulosos (Prim e Dijkstra)",
        fontsize=12, fontweight="bold"
    )
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.4)
    ax.set_yscale("log")
    ax.annotate(
        "Explosão\ncombinatorial",
        xy=(ns_fb[-1], ts_fb[-1]),
        xytext=(ns_fb[-1] - 2, ts_fb[-1] * 3),
        arrowprops=dict(arrowstyle="->", color="#e63946"),
        color="#e63946", fontsize=9
    )

    caminho = PASTA_FIGS / "fig3_tempo_vs_n.png"
    plt.tight_layout()
    plt.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  [Figura 3] Salva em {caminho}")


def figura_gap_otimalidade() -> None:
    grafo = construir_grafo_rs()
    tamanhos = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    gaps = calcular_gap(grafo, tamanhos)

    ns   = [g["N"] for g in gaps]
    gap_pcts = [g["gap_pct"] for g in gaps]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_facecolor("#f8f9fa")
    fig.patch.set_facecolor("#f8f9fa")

    ax.bar(ns, gap_pcts, color="#457b9d", edgecolor="#333333", linewidth=0.8, alpha=0.85)
    ax.axhline(0, color="#333333", linewidth=1)

    for n, g in zip(ns, gap_pcts):
        ax.text(n, g + 0.5, f"{g:.1f}%", ha="center", va="bottom", fontsize=8)

    ax.set_xlabel("Número de vértices (N)", fontsize=12)
    ax.set_ylabel("Gap de otimalidade (%)", fontsize=12)
    ax.set_title(
        "Figura 4 — Gap de Otimalidade: Diferença % entre Força Bruta e Prim\n"
        "Gap = |custo_Prim − custo_FB| / custo_FB × 100%",
        fontsize=12, fontweight="bold"
    )
    ax.grid(True, axis="y", alpha=0.4)

    caminho = PASTA_FIGS / "fig4_gap_otimalidade.png"
    plt.tight_layout()
    plt.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  [Figura 4] Salva em {caminho}")


def main():
    print("=" * 65)
    print("  Global Solution 2026 — Visualizações")
    print("  Cenário A: Enchentes RS 2024")
    print("=" * 65)

    grafo = construir_grafo_rs()
    bst   = construir_bst_rs(grafo)

    print("\n[1] Gerando figura do grafo com MST...")
    figura_grafo_mst(grafo)

    print("\n[2] Gerando figura da BST...")
    figura_bst(bst)

    print("\n[3] Gerando gráfico tempo × N...")
    figura_tempo_vs_n()

    print("\n[4] Gerando gráfico de gap de otimalidade...")
    figura_gap_otimalidade()

    print(f"\n[OK] Todas as figuras salvas em: {PASTA_FIGS}")


if __name__ == "__main__":
    main()
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from data_structures import (
    GrafoMunicipios,
    BinarySearchTree,
    FilaPrioridade,
    construir_grafo_rs,
    construir_bst_rs,
    MUNICIPIOS_RS,
)
from brute_force import ForcaBruta, subgrafo_n_nos


@pytest.fixture
def grafo_rs():
    return construir_grafo_rs()


@pytest.fixture
def bst_rs(grafo_rs):
    return construir_bst_rs(grafo_rs)


@pytest.fixture
def grafo_simples():
    g = GrafoMunicipios()
    g.adicionar_vertice((1, "A", 0.1, 100.0, 1000))
    g.adicionar_vertice((2, "B", 0.5, 200.0, 2000))
    g.adicionar_vertice((3, "C", 0.3, 150.0, 1500))
    g.adicionar_vertice((4, "D", 0.8, 300.0, 3000))
    g.adicionar_aresta(1, 2, 1.0)
    g.adicionar_aresta(1, 3, 2.0)
    g.adicionar_aresta(2, 4, 1.5)
    g.adicionar_aresta(3, 4, 0.5)
    return g


class TestGrafo:

    def test_numero_vertices(self, grafo_rs):
        assert len(grafo_rs.vertices) == len(MUNICIPIOS_RS)

    def test_numero_arestas(self, grafo_rs):
        total_arestas = sum(len(v) for v in grafo_rs.adj.values()) // 2
        assert total_arestas == 15

    def test_vizinhos_poa(self, grafo_rs):
        vizinhos_ids = [v for v, _ in grafo_rs.vizinhos(4314902)]
        assert 4300406 in vizinhos_ids
        assert 4316808 in vizinhos_ids
        assert 4303103 in vizinhos_ids
        assert 4313409 in vizinhos_ids

    def test_bfs_alcanca_todos(self, grafo_rs):
        bfs = grafo_rs.bfs(4314902)
        assert len(bfs) == len(MUNICIPIOS_RS)

    def test_dfs_alcanca_todos(self, grafo_rs):
        dfs = grafo_rs.dfs(4314902)
        assert len(dfs) == len(MUNICIPIOS_RS)

    def test_grafo_simples_vizinhos(self, grafo_simples):
        viz_1 = [v for v, _ in grafo_simples.vizinhos(1)]
        assert 2 in viz_1 and 3 in viz_1

    def test_bidireccional(self, grafo_simples):
        viz_4 = [v for v, _ in grafo_simples.vizinhos(4)]
        assert 2 in viz_4 and 3 in viz_4


class TestBST:

    def test_in_order_crescente(self, bst_rs):
        municipios = bst_rs.percurso_in_order()
        riscos = [m[2] for m in municipios]
        assert riscos == sorted(riscos)

    def test_busca_intervalo(self, bst_rs):
        resultado = bst_rs.buscar_intervalo(0.60, 0.80)
        for m in resultado:
            assert 0.60 <= m[2] <= 0.80

    def test_busca_intervalo_vazio(self, bst_rs):
        resultado = bst_rs.buscar_intervalo(0.95, 1.00)
        assert resultado == []

    def test_altura_positiva(self, bst_rs):
        assert bst_rs.altura() > 0

    def test_insercao_e_remocao(self):
        bst = BinarySearchTree()
        m1 = (1, "X", 0.3, 100.0, 1000)
        m2 = (2, "Y", 0.1, 200.0, 2000)
        m3 = (3, "Z", 0.5, 300.0, 3000)
        bst.inserir(m1)
        bst.inserir(m2)
        bst.inserir(m3)
        assert len(bst.percurso_in_order()) == 3

        bst.remover(2)
        ordem = bst.percurso_in_order()
        assert len(ordem) == 2
        ids = [m[0] for m in ordem]
        assert 2 not in ids

    def test_propriedade_bst(self, bst_rs):
        def verificar(no):
            if no is None:
                return True
            if no.esquerda and no.esquerda.chave >= no.chave:
                return False
            if no.direita and no.direita.chave < no.chave:
                return False
            return verificar(no.esquerda) and verificar(no.direita)

        assert verificar(bst_rs.raiz)

    def test_bst_vazia(self):
        bst = BinarySearchTree()
        assert bst.percurso_in_order() == []
        assert bst.altura() == 0
        assert bst.buscar_intervalo(0.0, 1.0) == []


class TestFilaPrioridade:

    def test_min_heap(self):
        fp = FilaPrioridade()
        fp.inserir(3.0, 1)
        fp.inserir(1.0, 2)
        fp.inserir(2.0, 3)

        custo1, _ = fp.extrair_min()
        custo2, _ = fp.extrair_min()
        custo3, _ = fp.extrair_min()

        assert custo1 <= custo2 <= custo3

    def test_vazia(self):
        fp = FilaPrioridade()
        assert fp.vazia()
        fp.inserir(1.0, 1)
        assert not fp.vazia()


class TestForcaBruta:

    def test_caminho_encontrado(self, grafo_simples):
        fb = ForcaBruta(grafo_simples)
        resultado = fb.caminho_minimo(1, 4)
        assert resultado["melhor_caminho"] is not None
        assert resultado["melhor_caminho"][0] == 1
        assert resultado["melhor_caminho"][-1] == 4

    def test_custo_otimo_grafo_simples(self, grafo_simples):
        fb = ForcaBruta(grafo_simples)
        resultado = fb.caminho_minimo(1, 4)
        assert abs(resultado["melhor_custo"] - 2.5) < 1e-6

    def test_instrumentacao(self, grafo_simples):
        fb = ForcaBruta(grafo_simples)
        resultado = fb.caminho_minimo(1, 4)
        assert resultado["chamadas_recursivas"] > 0
        assert resultado["caminhos_avaliados"] > 0

    def test_todos_caminhos_ordenados(self, grafo_simples):
        fb = ForcaBruta(grafo_simples)
        resultado = fb.caminho_minimo(1, 4)
        custos = [c for c, _ in resultado["todos_caminhos"]]
        assert custos == sorted(custos)

    def test_subgrafo_n_nos(self, grafo_rs):
        sub = subgrafo_n_nos(grafo_rs, 5)
        assert len(sub.vertices) == 5

    def test_fb_grafo_rs_pequeno(self, grafo_rs):
        sub = subgrafo_n_nos(grafo_rs, 6)
        ids = list(sub.vertices.keys())
        fb = ForcaBruta(sub)
        resultado = fb.caminho_minimo(ids[0], ids[-1])
        assert isinstance(resultado["melhor_custo"], float)

    def test_origem_igual_destino(self, grafo_simples):
        fb = ForcaBruta(grafo_simples)
        resultado = fb.caminho_minimo(1, 1)
        assert resultado["caminhos_avaliados"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from greedy import AlgoritmoPrim, AlgoritmoDijkstra


class TestPrim:

    def test_mst_n_menos_1_arestas(self, grafo_rs):
        prim = AlgoritmoPrim(grafo_rs)
        resultado = prim.executar(4314902)
        assert len(resultado["mst_arestas"]) == len(grafo_rs.vertices) - 1

    def test_mst_custo_positivo(self, grafo_rs):
        prim = AlgoritmoPrim(grafo_rs)
        resultado = prim.executar(4314902)
        assert resultado["custo_total"] > 0

    def test_mst_instrumentacao(self, grafo_rs):
        prim = AlgoritmoPrim(grafo_rs)
        resultado = prim.executar(4314902)
        assert resultado["insercoes_heap"] > 0
        assert resultado["extracoes_heap"] > 0

    def test_prim_grafo_simples(self, grafo_simples):
        prim = AlgoritmoPrim(grafo_simples)
        resultado = prim.executar(1)
        assert len(resultado["mst_arestas"]) == len(grafo_simples.vertices) - 1
        assert resultado["custo_total"] > 0


class TestDijkstra:

    def test_distancia_origem_zero(self, grafo_rs):
        dijkstra = AlgoritmoDijkstra(grafo_rs)
        resultado = dijkstra.executar(4314902)
        assert resultado["dist"][4314902] == 0.0

    def test_distancias_nao_negativas(self, grafo_rs):
        dijkstra = AlgoritmoDijkstra(grafo_rs)
        resultado = dijkstra.executar(4314902)
        for d in resultado["dist"].values():
            assert d >= 0

    def test_caminho_reconstruido(self, grafo_rs):
        dijkstra = AlgoritmoDijkstra(grafo_rs)
        resultado = dijkstra.executar(4314902)
        caminho = dijkstra.reconstruir_caminho(resultado["predecessor"], 4313409)
        assert caminho[0] == 4314902
        assert caminho[-1] == 4313409

    def test_dijkstra_grafo_simples(self, grafo_simples):
        dijkstra = AlgoritmoDijkstra(grafo_simples)
        resultado = dijkstra.executar(1)
        assert abs(resultado["dist"][4] - 2.5) < 1e-6

    def test_todos_alcancados(self, grafo_rs):
        dijkstra = AlgoritmoDijkstra(grafo_rs)
        resultado = dijkstra.executar(4314902)
        for d in resultado["dist"].values():
            assert d < float("inf")

    def test_arestas_relaxadas(self, grafo_rs):
        dijkstra = AlgoritmoDijkstra(grafo_rs)
        resultado = dijkstra.executar(4314902)
        assert resultado["arestas_relaxadas"] > 0
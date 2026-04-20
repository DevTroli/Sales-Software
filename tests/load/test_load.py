#!/usr/bin/env python3
"""
Script de teste de carga para o sistema de PDV
Simula usuários simultâneos acessando diferentes partes do sistema

Para executar:
    uv run locust -f test_load.py --host=http://localhost:8000

Ou com parâmetros específicos:
    uv run locust -f test_load.py --host=http://localhost:8000 --users 20 --spawn-rate 2 --run-time 5m
"""

import random
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner

class PDVUser(HttpUser):
    """
    Simula um usuário do sistema PDV
    Distribuição de tarefas baseada em uso real:
    - Busca de produtos: mais frequente (40%)
    - Listagem de produtos: frequente (25%)
    - Acesso ao PDV: frequente (20%)
    - Comandas: ocasional (10%)
    - Outras operações: menos frequentes (5%)
    """

    wait_time = between(1, 5)  # Tempo de espera entre requisições (1-5 segundos)

    def on_start(self):
        """Método executado quando um usuário de teste inicia"""
        self.client.get("/")

    @task(4)
    def search_products(self):
        """Simula busca de produtos - tarefa mais frequente"""
        search_terms = [
            "coca", "guarana", "refrigerante", "agua", "suco",
            "cerveja", "vinho", "whisky", "vodka", "energetico",
            "original", "lata", "litro", "600", "269",
            "kit", "pack", "unidade", "caixa", "unid",
        ]
        term = random.choice(search_terms)
        with self.client.get(f"/produtos/?q={term}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Busca falhou com status {response.status_code}")

    @task(3)
    def access_product_list(self):
        """Acessa a lista de produtos"""
        page = random.randint(1, 5)  # Páginas 1-5
        with self.client.get(f"/produtos/?page={page}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Listagem falhou com status {response.status_code}")

    @task(2)
    def access_pdv(self):
        """Acessa o ponto de venda"""
        with self.client.get("/pdv/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Acesso ao PDV falhou com status {response.status_code}")

    @task(1)
    def list_tabs(self):
        """Lista comandas"""
        with self.client.get("/comandas/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Listagem de comandas falhou com status {response.status_code}")

    @task(1)
    def view_product_detail(self):
        """Visualiza detalhes de um produto aleatório"""
        product_id = random.randint(1, 100)  # IDs de produtos
        with self.client.get(f"/produtos/{product_id}/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                response.success()  # 404 é esperado se o produto não existe
            else:
                response.failure(f"Detalhe do produto falhou com status {response.status_code}")

    @task(1)
    def view_homepage(self):
        """Acessa a página inicial"""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Homepage falhou com status {response.status_code}")


class PDVHeavyUser(HttpUser):
    """
    Simula um usuário intensivo do sistema (funcionário experiente)
    Faz mais operações e tem menos tempo de espera
    """

    wait_time = between(0.5, 2)  # Tempo de espera menor (0.5-2 segundos)

    @task(10)
    def rapid_search(self):
        """Busca rápida de produtos - simula busca contínua"""
        search_terms = ["coca", "guarana", "agua", "cerveja", "original"]
        term = random.choice(search_terms)
        self.client.get(f"/produtos/?q={term}")

    @task(5)
    def access_pdv(self):
        """Acesso constante ao PDV"""
        self.client.get("/pdv/")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento chamado quando o teste para"""
    print("\n" + "=" * 60)
    print("TESTE DE CARGA CONCLUÍDO")
    print("=" * 60)
    if hasattr(environment, 'stats'):
        stats = environment.stats
        print(f"\nTotal de requisições: {stats.total.num_requests}")
        print(f"Falhas: {stats.total.num_failures}")
        print(f"Tempo médio de resposta: {stats.total.avg_response_time:.2f}ms")
        print(f"Tempo mínimo: {stats.total.min_response_time:.2f}ms")
        print(f"Tempo máximo: {stats.total.max_response_time:.2f}ms")
        print(f"Requisições por segundo: {stats.total.total_rps:.2f}")
    print("=" * 60)


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response,
               context, exception, **kwargs):
    """Log para cada requisição"""
    if exception:
        print(f"[ERRO] {request_type} {name}: {exception}")

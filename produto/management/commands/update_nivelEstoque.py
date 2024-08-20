from django.core.management.base import BaseCommand
from produto.models import Produto


class Command(BaseCommand):
    help = (
        "Atualiza o nível de estoque de todos os produtos existentes no banco de dados."
    )

    def handle(self, *args, **kwargs):
        produtos = Produto.objects.all()
        total_produtos = produtos.count()
        self.stdout.write(
            self.style.NOTICE(
                f"Atualizando o nível de estoque para {total_produtos} produtos..."
            )
        )

        atualizados = 0
        for produto in produtos:
            # Aplica a lógica de atualização do nível de estoque
            if produto.estoque >= produto.estoque_minimo and produto.estoque > 0:
                produto.nivel_estoque = True
            else:
                produto.nivel_estoque = False

            # Salva o produto com o nível de estoque atualizado
            produto.save()
            atualizados += 1
            self.stdout.write(self.style.SUCCESS(f"Atualizado: {produto.produto}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Atualização concluída! {atualizados} produtos atualizados."
            )
        )

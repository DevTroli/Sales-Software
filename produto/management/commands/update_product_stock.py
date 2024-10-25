from django.core.management.base import BaseCommand
from produto.models import Produto


class Command(BaseCommand):
    help = "Updates the stock (estoque) to 1000 and minimum stock (estoque_minimo) to 1 for all products."

    def handle(self, *args, **kwargs):
        produtos = Produto.objects.all()
        total_produtos = produtos.count()
        self.stdout.write(
            self.style.NOTICE(f"Updating stock for {total_produtos} products...")
        )

        updated = 0
        for produto in produtos:
            produto.estoque = 1000
            produto.estoque_minimo = 1
            produto.save()
            updated += 1
            self.stdout.write(self.style.SUCCESS(f"Updated: {produto.produto}"))

        self.stdout.write(
            self.style.SUCCESS(f"Update completed! {updated} products updated.")
        )

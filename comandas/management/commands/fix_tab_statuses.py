from django.core.management.base import BaseCommand
from django.db.models import Count
from comandas.models import Tab

class Command(BaseCommand):
    help = 'Corrige o status de todas as comandas abertas com base no seu conteúdo.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Iniciando a correção dos status das comandas...'))

        tabs_para_verificar = Tab.objects.filter(aberta=True).annotate(num_itens=Count('itens'))

        corrigidas = 0
        for tab in tabs_para_verificar:
            novo_status = 'ATIVA' if tab.num_itens > 0 else 'VAZIA'

            if tab.status != novo_status:
                tab.status = novo_status
                tab.save(update_fields=['status'])
                corrigidas += 1
                self.stdout.write(f'Comanda "{tab.nome_cliente}" (ID: {tab.id}) corrigida para {novo_status}.')

        self.stdout.write(self.style.SUCCESS(f'Operação concluída! {corrigidas} comandas foram corrigidas.'))
document.addEventListener('DOMContentLoaded', function () {
    const dropdownToggle = document.querySelector('[data-dropdown-toggle="dropdownNavbar"]');
    const dropdownMenu = document.getElementById('dropdownNavbar');

    if (dropdownToggle) {
        dropdownToggle.addEventListener('click', function (event) {
            dropdownMenu.classList.toggle('hidden');
            event.stopPropagation();
        });
    }

    const navbarToggle = document.getElementById('navbar-toggle');
    const navbarDropdown = document.getElementById('navbar-dropdown');

    if (navbarToggle && navbarDropdown) {
        navbarToggle.addEventListener('click', function (event) {
            navbarDropdown.classList.toggle('hidden');
            event.stopPropagation();
        });
    }

    document.addEventListener('click', function (event) {
        if (navbarToggle && !navbarToggle.contains(event.target) && !navbarDropdown.contains(event.target)) {
            navbarDropdown.classList.add('hidden');
        }
        if (dropdownToggle && !dropdownToggle.contains(event.target) && !dropdownMenu.contains(event.target)) {
            dropdownMenu.classList.add('hidden');
        }
    });
});

// Seleciona o campo "Código de Barra" após o carregamento da página
    document.addEventListener('DOMContentLoaded', function() {
        const codigoBarraInput = document.querySelector('input[name="codigo_barra"]');
        if (codigoBarraInput) {
            codigoBarraInput.focus();
        }
    });

    
    document.addEventListener("DOMContentLoaded", function() {
        // Modal de Cálculo
        const openCalcModalBtn = document.getElementById("openCalcModal");
        const calcModal = document.getElementById("calcModal");
        const closeCalcModalBtn = document.getElementById("closeCalcModal");
    
        if (openCalcModalBtn && calcModal && closeCalcModalBtn) {
            openCalcModalBtn.addEventListener("click", function() {
                calcModal.classList.remove("hidden");
            });
    
            closeCalcModalBtn.addEventListener("click", function() {
                calcModal.classList.add("hidden");
            });
        }
    
        // Cálculo do troco em tempo real
        const valorEntregueInput = document.getElementById("valorEntregue");
        const valorTrocoInput = document.getElementById("valorTroco");
        const valorCompraInput = document.getElementById("valorCompra");
    
        function atualizarTroco() {
            // Converte os valores para números multiplicados por 100 para evitar problemas com decimais
            const valorCompra = Math.round(parseFloat(valorCompraInput.value || 0) * 100);
            const valorEntregue = Math.round(parseFloat(valorEntregueInput.value || 0) * 100);
            
            // Calcula o troco também multiplicado por 100
            const troco = valorEntregue - valorCompra;
            
            // Converte de volta dividindo por 100 e formata com 2 casas decimais
            if (!isNaN(troco)) {
                // Usa (troco / 100).toFixed(2) para garantir exatidão
                valorTrocoInput.value = (troco / 100).toFixed(2);
            } else {
                valorTrocoInput.value = "0.00";
            }
        }
    
        if (valorCompraInput && valorEntregueInput) {
            valorCompraInput.addEventListener("input", atualizarTroco);
            valorEntregueInput.addEventListener("input", atualizarTroco);
            valorCompraInput.addEventListener("keyup", atualizarTroco);
            valorEntregueInput.addEventListener("keyup", atualizarTroco);
            valorCompraInput.addEventListener("blur", atualizarTroco);
            valorEntregueInput.addEventListener("blur", atualizarTroco);
        }
    
        // Executa o cálculo inicial
        atualizarTroco();
        console.log("Script de cálculo de troco atualizado - versão sem arredondamento!");
    });
    
    
    
    document.addEventListener('DOMContentLoaded', function () {
        const metodoPagamentoSelect = document.querySelector('select[name="metodo_pagamento"]');
        const calcButton = document.getElementById('openCalcModal');

        // Função para verificar o método de pagamento e mostrar/ocultar o botão de cálculo
        function toggleCalcButton() {
            if (metodoPagamentoSelect.value === 'DINHEIRO') {
                calcButton.style.display = 'inline-block';
            } else {
                calcButton.style.display = 'none';
            }
        }

        // Inicializa o estado do botão quando a página é carregada
        toggleCalcButton();

        // Verifica quando o método de pagamento é alterado
        metodoPagamentoSelect.addEventListener('change', toggleCalcButton);

        // Função para abrir o modal e definir o valor do subtotal
        function openModalAndSetValue() {

            // Mostre o modal
            document.getElementById('calcModal').classList.remove('hidden');
        }

        // Função para fechar o modal
        document.getElementById('closeCalcModal').addEventListener('click', function() {
            document.getElementById('calcModal').classList.add('hidden');
        });

        // Associa a função openModalAndSetValue ao clique no botão de cálculo
        calcButton.addEventListener('click', openModalAndSetValue);
    });
    document.addEventListener('DOMContentLoaded', function() {
            const fecharVendaBtn = document.getElementById('fecharVendaBtn');
            const subtotalElem = document.getElementById('subtotal');
            const metodoPagamentoElem = document.getElementById('id_metodo_pagamento'); // Pega o campo de método de pagamento pelo id gerado automaticamente
            
            // Função para verificar as condições e habilitar/desabilitar o botão
            function verificarCondicoes() {
                const subtotal = parseFloat(subtotalElem.textContent.replace('R$', '').trim());
                const metodoPagamentoSelecionado = metodoPagamentoElem.value;
                
                // Habilita o botão se houver itens, o subtotal for maior que 0 e um método de pagamento estiver selecionado
                if (subtotal > 0 && metodoPagamentoSelecionado) {
                    fecharVendaBtn.disabled = false;
                    fecharVendaBtn.classList.remove('bg-gray-500');
                    fecharVendaBtn.classList.add('bg-amber-500');
                } else {
                    fecharVendaBtn.disabled = true;
                    fecharVendaBtn.classList.remove('bg-amber-500');
                    fecharVendaBtn.classList.add('bg-gray-500');
                }
            }
    
            // Executa a validação ao carregar a página
            verificarCondicoes();
    
            // Verifica quando o método de pagamento é alterado
            metodoPagamentoElem.addEventListener('change', verificarCondicoes);
        });
  
    document.addEventListener("DOMContentLoaded", function () {
        const subtotalElement = document.querySelector("p strong:contains('Subtotal:')");
        const fecharTabButton = document.querySelector(".btn");
    
        function verificarSubtotal() {
            const subtotal = parseFloat(subtotalElement.textContent.replace('R$', '').trim());
            if (subtotal > 0) {
                fecharTabButton.classList.remove("opacity-50", "pointer-events-none");
            } else {
                fecharTabButton.classList.add("opacity-50", "pointer-events-none");
            }
        }
    
        // Chama a função para verificar o subtotal quando a página carrega
        verificarSubtotal();
    
        // Você pode monitorar atualizações na página com um MutationObserver, se necessário,
        // ou chamar a função após a adição de itens.
    });

    // Script para remover automaticamente as mensagens após 3 segundos
    document.addEventListener("DOMContentLoaded", function () {
        const messages = document.querySelectorAll('.django-message'); // Seleciona apenas as mensagens de alerta                    
        messages.forEach((message) => {
        // Define um temporizador de 5 segundos para cada mensagem
        setTimeout(() => {
        message.style.opacity = '0';  // Reduz a opacidade para 0
        setTimeout(() => {
        message.style.display = 'none';  // Remove o alerta após a transição
          }, 500); // Aguarda a transição de 0.5 segundos antes de remover o alerta
        }, 5000); // 3 segundos antes de iniciar a transição de saída
    });
});
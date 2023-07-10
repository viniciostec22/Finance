from django.http import HttpResponse
from django.shortcuts import redirect, render
from perfil.models import Categoria
from .models import ContaPagar, ContaPaga
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime

# Create your views here.
def definir_contas(request):
    if request.method == 'GET':
        categorias = Categoria.objects.all()
        return render(request, 'definir_contas.html',{'categorias':categorias})
    else:
        titulo = request.POST.get('titulo')
        categoria = request.POST.get('categoria')
        descricao = request.POST.get('descricao')
        valor = request.POST.get('valor')
        dia_pagamento = request.POST.get('dia_pagamento')
        
        conta = ContaPagar(
            titulo = titulo,
            categoria_id = categoria,
            descricao = descricao,
            valor = valor,
            dia_pagamento = dia_pagamento           
        )
        
        conta.save()
        messages.add_message(request, constants.SUCCESS, 'Conta Cadastrada com Sucesso')
        return redirect('/contas/definir_contas')
    
def ver_contas(request):
    MES_ATUAL = datetime.now().month
    DIA_ATUAL = datetime.now().day
    
    contas = ContaPagar.objects.all()
    
    contas_pagas = ContaPaga.objects.filter(data_pagamento__month = MES_ATUAL).values('conta')
    contas_vencidas = contas.filter(dia_pagamento__lt=DIA_ATUAL).exclude(id__in = contas_pagas)
    contas_proximas_vencimento = contas.filter(dia_pagamento__lte = DIA_ATUAL + 5).filter(dia_pagamento__gt = DIA_ATUAL).exclude(id__in = contas_pagas)
    restantes = contas.exclude(id__in=contas_vencidas).exclude(id__in=contas_proximas_vencimento).exclude(id__in = contas_pagas)
    return render(request, 'ver_contas.html', {
        'contas_vencidas': contas_vencidas,
        'contas_proximas_vencimento': contas_proximas_vencimento,
        'restantes': restantes,
        'total_contas_vencidas': contas_vencidas.count(),
        'total_contas_proximas_vencimento': contas_proximas_vencimento.count(),
        'total_restantes': restantes.count()
    })


def pagar_conta(request, conta_id):
    conta = ContaPagar.objects.get(id=conta_id)
    # Aqui você pode adicionar a lógica de processamento do pagamento
    
    # Exemplo: definindo a data de pagamento como a data atual
    data_pagamento = datetime.now().date()
    
    # Criando um objeto ContaPaga com a conta e a data de pagamento
    conta_paga = ContaPaga(
        conta=conta, 
        data_pagamento=data_pagamento
    )
    conta_paga.save()
    
    # Redirecionando de volta para a página de visualização das contas
    messages.add_message(request, constants.SUCCESS, 'Conta paga com Sucesso')
    return redirect('ver_contas')

    
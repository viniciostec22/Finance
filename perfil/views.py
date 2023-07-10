from django.shortcuts import render, redirect
from . models import *
from django.contrib import messages
from django.contrib.messages import constants
from .utils import calcula_total, calcula_equilibriu_financeiro
from extrato.models import Valores
from datetime import datetime
from contas.models import ContaPagar, ContaPaga

def home(request):
    MES_ATUAL = datetime.now().month
    DIA_ATUAL = datetime.now().day
    
    contas = ContaPagar.objects.all()
    contas_pagas = ContaPaga.objects.filter(data_pagamento__month = MES_ATUAL).values('conta')
    contas_vencidas = contas.filter(dia_pagamento__lt=DIA_ATUAL).exclude(id__in = contas_pagas)
    contas_proximas_vencimento = contas.filter(dia_pagamento__lte = DIA_ATUAL + 5).filter(dia_pagamento__gt = DIA_ATUAL).exclude(id__in = contas_pagas)
    restantes = contas.exclude(id__in=contas_vencidas).exclude(id__in=contas_proximas_vencimento).exclude(id__in = contas_pagas)
    
    
    valores = Valores.objects.filter(data__month=datetime.now().month)
    entradas = valores.filter(tipo = 'E')
    saidas = valores.filter(tipo = 'S')
    total_entradas = calcula_total(entradas, 'valor')
    total_saidas = calcula_total(saidas, 'valor')
    contas = Conta.objects.all()
    total_contas = calcula_total(contas, 'valor')
    percentual_gastos_essenciais, percentual_gastos_nao_essenciais = calcula_equilibriu_financeiro()
    total_livre = total_entradas - total_saidas
    return render(request, 'home.html', {'contas':contas, 
                                         'total_contas':total_contas, 
                                         'total_entradas':total_entradas,
                                         'total_saidas':total_saidas,
                                         'percentual_gastos_essenciais':int(percentual_gastos_essenciais),
                                         'percentual_gastos_nao_essenciais':int(percentual_gastos_nao_essenciais),
                                         'total_contas_vencidas': contas_vencidas.count(),
                                         'total_contas_proximas_vencimento': contas_proximas_vencimento.count(),
                                         'total_restantes': restantes.count(),
                                         'total_livre':total_livre
                                         })

def gerenciar(request):
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()
    total_contas = 0
    total_contas = calcula_total(contas, 'valor')
    return render(request, 'gerenciar.html', {'contas':contas, 'total_contas':total_contas, 'categorias':categorias})

def cadastrar_banco(request):
    apelido = request.POST.get('apelido')
    banco = request.POST.get('banco')
    tipo = request.POST.get('tipo')
    valor = request.POST.get('valor')
    icone = request.FILES.get('icone')
    
    if len(apelido.strip()) == 0 or len(valor.strip()) == 0:
        messages.add_message(request, constants.WARNING, 'Preencha todos os campos')
        return redirect('/perfil/gerenciar/')
    
    #TODO: Realizar validação
    
    conta = Conta(
        apelido = apelido,
        banco=banco,
        tipo=tipo,
        valor=valor,
        icone=icone
    )

    conta.save()
    messages.add_message(request, constants.SUCCESS, 'Conta cadastrada com sucesso')
    return redirect('/perfil/gerenciar/')

def deletar_banco(request, id):
    conta = Conta.objects.get(id=id)
    conta.delete()
    
    messages.add_message(request, constants.SUCCESS, 'Conta removida com sucesso')
    return redirect('/perfil/gerenciar/')

def cadastrar_categoria(request):
    nome = request.POST.get('categoria')
    essencial = bool(request.POST.get('essencial'))
    #TODO: Realizar validação
    categoria = Categoria(
        categoria=nome,
        essencial=essencial
    )

    categoria.save()

    messages.add_message(request, constants.SUCCESS, 'Categoria cadastrada com sucesso')
    return redirect('/perfil/gerenciar/')

def update_categoria(request, id):
    categoria = Categoria.objects.get(id=id)
    categoria.essencial = not categoria.essencial
    categoria.save()

    return redirect('/perfil/gerenciar/')

def dashboard(request):
    dados = {}
    categorias = Categoria.objects.all()
    for categoria in categorias:
        total = 0
        valores = Valores.objects.filter(categoria = categoria)
        for v in valores:
            total += v.valor
        dados[categoria.categoria] = total
    print(dados)
    return render(request,'dashboard.html',
                  {'labels':list(dados.keys()),
                   'values':list(dados.values())})

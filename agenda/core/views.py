from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from core.models import Evento
from datetime import datetime
from django.http import Http404, JsonResponse, HttpResponse
# Create your views here.

def login_user(request):
    return render(request, 'core/login.html')

def logout_user(request):
    logout(request)
    return redirect('/')

def submit_login(request):
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        usuario = authenticate(username=username, password=password)
        if usuario is not None:
            login(request, usuario)
            return redirect('/')
        else:
            messages.error(request, "Usuário ou senha invalidos.")
    return redirect('/')

@login_required(login_url='/login/')
def lista_eventos(request):
    usuario = request.user
    data_atual = datetime.now()
    opcao = request.POST.get('filtro')
    visualizacao = opcao
    evento = Evento.objects.filter(usuario=usuario)
    if opcao == 'todos os eventos':
        evento = Evento.objects.filter(usuario=usuario)
    if opcao == 'eventos vencidos':
        evento = Evento.objects.filter(usuario=usuario, data_evento__lt=data_atual)
    if opcao == 'eventos a vencer':
        evento = Evento.objects.filter(usuario=usuario, data_evento__gt=data_atual)
    dados = {'eventos': evento, 
            'opcao': ['', 'todos os eventos', 'eventos vencidos', 'eventos a vencer'],
            'visualizacao': visualizacao
            }
    return render(request, 'core/agenda.html', dados)

@login_required(login_url='/login/')
def evento(request):
    id_evento = request.GET.get('id')
    dados = {}
    if id_evento:
        dados['evento'] = Evento.objects.get(id=id_evento)
    return render(request, 'core/evento.html', dados)

@login_required(login_url='/login/')
def submit_evento(request):
    if request.POST:
        id_evento = request.POST.get('id_evento')
        titulo = request.POST.get('titulo')
        data_evento = request.POST.get('data_evento')
        descricao = request.POST.get('descricao')
        local = request.POST.get('local')
        usuario = request.user
        if id_evento:
            evento = Evento.objects.get(id=id_evento)
            if evento.usuario == usuario:
                Evento.objects.filter(id=id_evento).update(
                    titulo=titulo,
                    data_evento=data_evento,
                    descricao=descricao,
                    local=local
                )
        else:
            Evento.objects.create(
                titulo=titulo,
                data_evento=data_evento,
                descricao=descricao,
                local=local,
                usuario=usuario
            )
    return redirect('/')

@login_required(login_url='/login/')
def delete_evento(request, id_evento):
    usuario = request.user
    try:
        evento = Evento.objects.get(id=id_evento)
    except Exception:
        raise Http404()
    if usuario == evento.usuario:
        evento.delete()
    else:
        raise Http404()
    return redirect('/')

def json_lista_evento(request, user_name):
    try:
        usuario = User.objects.get(username=user_name)
        evento = Evento.objects.filter(usuario=usuario).values('id', 'titulo')
        return JsonResponse(list(evento), safe=False)
    except:
        return HttpResponse('Usuário não existe')
    
def lista(request):
    return HttpResponse('Coloque o nome do usuário no endereço como o exemplo: ...agenda/lista/nome do usuario aqui')
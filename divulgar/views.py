from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from .models import Tag, Raca, Pet
from django.contrib import messages
from django.contrib.messages import constants
from adotar.models import PedidoAdocao
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@login_required
def novo_pet(request):
    if request.method == 'GET':
        tags = Tag.objects.all()
        racas = Raca.objects.all()
        return render(request, 'novo_pet.html', {'tags':tags, 'racas':racas})
    elif request.method == 'POST':
        foto = request.FILES.get('foto')
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        estado = request.POST.get('estado')
        cidade = request.POST.get('cidade')
        telefone = request.POST.get('telefone')
        tags = request.POST.getlist('tags')
        raca = request.POST.get('raca')
        if nome.strip() == 0 or descricao.strip() == 0 or estado.strip() == 0 or cidade.strip() == 0 or telefone.strip() == 0:
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos!')
            return render(request, 'novo_pet.html')
        else:
            pet = Pet(
                usuario=request.user,
                foto=foto,
                nome=nome,
                descricao=descricao,
                estado=estado,
                cidade=cidade,
                telefone=telefone,
                raca_id=raca,
            )
            pet.save()
            for tag_id in tags:
                tag = Tag.objects.get(id=tag_id)
                pet.tags.add(tag)
            pet.save()
            return redirect('/divulgar/seus_pets')

@login_required
def seus_pets(request):
    if request.method == "GET":
        pets = Pet.objects.filter(usuario=request.user)
        return render(request, 'seus_pets.html', {'pets': pets})

@login_required
def remover_pet(request, id):
    pet = Pet.objects.get(id=id)
    if not pet.usuario == request.user:
        messages.add_message(request, constants.ERROR, 'Esse pet n??o ?? seu!')
        return redirect('/divulgar/seus_pets')


    pet.delete()
    messages.add_message(request, constants.SUCCESS, 'Removido com sucesso.')
    return redirect('/divulgar/seus_pets')

@login_required
def ver_pet(request, id):
    if request.method == "GET":
        pet = Pet.objects.get(id = id)
        return render(request, 'ver_pet.html', {'pet': pet})

@login_required
def ver_pedido_adocao(request):
    if request.method == "GET":
        pedidos = PedidoAdocao.objects.filter(usuario=request.user).filter(status="AG")
        return render(request, 'ver_pedido_adocao.html', {'pedidos': pedidos})

@login_required
def processa_pedido_adocao(request, id_pedido):
    status = request.GET.get('status')
    pedido = PedidoAdocao.objects.get(id=id_pedido)
    pet = Pet.objects.get(id=pedido.pet_id)
    if status == "A":
        pedido.status = 'AP'
        string = '''Ol??, sua ado????o foi aprovada. ...'''
        pet.status = 'A'
    elif status == "R":
        string = '''Ol??, sua ado????o foi recusada. ...'''
        pedido.status = 'R'
        pet.status = 'A'

    pet.save()
    pedido.save()

    
    print(pedido.usuario.email)
    email = send_mail(
        'Sua ado????o foi processada',
        string,
        'seuemail@gmail.com',
        [pedido.usuario.email,],
    )
    
    messages.add_message(request, constants.SUCCESS, 'Pedido de ado????o processado com sucesso')
    return redirect('/divulgar/ver_pedido_adocao')

@login_required
def dashboard(request):
    if request.method == "GET":
        return render(request, 'dashboard.html')

@login_required
@csrf_exempt
def api_adocoes_por_raca(request):
    racas = Raca.objects.all()

    qtd_adocoes = []
    for raca in racas:
        adocoes = PedidoAdocao.objects.filter(pet__raca=raca).count()
        qtd_adocoes.append(adocoes)

    racas = [raca.raca for raca in racas]
    data = {'qtd_adocoes': qtd_adocoes,
            'labels': racas}

    return JsonResponse(data)
from django.contrib.auth import authenticate, login, logout
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Sum
from django.db.models.functions import Extract
from django.db import connections

from main.models import filiais, regras, reguas, classificacao, setores, cargos, formacao
from generator.models import funcionarios, gerentes, orcamentos, margens

import pandas 
import datetime
import os

directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def entrar(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    
    context = {}

    if request.POST:
        username    = request.POST.get('username')
        password = request.POST.get('password')

        try:
            User.objects.get(username=username)
        except:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user, backend='django_auth_ldap.backend.LDAPBackend')                
                return redirect('inicio')
            else:
                messages.error(request, "Usuário não encontrado")
                return redirect('entrar')
        else:
            print('veio aqui')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')                
                return redirect('inicio')
            else:
                messages.error(request, "Senha incorreta")
                return redirect('entrar')

        # email    = request.POST.get('email')
        # password = request.POST.get('password')

        # try:
        #     User.objects.get(email=email)
        #     username = User.objects.get(email=email).username
        #     user     = authenticate(request, username=username, password=password)

        #     if user:
        #         login(request, user)
        #         return redirect('inicio')
        #     else:
        #         messages.error(request, "Senha incorreta")
        #         return redirect('entrar')

        # except:
        #     messages.error(request, "Email não cadastrado")
        #     return redirect('entrar')

    return render(request, 'entrar.html', context)

def sair(request):
    logout(request)
    return redirect('entrar')

def get_self_gestor(name=None):
    _gerentes = gerentes.objects.filter(ativo=True)
    is_gestor = False

    for i in _gerentes:
        if name == i.gestor:
            is_gestor = True

    return is_gestor

def indicadores(request):
    if not request.user.is_authenticated:
        return redirect('entrar')

    if not request.user.is_staff:
        return redirect('forbidden')

    _funcionarios = funcionarios.objects.all().order_by('nome')
    _orcamentos   = orcamentos.objects.all().order_by('setor__setor')
    _margens      = margens.objects.all()
    _cargos       = cargos.objects.all().order_by('cargo')

    if get_self_gestor(request.user):
        _ccusto         = list((gerentes.objects.get(gestor=request.user).dominio).split(" "))
        _funcionarios   = funcionarios.objects.filter(cargo__setor__centro_custo__in=(_ccusto)).order_by('nome')
        _orcamentos     = orcamentos.objects.filter(setor__centro_custo__in=(_ccusto)).order_by('setor__setor')
        _cargos         = cargos.objects.filter(setor__centro_custo__in=(_ccusto))
        
    if not request.user.is_superuser and not get_self_gestor(request.user):
        _funcionarios   = None
        _orcamentos     = None
        _margens        = None

    if request.GET.get('q') is not None and request.GET.get('q') != '':
        _funcionarios = _funcionarios.filter(nome__icontains=request.GET.get('q'))

    if request.GET.get('p') is not None and request.GET.get('p') != '':
        _orcamentos   = _orcamentos.filter(setor__setor__icontains=request.GET.get('p'))

    if request.method == 'POST':
        # atualização dos indicadores de orçamento
        if request.POST.getlist('nMargemOrcamento') != []:
            novo_orcamento = [float(s.replace(',', '.')) for s in request.POST.getlist('nMargemOrcamento')]
            for i in range(len(_orcamentos)):
                if _orcamentos[i].margem != novo_orcamento[i]:
                    _orcamentos[i].cadastro = datetime.datetime.now()
                _orcamentos[i].margem = novo_orcamento[i]
                _orcamentos[i].save()

        # atualização dos indicadores de margem unica
        if request.POST.getlist('nMargemUnica') != []:
            nova_margem = [float(s.replace(',', '.')) for s in request.POST.getlist('nMargemUnica')]
            for i in range(len(_margens)):
                if _margens[i].margem != nova_margem[i]:
                    _margens[i].cadastro = datetime.datetime.now()
                _margens[i].margem = nova_margem[i]
                _margens[i].save()
        
        # atualização dos indicadores individuais
        if request.POST.getlist('nMargemIndividual') != []:
            novo_indicador = [float(s.replace(',', '.')) for s in request.POST.getlist('nMargemIndividual')]
            novo_salario   = [float(s.replace(',', '.')) for s in request.POST.getlist('nSalario')]
            novo_admissao  = [s for s in request.POST.getlist('nInicioContrato')]
            novo_recisao   = [s for s in request.POST.getlist('nFinalContrato')]
            for i in range(len(_funcionarios)):
                _funcionarios[i].margem  = novo_indicador[i]
                _funcionarios[i].salario = novo_salario[i]
                if novo_admissao[i] == '':
                    _funcionarios[i].inicio = None
                else:
                    _funcionarios[i].inicio = novo_admissao[i]
                if novo_recisao[i] == '':
                    _funcionarios[i].fim = None
                else:
                    _funcionarios[i].fim = novo_recisao[i]
                _funcionarios[i].save()

        # adicionar funcionario
        if request.POST.get('aFuncNome') is not None and request.POST.get('aFuncCodigo') is not None and request.POST.get('aFuncCargo') is not None and request.POST.get('aFuncMargem') is not None and request.POST.get('aFuncSalario') is not None:
            add_func_nome    = request.POST.get('aFuncNome')
            add_func_cod     = request.POST.get('aFuncCodigo')
            add_func_cargo   = cargos.objects.get(pk=request.POST.get('aFuncCargo'))
            add_func_margem  = request.POST.get('aFuncMargem')
            add_func_salario = request.POST.get('aFuncSalario')
            funcionarios(nome=add_func_nome, codigo=add_func_cod, cargo=add_func_cargo, margem=add_func_margem, salario=add_func_salario).save()

        # remover funcionario
        if request.POST.get('dFunc') is not None:
            funcionarios.objects.get(pk=int(request.POST.get('dFunc'))).delete()
        
        return redirect('indicadores')

    context = {
        'funcionarios' : _funcionarios,
        'cargos'       : _cargos,
        'orcamentos'   : _orcamentos,
        'margens'      : _margens,
        'formacoes'    : formacao.objects.filter(status=True)
    }

    return render(request, 'indicadores.html', context)

def cadastros(request):
    if not request.user.is_authenticated:
        return redirect('entrar')

    if not request.user.is_staff:
        return redirect('forbidden')
    
    _filiais  = filiais.objects.all()
    _regras   = regras.objects.all()
    _setores  = setores.objects.all().order_by('setor', 'filial')
    _cargos   = cargos.objects.all()

    if get_self_gestor(request.user):
        _ccusto  = list((gerentes.objects.get(gestor=request.user).dominio).split(" "))
        _setores  = setores.objects.filter(centro_custo__in=(_ccusto)).order_by('setor', 'filial')
        _cargos   = cargos.objects.filter(setor__centro_custo__in=(_ccusto))

    if not request.user.is_superuser and not get_self_gestor(request.user):
        _regras     = None
        _cargos     = None
        _setores    = None        
    
    if request.GET.get('q') is not None and request.GET.get('q') != '':
        _cargos = _cargos.filter(cargo__icontains=request.GET.get('q'))

    if request.GET.get('p') is not None and request.GET.get('p') != '':
        _setores   = _setores.filter(setor__icontains=request.GET.get('p'))

    if request.method == 'POST':
        # atualização dos valores de pesos e metas
        if request.POST.getlist('nPeso') != [] and request.POST.getlist('nMeta') != []:
            pesos = [float(s.replace(',', '.')) for s in request.POST.getlist('nPeso')]
            metas = [float(s.replace(',', '.')) for s in request.POST.getlist('nMeta')]
            for i in range(len(_regras)):
                if (_regras[i].peso != pesos[i]) or (_regras[i].meta != metas[i]):
                    _regras[i].cadastro = datetime.datetime.now()
                _regras[i].peso = pesos[i]
                _regras[i].meta = metas[i]
                _regras[i].save()

        # adicionar cargo
        if request.POST.get('aCargoNome') is not None and request.POST.get('aCargoSetor') is not None and request.POST.get('aCargoRegua') is not None:
            add_cargo_nome  = request.POST.get('aCargoNome')
            add_cargo_setor = setores.objects.get(pk=int(request.POST.get('aCargoSetor')))
            add_cargo_regua = reguas.objects.get(pk=int(request.POST.get('aCargoRegua')))
            cargos(cargo=add_cargo_nome, setor=add_cargo_setor, regua=add_cargo_regua).save()

        # remover cargo
        if request.POST.get('dCargo') is not None:
            cargos.objects.get(pk=int(request.POST.get('dCargo'))).delete()

        # adicionar setor e enviar para o orçamento
        if request.POST.get('aSetorNome') is not None and request.POST.get('aSetorCentroCusuto'):
            add_setor_nome   = request.POST.get('aSetorNome')
            add_setor_cc     = request.POST.get('aSetorCentroCusuto')
            add_setor_filial = filiais.objects.get(pk=int(request.POST.get('aSetorFilial')))
            add_setor_tipo   = request.POST.get('aSetorTipo')
            setores(setor=add_setor_nome, centro_custo=add_setor_cc, filial=add_setor_filial, tipo=add_setor_tipo).save()
            orcamentos(setor=setores.objects.get(setor=add_setor_nome, filial=add_setor_filial), margem=0).save()

        # remover setor
        if request.POST.get('dSetor') is not None:
            setores.objects.get(pk=int(request.POST.get('dSetor'))).delete()

        
        return redirect('cadastros')
        
    context = {
        'regras'    : _regras,
        'setores'   : _setores,
        'cargos'    : _cargos,
        'filiais'   : _filiais,
        'formacoes' : formacao.objects.filter(status=True)
    }

    return render(request, 'cadastros.html', context)

def qualificacao(request):
    if not request.user.is_authenticated:
        return redirect('entrar')

    if not request.user.is_superuser:
        messages.error(request, "Apenas usuários autorizados.")
        return redirect('inicio')

    _niveis         = reguas.objects.all()
    _classificacao  = classificacao.objects.all()

    if request.GET.get('q') is not None and request.GET.get('q') != '':
        try:
            _niveis.get(regua=request.GET.get('q')).id
            _niveis         = _niveis.filter(regua=request.GET.get('q'))
            _classificacao  = _classificacao.filter(regua=_niveis.get(regua=request.GET.get('q')).id)
        except:
            return redirect ('reguas')

    if request.method == 'POST':
        if request.POST.getlist('cMinimo') != [] and request.POST.getlist('cMaximo') != [] and request.POST.getlist('cValor') != []:
            mins = [float(s.replace(',', '.')) for s in request.POST.getlist('cMinimo')]
            maxs = [float(s.replace(',', '.')) for s in request.POST.getlist('cMaximo')]
            vals = [float(s.replace(',', '.')) for s in request.POST.getlist('cValor')]

            for i in range(len(_classificacao)):
                if (_classificacao[i].minimo != mins[i]) or (_classificacao[i].maximo != maxs[i]) or (_classificacao[i].valor != vals[i]):
                    _classificacao[i].cadastro = datetime.datetime.now()
                _classificacao[i].minimo = mins[i]
                _classificacao[i].maximo = maxs[i]
                _classificacao[i].valor  = vals[i]
                _classificacao[i].save()
        
    context = {
        'niveis'        : _niveis,
        'classificacao' : _classificacao,
        'formacoes'     : formacao.objects.filter(status=True)
    }

    return render(request, 'reguas.html', context)

def historico(request):
    if not request.user.is_authenticated:
        return redirect('entrar')

    if not request.user.is_superuser:
        messages.error(request, "Apenas usuários autorizados.")
        return redirect('inicio')

    _formacoes = formacao.objects.values('id_grupo', 'status').annotate(total=Sum('premio_total'), vigencia=Extract('cadastro', 'year')).distinct().order_by('-id_grupo')

    try:
        int(request.GET.get('q'))
        search = int(request.GET.get('q'))
        if search >= 2000:
            _formacoes = formacao.objects.values('id_grupo', 'status').annotate(total=Sum('premio_total'), vigencia=Extract('cadastro', 'year')).distinct().order_by('-id_grupo').filter(vigencia=search)
        else:
            _formacoes = formacao.objects.filter(id_grupo=search).values('id_grupo', 'status').annotate(total=Sum('premio_total'), vigencia=Extract('cadastro', 'year')).distinct().order_by('-id_grupo')
    except:
        _formacoes
            

    if request.method == 'POST':
        cnn      = connections['default'].cursor()

        if request.POST.get('visualizar_fechamento') is not None and request.POST.get('visualizar_fechamento') != '':
            with cnn as cursor: 
                cursor.execute("select * from main_formacao where id_grupo = " + request.POST.get('visualizar_fechamento') + ";")
                colunas         = [field_name[0] for field_name in cursor.description]
                dataset         = [dict(zip(colunas, linhas)) for linhas in cursor.fetchall()]
                cursor.close()
            cnn.close()

            ano = str(formacao.objects.filter(id_grupo=request.POST.get('visualizar_fechamento')).last().cadastro.year)
            grp = str(request.POST.get('visualizar_fechamento'))         

            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="fechamento_ppr_' + ano + '-' + grp + '.xlsx"'                                
            pandas.DataFrame(dataset).to_excel(response)
            return response        

    context = {'formacoes': _formacoes}

    return render(request, 'historico.html', context)

def inicio(request):
    if not request.user.is_authenticated:
        return redirect('entrar')

    if not request.user.is_staff:
        return redirect('forbidden')

    context              = {}
    atingido             = margens.objects.get(regra__regra='Lucro Líquido').margem  
    meta                 = regras.objects.get(regra='Lucro Líquido').meta
    formacoes            = formacao.objects.filter(status=True)
    context['formacoes'] = formacoes

    if atingido >= meta:
        cnn      = connections['default'].cursor()
        queryset = render_to_string(os.path.join(directory, 'media\querysets\queryset.sql'))

        if get_self_gestor(request.user):
            _ccusto  = list((gerentes.objects.get(gestor=request.user).dominio).split(" "))
            _ccusto  = str(_ccusto).replace("[", "(").replace("]", ")")
            conditional = ("= c.id where c.centro_custo in " + _ccusto)
            queryset    = queryset.replace("= c.id", conditional)

        if not request.user.is_superuser and not get_self_gestor(request.user):
            conditional = ("main where main.funcionario like '%XXXX%' order by main.funcionario;")
            queryset    = queryset.replace("main order by main.funcionario;", conditional)

        if request.GET.get('q') is not None and request.GET.get('q') != '':
            conditional = ("main where main.funcionario like '%" + request.GET.get('q') + "%' order by main.funcionario;")
            queryset    = queryset.replace("main order by main.funcionario;", conditional)

        with cnn as cursor: 
            cursor.execute(queryset)
            colunas            = [field_name[0] for field_name in cursor.description]
            dataset            = [dict(zip(colunas, linhas)) for linhas in cursor.fetchall()]
            context['dataset'] = dataset
            cursor.close()
        cnn.close()
    else:
        context['dataset'] = 'Vazio'

    if request.method == 'POST':
        if request.POST.get('download') == 'true':
            if atingido >= meta and request.user.is_superuser:
                response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename="calculo_atual_detalhado.xlsx"'                                
                pandas.DataFrame(dataset).to_excel(response)
                return response

        # se houver algum calculo fechado no ano atual, exibe a opção de reabrir e reseta os status
        if request.POST.get('novo_periodo') == 'true' and request.user.is_superuser:
            if atingido >= meta:
                for i in formacoes:
                    i.status = False
                    i.save()
                return redirect('inicio')

        # realizo o fechamento do ano salvando na tebela do PPR final
        if request.POST.get('salvar_e_fechar') == 'true' and request.user.is_superuser:
            if atingido >= meta:
                try:
                    formacao.objects.all()
                    grupo = formacao.objects.last().id_grupo + 1
                except:
                    grupo = 1

                for i in dataset:
                    formacao(
                        id_grupo=grupo,
                        matricula=i["matricula"],
                        funcionario=i["funcionario"],
                        cargo=i["cargo"],
                        setor=i["setor"],
                        tipo=i["tipo"],
                        filial=i["filial"],
                        ll_peso=i["ll_peso"],
                        ll_meta=i["ll_meta"],
                        ll_atingido=i["ll_atingido"],
                        ll_margem=i["ll_margem"],
                        ms_peso=i["ms_peso"],
                        ms_meta=i["ms_meta"],
                        ms_atingido=i["ms_atingido"],
                        ms_margem=i["ms_margem"],
                        ec_peso=i["ec_peso"],
                        ec_meta=i["ec_meta"],
                        ec_atingido=i["ec_atingido"],
                        ec_margem=i["ec_margem"],
                        dv_peso=i["dv_peso"],
                        dv_meta=i["dv_meta"],
                        dv_atingido=i["dv_atingido"],
                        dv_margem=i["dv_margem"],
                        oc_peso=i["oc_peso"],
                        oc_meta=i["oc_meta"],
                        oc_atingido=i["oc_atingido"],
                        oc_margem=i["oc_margem"],
                        ii_peso=i["ii_peso"],
                        ii_meta=i["ii_meta"],
                        ii_atingido=i["ii_atingido"],
                        ii_margem=i["ii_margem"],
                        salario=i["salario"],
                        margem_total=i["margem_total"],
                        nome_regua=i["nome_regua"],
                        valor_regua=i["valor_regua"],
                        premio_total=i["premio_total"],
                        status=True
                    ).save()
                return redirect('inicio')
        
        return redirect('inicio')

    return render(request, 'inicio.html', context)

def forbidden(request):
    return render(request, 'forbidden.html', {})
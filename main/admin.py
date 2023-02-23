from django.contrib import admin
from main.models import regras, reguas, setores, cargos, classificacao
from generator.models import funcionarios, gerentes, orcamentos, margens

class regrasAdmin(admin.ModelAdmin):
    list_display = ('regra', 'peso', 'meta', 'cadastro')
admin.site.register(regras, regrasAdmin)

class reguasAdmin(admin.ModelAdmin):
    list_display = ('regua', 'cadastro')
admin.site.register(reguas, reguasAdmin)

class setoresAdmin(admin.ModelAdmin):
    list_display = ('setor', 'centro_custo', 'cadastro')
    search_fields = ('setor', 'centro_custo')
admin.site.register(setores, setoresAdmin)

class cargosAdmin(admin.ModelAdmin):
    list_display = ('cargo', 'setor', 'regua', 'cadastro')
    search_fields = ('cargo', 'setor')
admin.site.register(cargos, cargosAdmin)

class classificacaoAdmin(admin.ModelAdmin):
    list_display = ('regua', 'minimo', 'maximo', 'valor', 'cadastro')
    search_fields = ('regua', 'valor')
admin.site.register(classificacao, classificacaoAdmin)

class margensAdmin(admin.ModelAdmin):
    list_display = ('regra', 'margem', 'cadastro')
admin.site.register(margens, margensAdmin)

class orcamentosAdmin(admin.ModelAdmin):
    list_display = ('setor', 'margem', 'cadastro')
admin.site.register(orcamentos, orcamentosAdmin)

class gerentesAdmin(admin.ModelAdmin):
    list_display = ('gestor', 'dominio', 'cadastro', 'ativo')
    search_fields = ('nome', 'dominio')
admin.site.register(gerentes, gerentesAdmin)

class funcionariosAdmin(admin.ModelAdmin):
    list_display = ('inicio', 'fim', 'nome', 'codigo', 'cargo', 'margem', 'salario', 'cadastro')
    search_fields = ('nome', 'codigo', 'cargo')
admin.site.register(funcionarios, funcionariosAdmin)

admin.site.site_header      = 'Sistema PPR - Colorado Máquinas'
admin.site.site_title       = 'Sistema PPR - Colorado Máquinas'
admin.site.index_title      = 'Administração'
admin.empty_value_display   = '**Empty**'
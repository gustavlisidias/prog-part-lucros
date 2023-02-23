from django.db import models

TIPOS = [
    ("R", "RECEITA"),
    ("D", "DESPESA")
]

class filiais(models.Model):
    nome                = models.CharField(max_length=128, verbose_name="Filial")
    razao               = models.CharField(max_length=128, verbose_name="Razão Social")
    cnpj                = models.CharField(max_length=128, verbose_name="CNPJ")
    cidade              = models.CharField(max_length=128, verbose_name="Cidade")
    cadastro            = models.DateTimeField(auto_now_add=True, verbose_name="Cadastro")

    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Filial"
        verbose_name_plural = "Filiais"

class regras(models.Model):
    regra               = models.CharField(max_length=64, verbose_name="Regra")
    peso                = models.FloatField(verbose_name="Peso (%)")
    meta                = models.FloatField(verbose_name="Meta (%)")
    cadastro            = models.DateTimeField(auto_now_add=True, verbose_name="Cadastro")

    def __str__(self):
        return self.regra
    
    class Meta:
        verbose_name = "Peso e Meta"
        verbose_name_plural = "Pesos & Metas"

class reguas(models.Model):
    regua               = models.CharField(max_length=64, verbose_name="Régua")
    cadastro            = models.DateTimeField(auto_now_add=True, verbose_name="Cadastro")

    def __str__(self):
        return self.regua
    
    class Meta:
        verbose_name = "Régua"
        verbose_name_plural = "Réguas"

class classificacao(models.Model):
    regua               = models.ForeignKey(reguas, on_delete=models.CASCADE, verbose_name="Categoria")
    minimo              = models.FloatField(verbose_name="Mínimo")
    maximo              = models.FloatField(verbose_name="Máximo")
    valor               = models.FloatField(verbose_name="Valor")
    cadastro            = models.DateTimeField(auto_now_add=True, verbose_name="Cadastro")

    def __str__(self):
        return self.regua.regua
    
    class Meta:
        verbose_name = "Nível da Régua"
        verbose_name_plural = "Níveis da Régua"

class setores(models.Model):
    setor               = models.CharField(max_length=64, verbose_name="Setor")
    filial              = models.ForeignKey(filiais, on_delete=models.CASCADE, verbose_name="Filial")
    tipo                = models.CharField(max_length=64, choices=TIPOS, verbose_name="tipo")
    centro_custo        = models.CharField(max_length=64, verbose_name="Centro de Custo")
    cadastro            = models.DateTimeField(auto_now_add=True, verbose_name="Cadastro")

    def __str__(self):
        return self.setor + ' - ' + self.filial.cidade
    
    class Meta:
        verbose_name = "Setor"
        verbose_name_plural = "Setores"

class cargos(models.Model):
    cargo               = models.CharField(max_length=64, verbose_name="Cargo")
    setor               = models.ForeignKey(setores, on_delete=models.CASCADE, verbose_name="Setor")
    regua               = models.ForeignKey(reguas, on_delete=models.CASCADE, verbose_name="Régua")
    cadastro            = models.DateTimeField(auto_now_add=True, verbose_name="Cadastro")

    def __str__(self):
        return self.cargo + ' - ' + self.setor.setor + ' (' + self.setor.filial.cidade + ')'
    
    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"

class formacao(models.Model):
    id_grupo            = models.IntegerField(verbose_name="Grupo ID")
    matricula           = models.CharField(max_length=32, verbose_name="Matrícula")
    funcionario         = models.CharField(max_length=128, verbose_name="Funcionário")
    cargo               = models.CharField(max_length=128, verbose_name="Cargo")
    setor               = models.CharField(max_length=128, verbose_name="Setor")
    tipo                = models.CharField(max_length=2, verbose_name="Receita/Despesa")
    filial              = models.CharField(max_length=128, verbose_name="Filial")
    ll_peso             = models.FloatField(verbose_name="Peso Lucro Líquido Global")
    ll_meta             = models.FloatField(verbose_name="Meta Lucro Líquido Global")
    ll_atingido         = models.FloatField(verbose_name="Resultado Lucro Líquido Global")
    ll_margem           = models.FloatField(verbose_name="Mergem Lucro Líquido Global")
    ms_peso             = models.FloatField(verbose_name="Peso Market Share")
    ms_meta             = models.FloatField(verbose_name="Meta Market Share")
    ms_atingido         = models.FloatField(verbose_name="Resultado Market Share")
    ms_margem           = models.FloatField(verbose_name="Margem Market Share")
    ec_peso             = models.FloatField(verbose_name="Peso Experiência do Cliente")
    ec_meta             = models.FloatField(verbose_name="Meta Experiência do Cliente")
    ec_atingido         = models.FloatField(verbose_name="Resultado Experiência do Cliente")
    ec_margem           = models.FloatField(verbose_name="Margem Experiência do Cliente")
    dv_peso             = models.FloatField(verbose_name="Peso Despesa Sobre Venda")
    dv_meta             = models.FloatField(verbose_name="Meta Despesa Sobre Venda")
    dv_atingido         = models.FloatField(verbose_name="Resultado Despesa Sobre Venda")
    dv_margem           = models.FloatField(verbose_name="Margem Despesa Sobre Venda")
    oc_peso             = models.FloatField(verbose_name="Peso Orçamento da Área")
    oc_meta             = models.FloatField(verbose_name="Meta Orçamento da Área")
    oc_atingido         = models.FloatField(verbose_name="Resultado Orçamento da Área")
    oc_margem           = models.FloatField(verbose_name="Margem Orçamento da Área")
    ii_peso             = models.FloatField(verbose_name="Peso Indicador Individual")
    ii_meta             = models.FloatField(verbose_name="Meta Indicador Individual")
    ii_atingido         = models.FloatField(verbose_name="Resultado Indicador Individual")
    ii_margem           = models.FloatField(verbose_name="Margem Indicador Individual")
    salario             = models.FloatField(verbose_name="Salário")
    margem_total        = models.FloatField(verbose_name="Total Margem")
    nome_regua          = models.CharField(max_length=32, verbose_name="Tipo Régua")
    valor_regua         = models.FloatField(verbose_name="Régua")
    premio_total        = models.FloatField(verbose_name="Total PPR")
    status              = models.BooleanField(default=False, verbose_name="Finalizado")
    cadastro            = models.DateTimeField(auto_now_add=True, verbose_name="Cadastro")

    def __str__(self):
        return 'PPR ' + str(self.cadastro.year) + str(self.id)
    
    class Meta:
        verbose_name = "Hitórico PPR"
        verbose_name_plural = "Hitórico PPR"
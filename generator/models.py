from django.db import models
from django.contrib.auth.models import User
from main.models import setores, cargos, regras

class funcionarios(models.Model):
    nome                = models.CharField(max_length=64, verbose_name="Funcionário")
    codigo              = models.CharField(max_length=64, verbose_name="Matrícula")
    cargo               = models.ForeignKey(cargos, on_delete=models.CASCADE, verbose_name="Cargo")
    margem              = models.FloatField(verbose_name="Atingido (%)")
    salario             = models.FloatField(verbose_name="Salário")
    inicio              = models.DateField(verbose_name="Inicio do Contrato", null=True, blank=True)
    fim                 = models.DateField(verbose_name="Fim do Contato", null=True, blank=True)
    cadastro            = models.DateTimeField(auto_now_add=True, verbose_name="Cadastro")

    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Funcionário"
        verbose_name_plural = "03 - Funcionários" 

class gerentes(models.Model):
    gestor              = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Gestor")
    dominio             = models.CharField(max_length=480, verbose_name="Centros de Custo")
    ativo               = models.BooleanField(default=True, verbose_name="Ativo")
    cadastro            = models.DateTimeField(auto_now_add=True, verbose_name="Cadastro")

    def __str__(self):
        return self.gestor.first_name + ' ' + self.gestor.last_name
    
    class Meta:
        verbose_name = "Gestor"
        verbose_name_plural = "04 - Gerentes" 

class orcamentos(models.Model):
    setor               = models.ForeignKey(setores, on_delete=models.CASCADE, verbose_name="Setor")
    margem              = models.FloatField(verbose_name="Atingido (%)")
    cadastro            = models.DateTimeField(auto_now_add=True, verbose_name="Cadastro")

    def __str__(self):
        return 'Orçamento: ' + self.setor.setor
    
    class Meta:
        verbose_name = "Orçamento"
        verbose_name_plural = "02 - Orçamentos"

class margens(models.Model):
    regra               = models.ForeignKey(regras, on_delete=models.CASCADE, verbose_name="Regra")
    margem              = models.FloatField(verbose_name="Atingido (%)")
    cadastro            = models.DateTimeField(auto_now_add=True, verbose_name="Cadastro")

    def __str__(self):
        return 'Margem: ' + self.regra.regra
    
    class Meta:
        verbose_name = "Margem"
        verbose_name_plural = "01 - Margens"
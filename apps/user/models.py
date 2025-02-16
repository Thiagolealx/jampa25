from django.db import models
from django.core.exceptions import ValidationError

class Lote(models.Model):
    descricao = models.CharField(max_length=255)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    unidades = models.IntegerField()
    status = models.CharField(max_length=10, choices=[('ativo', 'Ativo'), ('encerrado', 'Encerrado')], default='ativo')

    def __str__(self):
        return f"{self.descricao} - {self.status}"
    class Meta:
        ordering = ['-id']
    
class Categoria(models.Model):
    descricao = models.CharField(max_length=100)

    def __str__(self):
        return self.descricao
    class Meta:
        ordering = ['-id']

class TipoEvento(models.Model):
    descricao = models.CharField(max_length=100)

    def __str__(self):
        return self.descricao
    
    class Meta:
        ordering = ['-id']
    
class Evento(models.Model):
    descricao = models.CharField(max_length=100)
    tipo = models.ForeignKey(TipoEvento, on_delete=models.CASCADE)    
    data = models.DateField(null=True,blank=True)
    valor_planejado = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    valor_arrecadado = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    quantidade_pessoas = models.IntegerField(null=True,blank=True)
   
    @property
    def valor_do_evento(self):
        valor_arrecadado = self.valor_arrecadado or 0
        valor_planejado = self.valor_planejado or 0
        return valor_arrecadado - valor_planejado    

    def __str__(self):
        return self.descricao    
    class Meta:
        ordering = ['-id']
class Camisas(models.Model):

    TAMANHO = (
        ('P', 'Pequeno'),
        ('M', 'Médio'),
        ('G', 'Grande'),
        ('GG', 'Extra Grande'),
    )

    descricao = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100,null=True,blank=True)
    tamanho = models.CharField(max_length=2,choices=TAMANHO)
    quantidade = models.IntegerField(null=True,blank=True)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.descricao    
    class Meta:
        ordering = ['-id']


class Planejamento(models.Model):
    descricao = models.CharField(max_length=100)   
    valor_planejado = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)   
      

    def __str__(self):
        return self.descricao    
    class Meta:
        ordering = ['-id']

class Profissional(models.Model):
    nome = models.CharField(max_length=100)
    funcao = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    cache = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    jack_jill = models.BooleanField(default=False, verbose_name='Jack & Jill', null=True, blank=True)
    barco = models.BooleanField(default=False, verbose_name='Barco', null=True, blank=True)

    @property
    def barco_com_quantidade_pessoas(self):
        evento = Evento.objects.first()  # Ajuste conforme necessário para obter o evento correto
        return evento.quantidade_pessoas if evento else 0

    def save(self, *args, **kwargs):
        evento = Evento.objects.first()  # Ajuste conforme necessário para obter o evento correto
        if self.barco:
            if evento and evento.quantidade_pessoas > 0:
                evento.quantidade_pessoas -= 1
                evento.save()
            else:
                raise ValidationError("Não há vagas disponíveis no barco.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} - {self.funcao}"
    
    class Meta:
        ordering = ['-id']
from django.db import models

class Lote(models.Model):
    descricao = models.CharField(max_length=255)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    unidades = models.IntegerField()
    status = models.CharField(max_length=10, choices=[('ativo', 'Ativo'), ('encerrado', 'Encerrado')], default='ativo')

    def __str__(self):
        return self.descricao
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
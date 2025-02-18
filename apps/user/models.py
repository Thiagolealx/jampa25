from datetime import datetime
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
    contador_barco = models.IntegerField(default=0,editable=False,verbose_name="Vagas preenchidas ")

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

    def clean(self):
        evento = Evento.objects.first()  # Ajuste conforme necessário para obter o evento correto
        if not evento:
            raise ValidationError("Evento não encontrado.")
        
        if self.barco:
            if evento.contador_barco >= evento.quantidade_pessoas:
                raise ValidationError("Não há vagas disponíveis no barco.")

    def save(self, *args, **kwargs):
        self.clean()  # Chama o método clean para validação
        evento = Evento.objects.first()  # Ajuste conforme necessário para obter o evento correto
        
        # Verificar se a instância já existe no banco de dados
        if self.pk:
            old_instance = Profissional.objects.get(pk=self.pk)
            if old_instance.barco and not self.barco:
                # Se o campo barco foi desmarcado, decrementar o contador
                evento.contador_barco -= 1
                evento.save()
        
        if self.barco and (not self.pk or (self.pk and not old_instance.barco)):
            evento.contador_barco += 1
            evento.save()
        
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        evento = Evento.objects.first()  # Ajuste conforme necessário para obter o evento correto
        if self.barco and evento:
            if evento.contador_barco > 0:
                evento.contador_barco -= 1
                evento.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} - {self.funcao}"
    
    class Meta:
        ordering = ['-id']

class Inscricao(models.Model):
    # Step 1
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=11)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    ano = models.IntegerField(editable=False)
    cep = models.CharField("CEP", max_length=9, blank=True, null=True,
                           help_text="Digite um CEP válido para atualizar os campos abaixo.")  
    cidade = models.CharField(
        "Município", max_length=100, blank=True, null=True)
    uf = models.CharField("UF", max_length=2, blank=True,null=True)

    # Step 2
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE)
    

    def save(self, *args, **kwargs):
        if not self.ano:
            self.ano = datetime.now().year
        super().save(*args, **kwargs)
    
    def eventos_cadastrados(self):
        return ", ".join([str(evento.evento.descricao) for evento in self.inscricaoevento_set.all()])


    def __str__(self):
        return f"{self.nome} - {self.cpf}"

    class Meta:
        ordering = ['-id']

class InscricaoEvento(models.Model):
    inscricao = models.ForeignKey(Inscricao, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    confirmar = models.BooleanField(default=False, verbose_name="Confirmar Evento")

    def __str__(self):
        return f"{self.inscricao.nome} - {self.evento.descricao} - {'Sim' if self.confirmar else 'Não'}"
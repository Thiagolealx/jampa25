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
    # contador_barco = models.IntegerField(default=0,editable=False,verbose_name="Vagas preenchidas ")
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Valor unitário do evento')
    contador_inscricoes = models.IntegerField(default=0, editable=False, verbose_name="Inscrições")

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

    # def clean(self):
    #     evento = Evento.objects.first()  # Ajuste conforme necessário para obter o evento correto
    #     if not evento:
    #         raise ValidationError("Evento não encontrado.")
        
    #     if self.barco:
    #         if evento.contador_barco >= evento.quantidade_pessoas:
    #             raise ValidationError("Não há vagas disponíveis no barco.")

    # def save(self, *args, **kwargs):
    #     self.clean()  # Chama o método clean para validação
    #     evento = Evento.objects.first()  # Ajuste conforme necessário para obter o evento correto
        
    #     # Verificar se a instância já existe no banco de dados
    #     if self.pk:
    #         old_instance = Profissional.objects.get(pk=self.pk)
    #         if old_instance.barco and not self.barco:
    #             # Se o campo barco foi desmarcado, decrementar o contador
    #             evento.contador_barco -= 1
    #             evento.save()
        
    #     if self.barco and (not self.pk or (self.pk and not old_instance.barco)):
    #         evento.contador_barco += 1
    #         evento.save()
        
    #     super().save(*args, **kwargs)

    # def delete(self, *args, **kwargs):
    #     evento = Evento.objects.first()  # Ajuste conforme necessário para obter o evento correto
    #     if self.barco and evento:
    #         if evento.contador_barco > 0:
    #             evento.contador_barco -= 1
    #             evento.save()
    #     super().delete(*args, **kwargs)

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
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Desconto a ser aplicado no valor do lote')
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Valor total após aplicar desconto e incluir eventos')
    parcelas = models.IntegerField(default=1, choices=[(i, str(i)) for i in range(1, 11)], help_text='Número de parcelas para pagamento')

    def save(self, *args, **kwargs):
        if not self.ano:
            self.ano = datetime.now().year
        super().save(*args, **kwargs)  # Salvar a instância primeiro
    
    def calcular_valor_total(self):
        lote_valor = self.lote.valor_unitario if self.lote else 0
        valor_lote_com_desconto = lote_valor - self.desconto
        eventos_valor = sum(evento.evento.valor_unitario for evento in self.inscricaoevento_set.all())
        return valor_lote_com_desconto + eventos_valor
    
    def calcular_parcela(self):
        if self.parcelas > 0:
            return self.calcular_valor_total() / self.parcelas
        return 0
        
        
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

    def save(self, *args, **kwargs):
        # Se a instância já existe, significa que estamos atualizando
        if self.pk:
            old_instance = InscricaoEvento.objects.get(pk=self.pk)
            # Se o evento foi alterado
            if old_instance.evento != self.evento:
                # Decrementa o contador do evento antigo
                old_instance.evento.contador_inscricoes -= 1
                old_instance.evento.save()

        # Incrementa o contador do novo evento
        self.evento.contador_inscricoes += 1
        self.evento.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Decrementa o contador do evento ao deletar
        self.evento.contador_inscricoes -= 1
        self.evento.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.inscricao.nome} - {self.evento.descricao} - {'Sim' if self.confirmar else 'Não'}"

    class Meta:
        ordering = ['-id']


class Entradas(models.Model):
    descricao = models.CharField(max_length=100, null=True, blank=True)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.IntegerField(null=True, blank=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    data = models.DateField(auto_now_add=True)

    def calcular_valor_total(self):
        if self.valor_unitario is not None and self.quantidade is not None:
            return self.valor_unitario * self.quantidade
        return 0

    def save(self, *args, **kwargs):        
        self.valor_total = self.calcular_valor_total()  # Corrigido aqui
        super().save(*args, **kwargs)

    def __str__(self):
        return self.descricao

class Saidas(models.Model):
    descricao = models.CharField(max_length=100, null=True, blank=True)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.IntegerField(null=True, blank=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    data = models.DateField(auto_now_add=True)

    def calcular_valor_total(self):
        if self.valor_unitario is not None and self.quantidade is not None:
            return self.valor_unitario * self.quantidade
        return 0

    def save(self, *args, **kwargs):        
        self.valor_total = self.calcular_valor_total()  # Corrigido aqui
        super().save(*args, **kwargs)

    def __str__(self):
        return self.descricao

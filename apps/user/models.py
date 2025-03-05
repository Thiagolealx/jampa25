from datetime import datetime
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum
from datetime import timedelta
from django.dispatch import receiver
from django.db.models.signals import post_save


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
        
        super().save(*args, **kwargs)
    
    def calcular_valor_total(self):
        lote_valor = self.lote.valor_unitario if self.lote else 0
        valor_lote_com_desconto = lote_valor - self.desconto
        eventos_valor = sum((evento.evento.valor_unitario or 0) for evento in self.inscricaoevento_set.all())
        return valor_lote_com_desconto + eventos_valor
    
    def calcular_parcela(self):
        if self.parcelas > 0:
            return self.calcular_valor_total() / self.parcelas
        return 0
        
        
    def eventos_cadastrados(self):
        return ", ".join([str(evento.evento.descricao) for evento in self.inscricaoevento_set.all()])


    def valor_pago_total(self):
        return self.pagamento_set.aggregate(Sum('valor_pago'))['valor_pago__sum'] or 0

    def valor_a_pagar(self):
        return self.calcular_valor_total() - self.valor_pago_total()

    def __str__(self):
        return f"{self.nome} - {self.cpf}"

    class Meta:
        ordering = ['-id']
    
@receiver(post_save, sender=Inscricao)
def update_valor_total(sender, instance, created, **kwargs):
    if created:
        instance.valor_total = instance.calcular_valor_total()
        instance.save(update_fields=['valor_total'])

   

class InscricaoEvento(models.Model):
    inscricao = models.ForeignKey(Inscricao, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    confirmar = models.BooleanField(default=False, verbose_name="Confirmar Evento")

    def vagas_restantes(self):
        
        return self.evento.quantidade_pessoas - self.evento.contador_inscricoes

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

class Pagamento(models.Model):
    inscricao = models.ForeignKey(Inscricao, on_delete=models.CASCADE)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2)
    parcela = models.IntegerField()
    data_pagamento = models.DateField(auto_now_add=True)
    data_proximo_pagamento = models.DateField(null=True, blank=True) 

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Atualiza a data do próximo pagamento
        self.data_proximo_pagamento = self.data_pagamento + timedelta(days=30)
        super().save(update_fields=['data_proximo_pagamento'])   

    def __str__(self):
        return f"Pagamento de {self.valor_pago} para {self.inscricao.nome} - Parcela {self.parcela}"

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        ordering = ['-id']



class Caixa(models.Model):
  
    
    @property
    def total_inscricoes(self):
        return self.pagamento_set.aggregate(Sum('pagamento__valor_pago'))['pagamento__valor_pago__sum'] or 0
    
    @property
    def total_camisas(self):
        return self.pagamento_set.aggregate(Sum('valor_pago'))['valor_pago__sum'] or 0
    
    @property
    def total_entradas(self):
        return self.pagamento_set.aggregate(Sum('valor_pago'))['valor_pago__sum'] or 0
    
    @property
    def total_planejamento(self):
        return self.pagamento_set.aggregate(Sum('valor_pago'))['valor_pago__sum'] or 0

    @property
    def total_saidas(self):
        return self.pagamento_set.aggregate(Sum('valor_pago'))['valor_pago__sum'] or 0

    @property
    def total_caixa(self):
        return (self.total_inscricoes + self.total_camisas + self.total_entradas ) - self.total_saidas

    @property
    def saldo(self):
        return (self.total_caixa) - self.total_saidas

    class Meta:
        verbose_name = "Caixa"
        verbose_name_plural = "Caixas"
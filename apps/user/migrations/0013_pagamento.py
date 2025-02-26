# Generated by Django 5.0.6 on 2025-02-26 15:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0012_alter_inscricaoevento_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pagamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor_pago', models.DecimalField(decimal_places=2, max_digits=10)),
                ('parcela', models.IntegerField()),
                ('data_pagamento', models.DateField(auto_now_add=True)),
                ('inscricao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.inscricao')),
            ],
        ),
    ]

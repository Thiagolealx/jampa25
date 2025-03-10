# Generated by Django 5.0.6 on 2025-02-18 02:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_alter_evento_contador_barco_inscricao'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inscricao',
            name='evento',
        ),
        migrations.AlterField(
            model_name='inscricao',
            name='ano',
            field=models.IntegerField(editable=False),
        ),
        migrations.CreateModel(
            name='InscricaoEvento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('confirmar', models.BooleanField(default=False, verbose_name='Confirmar Evento')),
                ('evento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.evento')),
                ('inscricao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.inscricao')),
            ],
        ),
    ]

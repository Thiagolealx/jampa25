# Generated by Django 5.0.6 on 2025-02-17 23:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_profissional_delete_profissionais'),
    ]

    operations = [
        migrations.AddField(
            model_name='evento',
            name='contador_barco',
            field=models.IntegerField(default=0),
        ),
    ]

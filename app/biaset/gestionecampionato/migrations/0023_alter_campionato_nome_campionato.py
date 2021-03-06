# Generated by Django 3.2.6 on 2022-01-29 01:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestionecampionato', '0022_alter_campionato_nome_campionato'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campionato',
            name='nome_campionato',
            field=models.CharField(max_length=50, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_campionato', message='Il nome del campionato deve essere alfanumerico.', regex='^[A-Za-z0-9]*$')]),
        ),
    ]

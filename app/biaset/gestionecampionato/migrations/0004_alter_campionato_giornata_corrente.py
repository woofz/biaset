# Generated by Django 3.2.6 on 2022-01-15 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestionecampionato', '0003_campionato_championship_admin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campionato',
            name='giornata_corrente',
            field=models.IntegerField(default=1),
        ),
    ]

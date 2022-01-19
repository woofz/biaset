# Generated by Django 3.2.6 on 2022-01-18 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestionecampionato', '0009_alter_formazione_partita'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='formazione',
            options={'verbose_name_plural': 'Formazioni'},
        ),
        migrations.AddField(
            model_name='formazione',
            name='data_inserimento',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Data inserimento formazione'),
        ),
    ]

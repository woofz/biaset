# Generated by Django 3.2.6 on 2022-01-24 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestioneutenza', '0009_alter_invito_expire_dt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invito',
            name='destinatario',
            field=models.EmailField(max_length=255, verbose_name='Email destinatario'),
        ),
    ]

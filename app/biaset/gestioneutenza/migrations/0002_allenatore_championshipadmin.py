# Generated by Django 3.2.6 on 2022-01-06 15:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gestioneutenza', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChampionshipAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_profilo', models.CharField(blank=True, default='Championship Admin', max_length=35, null=True, verbose_name='Profilo')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Utente')),
            ],
        ),
        migrations.CreateModel(
            name='Allenatore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_profilo', models.CharField(blank=True, default='Allenatore', max_length=35, null=True, verbose_name='Profilo')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Utente')),
            ],
        ),
    ]

# Generated by Django 3.2.6 on 2022-01-22 02:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gestionecampionato', '0017_alter_campionato_partecipanti'),
    ]

    operations = [
        migrations.RenameField(
            model_name='campionato',
            old_name='max_partecipanti',
            new_name='partecipanti',
        ),
    ]

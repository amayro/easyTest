# Generated by Django 2.1.2 on 2018-10-24 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0002_remove_answer_text'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='question',
            managers=[
            ],
        ),
        migrations.RemoveField(
            model_name='test',
            name='questions',
        ),
        migrations.AddField(
            model_name='question',
            name='test',
            field=models.ManyToManyField(blank=True, related_name='questions', to='mainapp.Test'),
        ),
    ]

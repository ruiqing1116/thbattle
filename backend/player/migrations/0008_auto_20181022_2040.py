# Generated by Django 2.1.2 on 2018-10-22 12:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0007_auto_20181022_2039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='reporter',
            field=models.ForeignKey(help_text='报告者', on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='player.Player', verbose_name='举报者'),
        ),
        migrations.AlterField(
            model_name='report',
            name='suspect',
            field=models.ForeignKey(help_text='嫌疑人', on_delete=django.db.models.deletion.CASCADE, related_name='reported_by', to='player.Player', verbose_name='嫌疑人'),
        ),
    ]

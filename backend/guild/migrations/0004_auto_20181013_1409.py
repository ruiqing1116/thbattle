# Generated by Django 2.1.2 on 2018-10-13 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0002_auto_20181013_1409'),
        ('guild', '0003_guild_badges'),
    ]

    operations = [
        migrations.AddField(
            model_name='guild',
            name='requests',
            field=models.ManyToManyField(related_name='requested_guilds', to='player.Player', verbose_name='申请列表'),
        ),
        migrations.AlterField(
            model_name='guild',
            name='badges',
            field=models.ManyToManyField(related_name='guilds', to='badge.Badge', verbose_name='勋章'),
        ),
    ]

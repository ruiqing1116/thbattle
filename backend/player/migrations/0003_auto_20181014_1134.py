# Generated by Django 2.1.2 on 2018-10-14 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0002_auto_20181014_1124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='badges',
            field=models.ManyToManyField(blank=True, help_text='勋章', related_name='players', to='badge.Badge', verbose_name='勋章'),
        ),
        migrations.AlterField(
            model_name='player',
            name='blocks',
            field=models.ManyToManyField(blank=True, help_text='黑名单', related_name='_player_blocks_+', to='player.Player', verbose_name='黑名单'),
        ),
        migrations.AlterField(
            model_name='player',
            name='friends',
            field=models.ManyToManyField(blank=True, help_text='好友', related_name='_player_friends_+', to='player.Player', verbose_name='好友'),
        ),
    ]
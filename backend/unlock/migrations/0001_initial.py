# Generated by Django 2.0.7 on 2018-08-08 14:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('achievement', models.SlugField(max_length=256, verbose_name='成就')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='achievements', to=settings.AUTH_USER_MODEL, verbose_name='玩家')),
            ],
            options={
                'verbose_name': '成就',
                'verbose_name_plural': '成就',
            },
        ),
        migrations.CreateModel(
            name='Unlocked',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('item', models.SlugField(max_length=256, verbose_name='解锁项目')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unlocks', to=settings.AUTH_USER_MODEL, verbose_name='玩家')),
            ],
            options={
                'verbose_name': '解锁项目',
                'verbose_name_plural': '解锁项目',
            },
        ),
    ]

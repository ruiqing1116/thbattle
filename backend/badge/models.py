# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

# -- stdlib --
# -- third party --
from django.contrib.auth.models import User
from django.db import models

# -- own --
from guild import models as guild_models


# -- code --
class BadgeType(models.Model):

    class Meta:
        verbose_name        = '勋章类型'
        verbose_name_plural = '勋章类型'

    id          = models.AutoField(primary_key=True)
    title       = models.CharField('标题', max_length=50, unique=True)
    description = models.CharField('描述', max_length=200)
    icon        = models.ImageField('图标')
    icon2x      = models.ImageField('图标@2x')

    def __str__(self):
        return self.title


class PlayerBadge(models.Model):

    class Meta:
        verbose_name        = '玩家勋章'
        verbose_name_plural = '玩家勋章'

    id      = models.AutoField(primary_key=True)
    owner   = models.ForeignKey(User, models.CASCADE, verbose_name='所有者', related_name='badges')
    type    = models.ForeignKey(BadgeType, models.CASCADE, verbose_name='勋章', related_name='+')
    created = models.DateTimeField('日期', auto_now_add=True)

    def __str__(self):
        return f'{self.owner.username}的{self.type.title}勋章'


class GuildBadge(models.Model):

    class Meta:
        verbose_name        = '势力勋章'
        verbose_name_plural = '势力勋章'

    id      = models.AutoField(primary_key=True)
    guild   = models.ForeignKey(guild_models.Guild, models.CASCADE, verbose_name='所有势力', related_name='badges')
    type    = models.ForeignKey(BadgeType, models.CASCADE, verbose_name='勋章', related_name='badges')
    created = models.DateTimeField('日期', auto_now_add=True)

    def __str__(self):
        return f'{self.guild.name}的{self.type.title}勋章'

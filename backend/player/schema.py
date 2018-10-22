# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

# -- stdlib --
# -- third party --
from django.db import transaction
from graphene_django.types import DjangoObjectType
import django.contrib.auth as auth
import django.contrib.auth.models as auth_models
import graphene as gh

# -- own --
from . import models
from graphql import GraphQLError
from utils.graphql import require_login, require_perm
import utils.leancloud


# -- code --
class User(DjangoObjectType):
    class Meta:
        model = models.User
        exclude_fields = [
            'password',
        ]


class Group(DjangoObjectType):
    class Meta:
        model = auth_models.Group


class Permission(DjangoObjectType):
    class Meta:
        model = auth_models.Permission


class Player(DjangoObjectType):
    class Meta:
        model = models.Player
        exclude_fields = [
            'friended_by',
            'blocked_by',
            'reported_by',
        ]

    friend_requests = gh.List(
        gh.NonNull('player.schema.Player'),
        description="未处理的好友请求",
    )

    @staticmethod
    def resolve_friends(root, info):
        ctx = info.context
        require_login(ctx)
        p = ctx.user.player
        if p.id != root.id:
            require_perm(ctx, 'player.view_player')
        return root.friends.filter(friends__id=root.id)

    @staticmethod
    def resolve_friend_requests(root, info):
        ctx = info.context
        require_login(ctx)
        p = ctx.user.player
        if p.id != root.id:
            require_perm(ctx, 'player.view_player')
        return root.friended_by.exclude(
            id__in=root.friends.only('id')
        )

    user = gh.Field(User, description="关联用户")

    @staticmethod
    def resolve_user(root, info):
        ctx = info.context
        require_login(ctx)
        u = ctx.user
        if u.id == root.user.id or require_perm(ctx, 'player.view_user'):
            return root.user


class Report(DjangoObjectType):
    class Meta:
        model = models.Report


class PlayerQuery(gh.ObjectType):
    user = gh.Field(
        User,
        id=gh.Int(description="用户ID"),
        phone=gh.String(description="手机号"),
        token=gh.String(description="登录令牌"),
        description="获取用户",
    )

    @staticmethod
    def resolve_user(root, info, id=None, phone=None, token=None):
        ctx = info.context
        require_perm(ctx, 'player.view_user')

        if id is not None:
            return models.User.objects.get(id=id)
        elif phone is not None:
            return models.User.objects.get(phone=phone)
        elif token is not None:
            return models.User.from_token(token)

        return None

    me = gh.Field(User, description="当前登录用户")

    @staticmethod
    def resolve_me(root, info, id=None, phone=None, token=None):
        u = info.context.user
        return u if u.is_authenticated else None

    player = gh.Field(
        Player,
        id=gh.Int(description="玩家ID"),
        name=gh.String(description="玩家昵称"),
        description="获取玩家",
    )

    @staticmethod
    def resolve_player(root, info, id=None, name=None):
        if id is not None:
            return models.Player.objects.get(id=id)
        elif name is not None:
            return models.Player.objects.get(name=name)

        return None

    players = gh.List(
        gh.NonNull(Player),
        keyword=gh.String(description="关键字"),
        description="查找玩家",
    )

    @staticmethod
    def resolve_players(root, info, keyword):
        return models.Player.objects.filter(name__contains=keyword)

    token = gh.String(description="获取登录令牌")

    @staticmethod
    def resolve_token(root, info):
        req = info.context
        u = req.user
        if u.is_authenticated:
            return u.token()
        else:
            return None


class Register(gh.Mutation):
    class Arguments:
        name     = gh.String(required=True, description="昵称")
        phone    = gh.String(required=True, description="手机")
        password = gh.String(required=True, description="密码")
        smscode  = gh.Int(required=True, description="短信验证码")

    token  = gh.String(required=True, description="登录令牌")
    user   = gh.Field(User, required=True, description="用户")
    player = gh.Field(Player, required=True, description="玩家")

    @staticmethod
    def mutate(root, info, name, phone, password, smscode):
        if models.User.objects.filter(phone=phone).exists():
            raise GraphQLError('手机已经注册')
        elif models.Player.objects.filter(name=name).exists():
            raise GraphQLError('昵称已经注册')
        elif not utils.leancloud.verify_smscode(phone, smscode):
            raise GraphQLError('验证码不正确')

        with transaction.atomic():
            try:
                u = models.User.objects.create_user(phone=phone, password=password)
                u.save()
                p = models.Player.objects.create(user=u, name=name)
                p.save()
            except Exception:
                import traceback
                traceback.print_exc()
                raise

        return Register(
            user=u, player=u.player,
            token=u.token(),
        )


class Login(object):
    @classmethod
    def Field(cls, **kw):
        return gh.Field(
            User,
            phone=gh.String(description="手机"),
            forum_id=gh.ID(description="论坛用户ID"),
            name=gh.String(description="昵称"),
            password=gh.String(required=True, description="密码"),
            resolver=cls.mutate,
            **kw,
        )

    @staticmethod
    def mutate(root, info, phone=None, forum_id=None, name=None, password=None):
        if not phone:
            return None

        u = auth.authenticate(phone=phone, password=password)
        if not u:
            return None

        auth.login(info.context, u)
        return u


class Update(object):
    @classmethod
    def Field(cls, **kw):
        return gh.Field(
            Player,
            # id=gh.ID(required=True, description="玩家ID"),
            bio=gh.String(description="签名"),
            avatar=gh.String(description="头像"),
            resolver=cls.mutate,
            **kw,
        )

    @staticmethod
    def mutate(root, info, bio=None, avatar=None):
        ctx = info.context
        require_login(ctx)
        p = ctx.user.player
        p.bio = bio or p.bio
        p.avatar = avatar or p.avatar
        p.save()
        return p


class BindForum(object):
    @classmethod
    def Field(cls, **kw):
        return gh.Field(
            Player,
            forum_id=gh.ID(required=True, description="论坛UID"),
            forum_password=gh.String(required=True, description="论坛密码"),
            **kw,
        )

    @staticmethod
    def mutate(root, info, forum_id, forum_password):
        raise GraphQLError('not impl')


class Friend(object):
    @classmethod
    def Field(cls, **kw):
        return gh.Boolean(
            id=gh.ID(required=True, description="目标玩家ID"),
            resolver=cls.mutate,
            **kw,
        )

    @staticmethod
    def mutate(root, info, id):
        ctx = info.context
        require_login(ctx)
        me = ctx.user.player
        p = models.Player.objects.get(id=id)
        if not p:
            raise GraphQLError('找不到相应的玩家')
        me.friends.add(p)
        return True


class Unfriend(object):
    @classmethod
    def Field(cls, **kw):
        return gh.Boolean(
            id=gh.ID(required=True, description="目标玩家ID"),
            resolver=cls.mutate,
            **kw,
        )

    @staticmethod
    def mutate(root, info, id):
        ctx = info.context
        require_login(ctx)
        me = ctx.user.player
        p = models.Player.objects.get(id=id)
        if not p:
            raise GraphQLError('找不到相应的玩家')
        me.friends.remove(p)
        p.friends.remove(me)
        return True


class Block(object):
    @classmethod
    def Field(cls, **kw):
        return gh.Boolean(
            id=gh.ID(required=True, description="目标玩家ID"),
            resolver=cls.mutate,
            **kw,
        )

    @staticmethod
    def mutate(root, info, id):
        raise GraphQLError('not impl')


class Unblock(object):
    @classmethod
    def Field(cls, **kw):
        return gh.Boolean(
            id=gh.ID(required=True, description="目标玩家ID"),
            resolver=cls.mutate,
            **kw,
        )

    @staticmethod
    def mutate(root, info, id):
        raise GraphQLError('not impl')


class ReportOp(object):
    @classmethod
    def Field(cls, **kw):
        return gh.Boolean(
            id=gh.ID(required=True, description="目标玩家ID"),
            reason=gh.ID(required=True, description="举报原因"),
            game_id=gh.ID(description="游戏ID（如果有）"),
            resolver=cls.mutate,
            **kw,
        )

    @staticmethod
    def mutate(root, info, id, reason, game_id=None):
        raise GraphQLError('not impl')


class PlayerOps(gh.ObjectType):
    login      = Login.Field(description="登录")
    register   = Register.Field(description="注册")
    update     = Update.Field(description="更新资料")
    bind_forum = BindForum.Field(description="绑定论坛帐号")
    friend     = Friend.Field(description="发起好友请求")
    unfriend   = Unfriend.Field(description="移除好友/拒绝好友请求")
    block      = Block.Field(description="拉黑")
    unblock    = Unblock.Field(description="解除拉黑")
    report     = ReportOp.Field(description="举报玩家")

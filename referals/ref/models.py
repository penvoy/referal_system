from django.db import models
from django.contrib.auth.models import User

class Refcode(models.Model):
    """
    Таблица: Реферальные коды

    :param
        code - код
        date_created - дата создания
        date_end - время истекания кода
        is_active - активный ли код
        user - пользователь, создавший код

    """
    code = models.CharField(blank=True, unique=True)
    date_created = models.FloatField(default=0, null=False)
    date_end = models.FloatField(default=0, null=False)
    is_active = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)


class Referrals(models.Model):
    """
    Таблица: Рефералы

    :param
        referrer - пользователь-реферер
        reffered - пользователь-реферал
    
    """
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='referrer_referrals')
    reffered = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='referred_referrals')


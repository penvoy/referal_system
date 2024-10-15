from django.conf import settings
from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes, authentication_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
import uuid
import time
from datetime import datetime
from loguru import logger

from .models import Refcode, Referrals
from .tasks import expire_code

@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
class RefcodeViewset(viewsets.ViewSet):
    queryset = Refcode.objects.all()

    @action(detail=False, methods=['post'])
    def create_code(self, request):
        """
        Метод для создания кода
        """

        if not request.data.get("expDate"):
            return Response("Не передан параметр истечения срока действия кода", status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(request.data['expDate'], (int, float)):
            return Response("неверный тип expDate", status=status.HTTP_400_BAD_REQUEST)

        if self.queryset.filter(user=request.user, is_active=True).exists():
            return Response("У данного пользователя уже существует активный код", status=status.HTTP_400_BAD_REQUEST)

        created = Refcode.objects.create(
            code=uuid.uuid4(),
            date_created=time.time(),
            date_end=request.data["expDate"],
            user=request.user,
            is_active=True
        )

        # Сохраняем код в Redis
        cache.set(request.user.email, created.code, timeout=int(float(request.data["expDate"]) - time.time()))

        # создаём объект datetime из expDate, чтобы передать в celery
        datetime_obj = datetime.fromtimestamp(int(float(request.data["expDate"])))

        # создаём задачу на запланированное время expDate, чтобы заэкспарить код
        expire_code.apply_async(args=[created.id], eta=datetime_obj)

        response = {
            "id": created.id,
            "code": created.code
        }
        return Response(response, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def destroy_code(self, request, pk=None):
        """
        Функция для удаления кода по его id
        """
        # получаем инстанс кода или 404
        refcode = get_object_or_404(self.queryset, pk=pk)

        # Удаляем код из Redis
        cache.delete(request.user.email)

        refcode.delete()
        return Response("", status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def retrieve_code(self, request):
        """
        Функция для получения кода по email создателя
        """
        if not request.data.get("email"):
            return Response("Не передан email", status=status.HTTP_400_BAD_REQUEST)
        
        email = request.data['email']

        # Попытка получить код из кэша
        cached_code = cache.get(email)
        if cached_code:
            return Response(cached_code, status=status.HTTP_200_OK)
        
        # если код не был найден в кэше, ищем в бд
        refcodes = self.queryset.select_related('user')
        for code in refcodes:
            if code.user.email == email:
                result = {"id": code.id, "code": code.code}
                return Response(result, status=status.HTTP_200_OK)

        return Response("Не найдено", status=status.HTTP_404_NOT_FOUND)


@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
class ReferalView(APIView):
    def get(self, request):
        """
        Функция для получения рефералов по id реферера
        """
        if not request.data.get("refferer_id"):
            return Response("Не передан id реферера", status=status.HTTP_400_BAD_REQUEST)

        list_of_refs = []

        # ищем рефералов
        referals = Referrals.objects.filter(
            referrer_id=request.data["refferer_id"]).select_related('reffered')

        # собираем
        for user in referals:
            list_of_refs.append(
                {
                    "id": user.reffered.id,
                    "username": user.reffered.username,
                    "email": user.reffered.email
                }
            )

        return Response(list_of_refs, status=status.HTTP_200_OK)



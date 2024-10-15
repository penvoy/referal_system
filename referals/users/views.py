from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes

from .serializers import UserSerializer
from ref.models import Refcode, Referrals


@permission_classes([AllowAny])
class RegisterView(APIView):
    def post(self, request):
        """
        Метод для регистрации пользователей
        """
        # сериализуем входные данные
        serializer = UserSerializer(data=request.data)

        # в случае валидности, сохраняем пользователя
        if serializer.is_valid():
            user = serializer.save()
            if user:
                json = serializer.data
                json['id'] = user.id
                return Response(json, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class ReferalRegisterView(APIView):
    def post(self, request):
        """
        Метод для регистрации пользователей с использованием реферального кода
        """
        if not request.data.get("refcode"):
            return Response("не передан реферальный код", status=status.HTTP_400_BAD_REQUEST)

        # получаем инстанс кода
        code = Refcode.objects.filter(code=request.data['refcode']).first()

        # выводим ошибку, если код не найден
        if not code:
            return Response("не найден реферальный код", status=status.HTTP_404_NOT_FOUND)

        # сериализуем данные 
        serializer = UserSerializer(data=request.data)
        
        # если данные валидны, то сохраняем пользователя
        if serializer.is_valid():
            user = serializer.save()
            if user:
                # создаем запись в таблице рефералов
                try:
                    Referrals.objects.create(
                        reffered=user,
                        referrer=code.user
                    )
                except Exception as e:
                    return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

                json = serializer.data
                json['id'] = user.id
                return Response(json, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


   

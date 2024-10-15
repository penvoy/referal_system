from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from users.views import RegisterView, ReferalRegisterView
from ref.views import RefcodeViewset, ReferalView


schema_view = get_schema_view(
    openapi.Info(
        title="ReferalApp API",
        default_version='v1',
        description="API documentation for my project",
    ),
    public=True,
)

router = routers.DefaultRouter()
router.register(r'api', RefcodeViewset)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/obtain', TokenObtainPairView.as_view(), name='token_obtain'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/referals', ReferalView.as_view(), name='referals'),
    path('', include(router.urls)), 
    path('register', RegisterView.as_view(), name='register'),
    path('refregister', ReferalRegisterView.as_view(), name='refregister'),
]

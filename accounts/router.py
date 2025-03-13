from rest_framework import routers
from .views import UserViewSet

app_name = "accounts"

router = routers.DefaultRouter()
router.register('user',UserViewSet)
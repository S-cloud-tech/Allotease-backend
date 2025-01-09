from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from . import serializers
from .models import Account

# Create your views here.
class RegisterView(generics.GenericAPIView):
    serializer_class = serializers.RegisterSerializer
    
    def  post(self, request):
        user = request.data
        serializers = self.serializer_class(data=user)
        serializers.is_valid(raise_exception=True)
        serializers. save()

        user_data = serializers.data
        user = Account.objects.get(email=user_data['email'])
        
        token = RefreshToken.for_user(user)

        return Response(user_data, status=status.HTTP_201_CREATED)
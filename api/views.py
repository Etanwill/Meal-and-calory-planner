from django.shortcuts import render
from rest_framework import viewsets
from .serializers import UserSerializer
from counter.models import CustomUser






class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()# api views uses all users in database
    serializer_class = UserSerializer # 

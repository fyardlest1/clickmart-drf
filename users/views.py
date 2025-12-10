from django.shortcuts import render

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import UserRegisterSerializer, UserSerializer


# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):    
    permission_classes = [IsAuthenticated] # check if the user is authenticated
    def get(self, request):
        # check the login user
        # print(f'user: {request.user}')
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # PATCH = partial update → only updates provided fields
    def  patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # check the login user
            # print(f'user: {request.user.first_name}')
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




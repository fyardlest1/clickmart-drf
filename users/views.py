from django.shortcuts import render

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema

from .serializers import UserRegisterSerializer, UserSerializer


# Create your views here.
class RegisterView(APIView):
    """User Registration Endpoint"""
    
    @extend_schema(
        tags=['Users'],
        summary="Register a new user",
        description="Create a new user account."
    )
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    """User Profile Endpoint""" 
    
    permission_classes = [IsAuthenticated] # check if the user is authenticated
    @extend_schema(
        tags=['Users'],
        summary="Get or update user profile",
        description="Retrieve or update the profile of the currently logged-in user."
    )
    def get(self, request):
        # check the login user
        # print(f'user: {request.user}')
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # PATCH = partial update → only updates provided fields
    @extend_schema(
        tags=['Users'],
        summary="Update user profile",
        description="Partially update the profile of the currently logged-in user."
    )
    def  patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # check the login user
            # print(f'user: {request.user.first_name}')
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




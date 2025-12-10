from rest_framework import serializers
from .models import User
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    # password should not sent back (in the response) when creating a user
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password']
    
    # tell django to create the user
    # this will automatically hash the password
    def create(self, validate_data):
        user = User.objects.create_user(**validate_data)
        # user = user.objects.create_user(
        #     validate_data['username'],
        #     validate_data['email'],
        #     validate_data['password'],            
        # )
        return user
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']





# test
# {
# "username": "yayad",
# "password": "Pass@123",
# "email": "yayad@gmail.com"
# }
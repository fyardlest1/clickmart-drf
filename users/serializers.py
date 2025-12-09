from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()



class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password']
        
    def create(self, validate_data):
        user = User.objects.create_user(**validate_data)
        return user
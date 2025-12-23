# views.py
# clickmart_main/views.py

from django.shortcuts import render

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    post=extend_schema(
        tags=['Authentication'],
        summary="Login (Get Token)",
        description="Takes a set of user credentials and returns an access and refresh JSON web token pair to prove the authentication of those credentials."
    )
)
# Customizing the TokenObtainPairView to add schema information
class CustomTokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema_view(
    post=extend_schema(
        tags=['Authentication'],
        summary="Refresh Token",
        description="Takes a refresh type JSON web token and returns an access type JSON web token if the refresh token is valid."
    )
)
# Customizing the TokenRefreshView to add schema information
class CustomTokenRefreshView(TokenRefreshView):
    pass

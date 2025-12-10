from django.urls import path
from users import views as UserView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('register/', UserView.RegisterView.as_view()),
    # include routes for Simple JWT’s
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # users api
    path('profile/', UserView.ProfileView.as_view()), 
    # products api
    # path('products/', )
    
]
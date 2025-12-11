from django.urls import path
from users import views as UserViews
from products import views as ProdViews

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('register/', UserViews.RegisterView.as_view()),
    # include routes for Simple JWT’s
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # users api
    path('profile/', UserViews.ProfileView.as_view()), 
    # products APIs
    path("products/", ProdViews.ProductListView.as_view(), name="product-list"),
    path("products/<uuid:id>/", ProdViews.ProductDetailView.as_view(), name="product-detail"),
    
]
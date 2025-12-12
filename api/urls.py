from django.urls import path
from users import views as UserViews
from products import views as ProdViews
from carts import views as CartViews

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
    # carts APIs
    path("cart/", CartViews.CartDetailView.as_view(), name="cart-detail"),
    path("cart/add/", CartViews.AddToCartView.as_view(), name="cart-add"),
    path("cart/item/<uuid:id>/", CartViews.UpdateCartItemView.as_view(), name="cart-item-update"),
    path("cart/item/<uuid:id>/delete/", CartViews.RemoveCartItemView.as_view(), name="cart-item-delete"),
]
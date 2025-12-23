from django.urls import path
from users import views as UserViews
from products import views as ProdViews
from carts import views as CartViews
from orders import views as OrderViews

# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )

from .views import CustomTokenObtainPairView, CustomTokenRefreshView


urlpatterns = [
    path('register/', UserViews.RegisterView.as_view()),
    
    # include routes for Simple JWT’s
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    
    # users api
    path('profile/', UserViews.ProfileView.as_view()), 
    
    # products APIs
    path("products/", ProdViews.ProductListView.as_view(), name="product-list"),
    path("products/<uuid:id>/", ProdViews.ProductDetailView.as_view(), name="product-detail"),
    
    # carts APIs
    path("cart/", CartViews.CartView.as_view(), name="cart-view"),
    # Add to Cart
    path("cart/add/", CartViews.AddToCartView.as_view(), name="cart-add"),
    # Manage Cart
    path('cart/items/<uuid:item_id>/', CartViews.ManageCartItemView.as_view(), name='cart-manage-item'),
    # path("cart/items/<uuid:item_id>/", CartViews.CartItemDetailView.as_view(), name="cart-item-detail"),

    # orders APIs
    path("orders/place/", OrderViews.PlaceOrderView.as_view(), name="order-place"),
    path("orders/", OrderViews.CustomerOrderView.as_view(), name="order-list"),
    path("orders/<uuid:id>/", OrderViews.OrderDetailView.as_view(), name="order-detail"),
]
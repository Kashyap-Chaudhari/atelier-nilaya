from django.urls import path
from .views import (
    api_get_cart,
    api_add_to_cart,
    api_update_cart_item,
    api_remove_cart_item,
    api_merge_guest_cart,
)

app_name = 'cart'

urlpatterns = [
    path('add/', api_add_to_cart, name='add'),
    path('add', api_add_to_cart, name='add_noslash'),
    path('api/state/', api_get_cart, name='api_state'),
    path('api/add/', api_add_to_cart, name='api_add'),
    path('api/update/', api_update_cart_item, name='api_update'),
    path('api/remove/', api_remove_cart_item, name='api_remove'),
    path('api/merge/', api_merge_guest_cart, name='api_merge'),
]

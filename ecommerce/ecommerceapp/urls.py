from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name="index"),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    path('contact',views.contact,name="contact"),
    # path('about',views.about,name="about"),
    path('profile',views.profile,name="profile"),
    path('checkout/', views.checkout, name="Checkout"),
    path('handlerequest/', views.handlerequest, name="HandleRequest"),

]

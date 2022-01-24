"""DailyFresh URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from user import urls as user_urls
from order import urls as order_urls
from goods import urls as goods_urls
from cart import urls as cart_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include(user_urls, namespace='user')),  # 用户模块
    path('order/', include(order_urls, namespace='order')),  # 订单模块
    path('cart/', include(cart_urls, namespace='cart')),  # 购物车模块
    path('', include(goods_urls, namespace='goods')),  # 商品模块
    path('tinymce/', include('tinymce.urls')),  # 富文本编辑器
]

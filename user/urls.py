#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :urls.py
# @Time      :2022/1/24 15:58
# @Author    :Andy
from django.urls import path
from user.views import (LoginView, RegisterView, LoginOutView, UserOrderView, UserAddressView, UserInfoView)
from django.urls import re_path
# from django.contrib.auth.decorators import login_required

app_name = 'user'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),  # 登录页面
    path('register/', RegisterView.as_view(), name='register'),  # 注册页面
    path('logout/', LoginOutView.as_view(), name='logout'),  # 登出页面
    re_path('^order/(?P<page>\d+)', UserOrderView.as_view(), name='order'),  # 用户中心-订单
    re_path('^$', UserInfoView.as_view(), name='user'),  # 用户中心-信息
    path('address/', UserAddressView.as_view(), name='address'),  # 用户中心-地址
]

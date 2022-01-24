#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :urls.py
# @Time      :2022/1/24 15:57
# @Author    :Andy
from django.urls import path
from goods import views
app_name = 'goods'

urlpatterns = [
    path('', views.index, name='index'),
]
from django.shortcuts import render


def index(request):
    """首页"""
    return render(request, 'df_goods/index.html')
    # return render(request, 'fm_goods/index.html')

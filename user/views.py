from django.shortcuts import render, redirect
from django.views.generic import View
from django.urls import reverse
from django.http import HttpResponse
import re
from user.models import User, Address
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from DailyFresh import settings
from django.core.mail import send_mail
from itsdangerous import SignatureExpired
# from celery_tasks.task import send_register_active_email
from django.contrib.auth import authenticate, login, logout
from utils.mixin import LoginRequireMixin
from django_redis import get_redis_connection
from goods.models import GoodsSKU
from order.models import OrderInfo, OrderGoods
from django.http import JsonResponse
from django.core.paginator import Paginator


# /user/register
class RegisterView(View):
    """注册页面"""

    def get(self, request):
        """获取注册页面"""

        return render(request, 'df_user/register.html')

    def post(self, request):
        """注册处理"""
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')

        # 进行数据校验
        if not all([username, password, email]):
            return render(request, 'df_user/register.html', {'error': '数据不完整'})

        # 邮箱校验
        if not re.match(r'[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'df_user/register.html', {'error': '邮箱格式不正确'})

        # 检测用户名是否重复
        try:
            user = User.objects.get(username=username, password=password)
        except User.DoesNotExist:
            # 用户名不存在
            user = None

        if user:
            # 用户名存在
            return render(request, 'df_user/register.html', {'error': '用户名已存在'})

        # 业务处理进行注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 1
        user.save()

        # 生成激活连接
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info).decode('utf-8')

        # 发送邮件
        username = user.username
        # msg = '<h1>%s,欢迎注册，请点击下方连接激活</h1><a href="http://127.0.0.1:7890/user/active/%s">http://127.0.0.1:7890/user/active/%s</a>' % (
        #     username, token, token)
        # sender = '291075564@qq.com'
        # subject = 'django项目，注册激活F'
        # send_mail(subject, msg, sender, ['root_pei@163.com'], html_message=msg, )
        # 将邮件放到broker去做
        # send_register_active_email.delay(username, token)

        # 注册完跳转到首页
        return redirect(reverse('goods:index'))

# /user/login
# class LoginView(View):
#     """登录页面"""
#
#     def get(self, request):
#         if 'username' in request.COOKIES:
#             username = request.COOKIES['username']
#         else:
#             username = ''
#         return render(request, 'df_user/login.html', {'username': username})
#
#     def post(self, request):
#         username = request.POST.get('username')
#         password = request.POST.get('pwd')
#         if not all([username, password]):
#             return render(request, 'df_user/login.html', {'error': '请填写账号或密码'})
#         user = authenticate(username=username, password=password)
#         if user is not None:
#             # 用户密码正确
#             # 是否激活
#             if user.is_active:
#                 login(request, user)
#                 # 判断是否记住账号
#                 next_url = request.GET.get('next', reverse('goods:index'))
#                 response = redirect(next_url)
#                 remember = request.POST.get('remember')
#                 if remember == 'on':
#                     response.set_cookie('username', username, max_age=60)
#                 else:
#                     response.delete_cookie('username')
#                 return response
#             else:
#                 return render(request, 'df_user/login.html', {'error': '用户未激活'})
#         else:
#             return render(request, 'df_user/login.html', {'error': '账号或密码错误'})


class LoginView(View):
    """登录"""
    def get(self, request):
        # 显示登录页面
        # 判断是否记住密码
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')  # request.COOKIES['username']
            checked = 'checked'
        else:
            username = ''
            checked = ''

        return render(request, 'df_user/login.html', {'username': username, 'checked': checked})

    def post(self, request):
        # 接受数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        # remember = request.POST.get('remember')  # on

        # 校验数据
        if not all([username, password]):
            return render(request, 'df_user/login.html', {'errmsg': '数据不完整'})

        # 业务处理: 登陆校验
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                # print("User is valid, active and authenticated")
                login(request, user)  # 登录并记录用户的登录状态

                # 获取登录后所要跳转到的地址, 默认跳转首页
                next_url = request.GET.get('next', reverse('goods:index'))

                #  跳转到next_url
                response = redirect(next_url)  # HttpResponseRedirect

                # 设置cookie, 需要通过HttpReponse类的实例对象, set_cookie
                # HttpResponseRedirect JsonResponse

                # 判断是否需要记住用户名
                remember = request.POST.get('remember')
                if remember == 'on':
                    response.set_cookie('username', username, max_age=7*24*3600)
                else:
                    response.delete_cookie('username')

                # 回应 response
                return response

            else:
                # print("The passwoed is valid, but the account has been disabled!")
                return render(request, 'df_user/login.html', {'errmsg': '账户未激活'})
        else:
            return render(request, 'df_user/login.html', {'errmsg': '用户名或密码错误'})


# /user/logout
class LoginOutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('goods:index'))


class IndexView(View):
    def get(self, request):
        return render(request, 'df_user/index.html')


# /user/
class UserInfoView(LoginRequireMixin, View):
    """用户中心信息页"""

    def get(self, request):
        user = request.user
        address = Address.objects.get_default_address(user)

        # 获取用户历史浏览信息
        # from redis import StrictRedis
        # sr = StrictRedis(host='172.16.179.130', port=6379, db=2)
        con = get_redis_connection('default')

        history_key = 'history_%d' % user.id

        # 获取用户最近浏览的5个商品
        sku_ids = con.lrange(history_key, 0, 4)

        # # 从数据库中查询用户浏览的商品的具体信息
        # goods_li = GoodsSKU.objects.filter(id__in=sku_ids)
        #
        # goods_res = []
        # for a_id in sku_ids:
        #     for goods in goods_li:
        #         if a_id == goods.id:
        #             goods_res.append(goods)

        # 遍历获取用户浏览的历史商品信息
        goods_li = []
        for id in sku_ids:
            goods = GoodsSKU.objects.get(id=id)
            goods_li.append(goods)

        context = {'address': address,
                   'goods_li': goods_li}

        return render(request, 'df_user/user_center_info.html', context)


# user/order/page
class UserOrderView(LoginRequireMixin, View):
    def get(self, request, page):
        user = request.user
        orders = OrderInfo.objects.filter(user=user).order_by('-create_time')
        if not user.is_authenticated:
            return JsonResponse({'code': 403, 'msg': '用户未登录'})
        for order in orders:
            order_skus = OrderGoods.objects.filter(order_id=order.order_id)
            order.status_name = OrderInfo.ORDER_STATUS[order.order_status]
            for order_sku in order_skus:
                # 计算小计
                amonut = order_sku.price * order_sku.count
                order_sku.amount = amonut
            # 动态添加属性
            order.order_skus = order_skus

        # 分页
        paginator = Paginator(orders, 1)
        # 获取页面
        try:
            page = int(page)
        except Exception as e:
            page = 1
        if page > paginator.num_pages:
            page = 1
        order_page = paginator.page(page)

        # todo: 进行页码的控制，页面上最多显示5个页码
        # 1. 总数不足5页，显示全部
        # 2. 如当前页是前3页，显示1-5页
        # 3. 如当前页是后3页，显示后5页
        # 4. 其他情况，显示当前页的前2页，当前页，当前页的后2页
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)

        context = {
            'order_page': order_page,
            'pages': pages
        }
        return render(request, 'df_user/user_center_order.html', context)


class UserAddressView(View):
    """用户中心-地址"""

    def get(self, request):
        user = request.user
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     address = None
        # 上面try用了下面的封装
        address = Address.objects.get_default_address(user=user)
        return render(request, 'df_user/user_center_site.html', {'address': address})
        # return render(request, 'df_user/user_center_site.html',
        #           {'title': '用户中心-收货地址', 'page': 'address', 'address': address})

    def post(self, request):
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        # 判断填写信息是否为空
        if not all([receiver, addr, phone]):
            return render(request, 'df_user/user_center_site.html', {'error': '请填写相关信息'})

        # 判断手机号格式
        if not re.match(r'^1[3|4|5|6|7|8|9][0-9]{9}$', phone):
            return render(request, 'df_user/user_center_site.html', {'error': '手机号格式不正确'})

        user = request.user
        # 查询是否有默认地址
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     address = None
        address = Address.objects.get_default_address(user=user)
        # 如果有默认地址就将is_default设置None,表示新增地址时不设置为默认地址
        if address:
            is_default = False
        else:
            is_default = True

        Address.objects.create(
            user=user,
            receiver=receiver,
            addr=addr,
            zip_code=zip_code,
            phone=phone,
            is_default=is_default
        )
        # 返回应答
        return redirect(reverse('user:address'))

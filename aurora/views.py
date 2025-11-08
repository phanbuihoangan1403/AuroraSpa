from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm
from aurora.models import Blog, DichVu

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # đăng nhập luôn sau khi tạo
            return redirect('home')
        else:
            messages.error(request, "Thông tin chưa hợp lệ, vui lòng kiểm tra.")
    else:
        form = RegisterForm()

    return render(request, 'auth/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user:
            login(request, user)
            return redirect('home')  # đổi sang trang chủ của bạn
        messages.error(request, "Sai tài khoản hoặc mật khẩu.")
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')
# Create your views here.
from django.http import HttpResponse

def home_view(request):
    return render(request, 'pages/home.html')

def blog_view(request):
    posts = Blog.objects.filter(TrangThaiHienThi=True).order_by('-NgayDang')
    return render(request, 'pages/blog.html', {'posts': posts})

def dichvu_view(request):
    posts=DichVu.objects.filter(TrangThaiHienThi=True)
    return render(request, 'pages/dichvu.html',{'posts': posts} )

def lichhen_view(request):
    return render(request, 'pages/lichhen.html')

def faq_view(request):
    return render(request, 'pages/faq.html')

def lienhe_view(request):
    return render(request, 'pages/lienhe.html')

def chitietblog_view(request):
    return render(request, 'pages/chitietblog.html')
def chitietdichvu_view(request):
    return render(request, 'pages/chitietdichvu.html')
@login_required
def profile_view(request):
    return render(request, 'pages/profile.html')


@login_required
def diem_view(request):
    return render(request, 'pages/diem.html')


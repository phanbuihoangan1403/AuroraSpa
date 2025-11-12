from django.shortcuts import render
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm
from django.utils.timezone import localtime
from aurora.models import Blog, DichVu, KhachHang, DiemTichLuy, LichSuTichDiem, FAQ, DanhMucDichVu

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
    dichvu_list = DichVu.objects.filter(TrangThaiHienThi=True).order_by('MaDichVu')[:10]

    # Lấy 10 bài blog hiển thị
    blog_list = Blog.objects.filter(TrangThaiHienThi=True).order_by('-NgayDang')[:10]

    return render(request, 'pages/home.html', {
        'dichvu_list': dichvu_list,
        'blog_list': blog_list,
    })

def blog_view(request):
    # Lấy các bài viết có trạng thái hiển thị
    posts_list = Blog.objects.filter(TrangThaiHienThi=True).order_by('-NgayDang')

    # Phân trang: 4 bài mỗi trang
    paginator = Paginator(posts_list, 4)

    # Lấy số trang hiện tại từ URL (?page=2)
    page_number = request.GET.get('page')

    # Lấy danh sách bài của trang hiện tại
    posts = paginator.get_page(page_number)

    return render(request, 'pages/blog.html', {'posts': posts})

def dichvu_view(request, madanhmuc=None):
    # Lấy toàn bộ danh mục
    danhmuc = DanhMucDichVu.objects.all()

    # Lấy các dịch vụ theo danh mục
    data = []
    for dm in danhmuc:
        dichvu = DichVu.objects.filter(MaDanhMuc=dm, TrangThaiHienThi=True)
        data.append({
            'danhmuc': dm,
            'dichvu': dichvu
        })

    return render(request, 'pages/dichvu.html', {'data': data})


def lichhen_view(request):
    return render(request, 'pages/lichhen.html')

def faq_view(request):
    faqs = FAQ.objects.filter(TrangThaiHienThi=True).order_by('NgayCapNhat')
    return render(request, 'pages/faq.html', {'faqs': faqs})

def lienhe_view(request):
    return render(request, 'pages/lienhe.html')

def chitietblog_view(request,pk):
    blog = get_object_or_404(Blog, MaBaiViet=pk)
    return render(request, 'pages/chitietblog.html', {'blog': blog})
def chitietdichvu_view(request, madanhmuc, madichvu):
    danhmuc = get_object_or_404(DanhMucDichVu, MaDanhMuc=madanhmuc)
    dichvu = get_object_or_404(DichVu, MaDichVu=madichvu, MaDanhMuc=danhmuc)

    return render(request, 'pages/chitietdichvu.html', {
        'dichvu': dichvu,
        'danhmuc': danhmuc,
    })
@login_required
def profile_view(request):
    khachhang = KhachHang.objects.filter(user=request.user).first()
    return render(request, 'pages/profile.html', {'khachhang': khachhang})


@login_required
def diem_view(request):
    # Lấy thông tin khách hàng theo user đang đăng nhập
    kh = get_object_or_404(KhachHang, user=request.user)

    # Lấy tổng điểm hiện có
    diem = DiemTichLuy.objects.get(MaKhachHang=kh)

    # Lịch sử tích điểm
    history = (
        LichSuTichDiem.objects
        .filter(MaKhachHang=kh)
        .order_by("-NgayGiaoDich")
    )

    # Tính điểm còn lại sau mỗi giao dịch để hiển thị như hình mẫu
    running_balance = diem.SoDiemHienTai
    rows = []
    for tx in history:
        rows.append({
            "date": localtime(tx.NgayGiaoDich),
            "detail": tx.ChiTietGiaoDich,
            "delta": tx.SoDiemThayDoi,
            "balance_after": running_balance
        })
        running_balance -= tx.SoDiemThayDoi

    context = {
        "kh": kh,
        "diem": diem,
        "rows": rows,
        "joined": request.user.date_joined,
    }

    return render(request, "pages/diem.html", context)


from django.shortcuts import render
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm
from django.utils.timezone import localtime
from aurora.models import Blog, DichVu, KhachHang, DiemTichLuy, LichSuTichDiem, FAQ, DanhMucDichVu

from django.http import JsonResponse #JAVA
from django.views import View #JAVA
from .models import DichVu, KhachHang, LichHen  # JAVA
from .forms import DatLichForm #ĐẶT LỊCH

### LICH HEN
## Lưu lịch hẹn
def save_appointment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Lấy thông tin từ request
            HoTen = data.get('hoten')
            Email = data.get('email')
            DienThoai = data.get('sdt')
            DanhMucDichVu = data.get('danhmuc')
            DichVu = data.get('dichvu')
            NgayHen = data.get('ngay')  # định dạng "YYYY-MM-DD"
            KhungGio = data.get('gio')
            MaGiamGia = data.get('magiamgia', '')

            # Kiểm tra bắt buộc
            if not all([ho_ten, email, sdt, dich_vu_id, ngay, khung_gio]):
                return JsonResponse({'success': False, 'error': 'Thiếu dữ liệu bắt buộc'})

            # Lấy dịch vụ và danh mục
            dich_vu = DichVu.objects.get(id=dich_vu_id)
            danh_muc = DanhMucDichVu.objects.get(id=danh_muc_id) if danh_muc_id else None

            # Lưu lịch hẹn
            lich_hen = LichHen.objects.create(
                HoTen=HoTen,
                Email=Email,
                DienThoai=DienThoai,
                DanhMucDichVu=DanhMucDichVu,
                DichVu=DichVu,
                NgayHen=NgayHen.strptime(ngay, "%Y-%m-%d").date(),
                KhungGio=KhungGio,
                MaGiamGia=MaGiamGia
            )

            return JsonResponse({'success': True, 'message': 'Đặt lịch thành công!', 'MaLichHen': lich_hen.MaLichHen})

        except DichVu.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Dịch vụ không tồn tại'})
        except DanhMucDichVu.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Danh mục không tồn tại'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

## Lấy khung giờ còn trống
ALL_TIME_SLOTS = ["08:00 - 10:00","10:00 - 12:00", "13:00 - 15:00", "15:00 - 17:00", "17:00 - 19:00", "19:00 - 21:00"]
def available_time_slots(request):
    selected_date = request.GET.get('date')

    if not selected_date:
        return JsonResponse({'error': 'Chưa chọn ngày'}, status=400)

    # Lấy danh sách giờ đã đặt cho ngày đó
    booked_times = LichHen.objects.filter(NgayHen=selected_date).values_list('KhungGio', flat=True)
    booked_times_str = [t.strftime("%H:%M") for t in booked_times]

    # Lọc ra các khung giờ còn trống
    available_times = [t for t in ALL_TIME_SLOTS if t not in booked_times_str]

    return JsonResponse({'available_times': available_times})

def lichhen_view(request):
    khachhang, created = KhachHang.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = DatLichForm(request.POST)
        if form.is_valid():
            lich = form.save(commit=False)
            kh = KhachHang.objects.get(user=request.user)
            lich.MaKhachHang = kh
            lich.MaDichVu = form.cleaned_data['dich_vu']
            lich.MaNhanVien = None  # tạm để None, admin sẽ gán sau
            lich.NgayDatLich = request.POST.get('ngay_dat') + ' 00:00:00'  # hoặc dùng datetime
            lich.NgayHen = request.POST.get('ngay_dat') + ' ' + request.POST.get('khung_gio')
            lich.save()
            messages.success(request, "Đặt lịch thành công!")
            return redirect('lichhen')
        else:
            messages.error(request, "Vui lòng kiểm tra lại thông tin.")
    else:
        form = DatLichForm()

    danh_muc_list = DanhMucDichVu.objects.all()
    return render(request, 'pages/lichhen.html', {
        'form': form,
        'danh_muc_list': danh_muc_list,
        'ma_khach_hang': KhachHang.objects.get(user=request.user).MaKhachHang
    })

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

@login_required
def lichsu_lichhen_view(request):
    # appointments = LichHen.objects.filter(user=request.user).order_by('-ngay_dat')
    appointments = []
    return render(request, 'lichsu_lichhen.html', {'appointments': appointments})

#THÊM AJAX VIEW
class LayDichVuView(View):
    def get(self, request):
        dm_id = request.GET.get('danh_muc')
        dv = DichVu.objects.filter(MaDanhMuc_id=dm_id).values('MaDichVu', 'TenDichVu')
        return JsonResponse(list(dv), safe=False)
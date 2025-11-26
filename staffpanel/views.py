from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction, models
from django.db.models import F
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q
from aurora.models import (
    NhanVien, FAQ, Blog, DichVu, LichHen,
    KhachHang, DiemTichLuy, LichSuTichDiem, DanhMucDichVu
)
from .models import NhatKyHoatDong
from .forms import (
    StaffLoginForm, StaffRegisterForm,UserProfileForm,StaffProfileForm,
    FAQForm, BlogForm, DichVuForm, LichHenForm,
    KhachHangForm, DiemTichLuyForm
)
from .permissions import manager_required, content_required, reception_required, staff_required
# ====================== THÊM 2 DÒNG IMPORT AJAX ======================
from django.http import JsonResponse
from django.views.decorators.http import require_GET


# ========== AUTH ==========

def staff_login(request):
    if request.user.is_authenticated and hasattr(request.user, 'nhanvien'):
        return redirect('staff_dashboard')

    if request.method == 'POST':
        form = StaffLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not hasattr(user, 'nhanvien'):
                messages.error(request, "Tài khoản này không thuộc nhân viên Aurora.")
            else:
                login(request, user)
                return redirect('staff_dashboard')
    else:
        form = StaffLoginForm(request)

    return render(request, 'staffpanel/auth_login.html', {'form': form})


@login_required
def staff_logout(request):
    logout(request)
    return redirect('staff_login')


@manager_required
def staff_register(request):
    if request.method == 'POST':
        form = StaffRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tạo tài khoản nhân viên thành công.")
            return redirect('staff_employee_list')
    else:
        form = StaffRegisterForm()
    return render(request, 'staffpanel/auth_register.html', {'form': form})


@login_required
def staff_profile(request):
    nv = request.user.nhanvien
    if request.method == 'POST':
        nv_form = StaffProfileForm(request.POST, instance=nv)
        user_form = UserProfileForm(request.POST, instance=request.user)
        if nv_form.is_valid() and user_form.is_valid():
            nv_form.save()
            user_form.save()
            messages.success(request, "Cập nhật hồ sơ thành công.")
            return redirect('staff_profile')
    else:
        nv_form = StaffProfileForm(instance=nv)
        user_form = UserProfileForm(instance=request.user)

    return render(request, 'staffpanel/auth_profile.html', {
        'nv_form': nv_form,
        'user_form': user_form,
        'nv': nv,
    })


# ========== DASHBOARD ==========

@login_required
def staff_dashboard(request):
    nv = request.user.nhanvien

    ctx = {
        'nv': nv,
        'tong_faq': FAQ.objects.count(),
        'tong_blog': Blog.objects.count(),
        'tong_dich_vu': DichVu.objects.count(),
        'tong_lich_hen': LichHen.objects.count(),
        'tong_khach_hang': KhachHang.objects.count(),
        'nhan_vien_online': NhanVien.objects.filter(is_online=True),
        'log_gan_day': NhatKyHoatDong.objects.select_related('nhan_vien')[:10],
    }
    return render(request, 'staffpanel/dashboard.html', ctx)


# ========== FAQ (CONTENT + MANAGER) ==========

@content_required
def staff_faq_list(request):
    q = request.GET.get('q', '')
    faqs = FAQ.objects.all().order_by('MaCauHoi')
    if q:
        faqs = faqs.filter(CauHoi__icontains=q)

    return render(request, 'staffpanel/faq_list.html', {
        'faqs': faqs,
        'q': q,
    })


@content_required
def staff_faq_edit(request, pk=None):
    if pk:
        faq = get_object_or_404(FAQ, pk=pk)
        action = "Sửa FAQ"
    else:
        faq = FAQ()
        action = "Tạo FAQ"

    if request.method == 'POST':
        form = FAQForm(request.POST, instance=faq)
        if form.is_valid():
            faq = form.save(commit=False)
            faq.MaNhanVien = request.user.nhanvien
            faq.save()

            NhatKyHoatDong.objects.create(
                nhan_vien=request.user.nhanvien,
                hanh_dong=action,
                doi_tuong='FAQ',
                object_id=faq.MaCauHoi,
                mo_ta=faq.CauHoi[:200]
            )

            messages.success(request, "Lưu FAQ thành công.")
            return redirect('staff_faq_list')
    else:
        form = FAQForm(instance=faq)

    return render(request, 'staffpanel/faq_form.html', {'form': form, 'faq': faq})


@content_required
def staff_faq_delete(request, pk):
    faq = get_object_or_404(FAQ, pk=pk)
    if request.method == 'POST':
        ma = faq.MaCauHoi
        title = faq.CauHoi
        faq.delete()
        NhatKyHoatDong.objects.create(
            nhan_vien=request.user.nhanvien,
            hanh_dong="Xóa FAQ",
            doi_tuong='FAQ',
            object_id=ma,
            mo_ta=title[:200]
        )
        messages.success(request, "Đã xóa FAQ.")
        return redirect('staff_faq_list')
    return render(request, 'staffpanel/confirm_delete.html', {'object': faq, 'title': faq.CauHoi})


# ========== BLOG (CONTENT + MANAGER) ==========

@content_required
def staff_blog_list(request):
    q = request.GET.get('q', '')
    blogs = Blog.objects.all().order_by('-NgayCapNhat')
    if q:
        blogs = blogs.filter(TieuDeBaiViet__icontains=q)
    return render(request, 'staffpanel/blog_list.html', {'blogs': blogs, 'q': q})


@content_required
def staff_blog_edit(request, pk=None):
    if pk:
        blog = get_object_or_404(Blog, pk=pk)
        action = "Sửa bài viết"
    else:
        blog = Blog()
        action = "Tạo bài viết"

    if request.method == 'POST':
        form = BlogForm(request.POST, instance=blog)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.MaNhanVien = request.user.nhanvien
            blog.save()

            NhatKyHoatDong.objects.create(
                nhan_vien=request.user.nhanvien,
                hanh_dong=action,
                doi_tuong='Blog',
                object_id=blog.MaBaiViet,
                mo_ta=blog.TieuDeBaiViet[:200]
            )
            messages.success(request, "Lưu bài viết thành công.")
            return redirect('staff_blog_list')
    else:
        form = BlogForm(instance=blog)

    return render(request, 'staffpanel/blog_form.html', {'form': form, 'blog': blog})


@content_required
def staff_blog_delete(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        ma = blog.MaBaiViet
        title = blog.TieuDeBaiViet
        blog.delete()
        NhatKyHoatDong.objects.create(
            nhan_vien=request.user.nhanvien,
            hanh_dong="Xóa bài viết",
            doi_tuong='Blog',
            object_id=ma,
            mo_ta=title[:200]
        )
        messages.success(request, "Đã xóa bài viết.")
        return redirect('staff_blog_list')
    return render(request, 'staffpanel/confirm_delete.html', {'object': blog, 'title': blog.TieuDeBaiViet})


# ========== DỊCH VỤ (CONTENT + MANAGER) ==========

@content_required
def staff_service_list(request):
    q = request.GET.get('q', '')
    dv = DichVu.objects.select_related('MaDanhMuc').all()
    if q:
        dv = dv.filter(TenDichVu__icontains=q)
    return render(request, 'staffpanel/service_list.html', {'services': dv, 'q': q})


@content_required
def staff_service_edit(request, pk=None):
    if pk:
        dv = get_object_or_404(DichVu, pk=pk)
        action = "Sửa dịch vụ"
    else:
        dv = DichVu()
        action = "Tạo dịch vụ"

    if request.method == 'POST':
        form = DichVuForm(request.POST, instance=dv)
        if form.is_valid():
            dv = form.save()

            NhatKyHoatDong.objects.create(
                nhan_vien=request.user.nhanvien,
                hanh_dong=action,
                doi_tuong='DichVu',
                object_id=dv.MaDichVu,
                mo_ta=dv.TenDichVu[:200]
            )
            messages.success(request, "Lưu dịch vụ thành công.")
            return redirect('staff_service_list')
    else:
        form = DichVuForm(instance=dv)

    return render(request, 'staffpanel/service_form.html', {'form': form, 'dv': dv})


@content_required
def staff_service_delete(request, pk):
    dv = get_object_or_404(DichVu, pk=pk)
    if request.method == 'POST':
        ma = dv.MaDichVu
        ten = dv.TenDichVu
        dv.delete()
        NhatKyHoatDong.objects.create(
            nhan_vien=request.user.nhanvien,
            hanh_dong="Xóa dịch vụ",
            doi_tuong='DichVu',
            object_id=ma,
            mo_ta=ten[:200]
        )
        messages.success(request, "Đã xóa dịch vụ.")
        return redirect('staff_service_list')
    return render(request, 'staffpanel/confirm_delete.html', {'object': dv, 'title': dv.TenDichVu})


# ========== LỊCH HẸN (RECEPTION + MANAGER) ==========

@reception_required
def staff_appointment_list(request):
    ngay = request.GET.get('ngay')
    trang_thai = request.GET.get('trang_thai', '')
    dich_vu = request.GET.get('dich_vu', '')

    lich_hen = LichHen.objects.select_related('DichVu').order_by('-MaLichHen')

    if ngay:
        lich_hen = lich_hen.filter(NgayHen=ngay)
    if trang_thai:
        lich_hen = lich_hen.filter(TrangThai=trang_thai)
    if dich_vu:
        lich_hen = lich_hen.filter(DichVu_id=dich_vu)

    context = {
        'lich_hen': lich_hen,
        'form': LichHenForm(),  # để lấy choices trạng thái
        'dich_vu_list': DichVu.objects.all(),  # để đổ dropdown dịch vụ
    }
    return render(request, 'staffpanel/appointment_list.html', context)


# ========== THÊM MỚI, XEM CHI TIẾT, XÓA LỊCH HẸN ==========

@reception_required
def staff_appointment_create(request):
    if request.method == 'POST':
        form = LichHenForm(request.POST)
        if form.is_valid():
            lh = form.save(commit=False)
            lh.save()

            NhatKyHoatDong.objects.create(
                nhan_vien=request.user.nhanvien,
                hanh_dong="Tạo lịch hẹn mới",
                doi_tuong='LichHen',
                object_id=lh.MaLichHen,
                mo_ta=f"{lh.HoTen} - {lh.NgayHen} {lh.KhungGio}"
            )
            messages.success(request, "Tạo lịch hẹn thành công!")
            return redirect('staff_appointment_list')
    else:
        form = LichHenForm()

    return render(request, 'staffpanel/appointment_form.html', {
        'form': form,
        'title': 'Tạo lịch hẹn mới',
        'danh_muc_list': DanhMucDichVu.objects.all(),   # ← THÊM DÒNG NÀY
    })


@reception_required
def staff_appointment_detail(request, ma_lich_hen):
    lh = get_object_or_404(LichHen, MaLichHen=ma_lich_hen)
    return render(request, 'staffpanel/appointment_detail.html', {'lh': lh})


@reception_required
def staff_appointment_edit(request, ma_lich_hen):
    lh = get_object_or_404(LichHen, MaLichHen=ma_lich_hen)
    if request.method == 'POST':
        form = LichHenForm(request.POST, instance=lh)
        if form.is_valid():
            lh = form.save()
            NhatKyHoatDong.objects.create(
                nhan_vien=request.user.nhanvien,
                hanh_dong="Cập nhật lịch hẹn",
                doi_tuong='LichHen',
                object_id=lh.MaLichHen,
                mo_ta=f"{lh.HoTen} - {lh.NgayHen} {lh.KhungGio}"
            )
            messages.success(request, "Cập nhật lịch hẹn thành công!")
            return redirect('staff_appointment_list')
    else:
        form = LichHenForm(instance=lh)

    return render(request, 'staffpanel/appointment_form.html', {
        'form': form,
        'lh': lh,
        'title': f'Cập nhật lịch hẹn #{lh.MaLichHen}',
        'danh_muc_list': DanhMucDichVu.objects.all(),   # ← THÊM DÒNG NÀY
    })


# ====================== XÓA HÀNG riêng lẻ ======================


@reception_required  # lễ tân vẫn được vào trang confirm delete để xem
def staff_appointment_delete(request, ma_lich_hen):
    lh = get_object_or_404(LichHen, MaLichHen=ma_lich_hen)

    # ---------- KIỂM TRA QUYỀN XÓA (chỉ MANAGER hoặc superuser) ----------
    if not (request.user.is_superuser or
            (hasattr(request.user, 'nhanvien') and request.user.nhanvien.VaiTro == 'MANAGER')):
        messages.error(request, "Bạn không có quyền xóa lịch hẹn.")
        return redirect('staff_appointment_list')
    # -------------------------------------------------------------------

    if request.method == 'POST':
        ma = lh.MaLichHen
        ten_khach = lh.HoTen or "Khách lẻ"
        lh.delete()

        NhatKyHoatDong.objects.create(
            nhan_vien=request.user.nhanvien,
            hanh_dong="Xóa lịch hẹn",
            doi_tuong='LichHen',
            object_id=ma,
            mo_ta=f"{ten_khach} - {lh.NgayHen} {lh.KhungGio}"
        )
        messages.success(request, "Đã xóa lịch hẹn thành công!")
        return redirect('staff_appointment_list')

    return render(request, 'staffpanel/appointment_confirm_delete.html', {'lh': lh})

# ====================== XÓA HÀNG LOẠT ======================
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
@require_POST
@login_required
@reception_required   # lễ tân vẫn tick chọn được trong danh sách
def staff_appointment_bulk_delete(request):
    # ---------- KIỂM TRA QUYỀN XÓA HÀNG LOẠT ----------
    if not (request.user.is_superuser or
            (hasattr(request.user, 'nhanvien') and request.user.nhanvien.VaiTro == 'MANAGER')):
        messages.error(request, "Bạn không có quyền xóa lịch hẹn.")
        return redirect('staff_appointment_list')
    # -------------------------------------------------

    ids = request.POST.getlist('ids')
    if not ids:
        messages.error(request, "Không có lịch hẹn nào được chọn.")
        return redirect('staff_appointment_list')

    deleted_count = 0
    for ma_lich_hen in ids:
        try:
            lh = LichHen.objects.get(MaLichHen=ma_lich_hen)
            NhatKyHoatDong.objects.create(
                nhan_vien=request.user.nhanvien,
                hanh_dong="Xóa lịch hẹn (hàng loạt)",
                doi_tuong='LichHen',
                object_id=lh.MaLichHen,
                mo_ta=f"{lh.HoTen or 'Khách lẻ'} - {lh.NgayHen} {lh.KhungGio}"
            )
            lh.delete()
            deleted_count += 1
        except LichHen.DoesNotExist:
            continue

    if deleted_count > 0:
        messages.success(request, f"Đã xóa thành công {deleted_count} lịch hẹn.")
    else:
        messages.warning(request, "Không thể xóa bất kỳ lịch hẹn nào.")

    return redirect('staff_appointment_list')


# ====================== AJAX CHO THÊM/SỬA LỊCH HẸN ======================

@require_GET
def ajax_get_services(request):
    ma_danh_muc = request.GET.get('ma_danh_muc')
    if not ma_danh_muc:
        return JsonResponse([], safe=False)

    services = DichVu.objects.filter(MaDanhMuc_id=ma_danh_muc).values('MaDichVu', 'TenDichVu')
    return JsonResponse(list(services), safe=False)


@require_GET
def ajax_available_times(request):
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'available_times': []})

    ALL_TIMES = [
        "09:00 - 10:30", "10:30 - 12:00", "13:30 - 15:00",
        "15:00 - 16:30", "16:30 - 18:00", "18:00 - 19:30", "19:30 - 21:00"
    ]

    booked_times = LichHen.objects.filter(NgayHen=date_str).values_list('KhungGio', flat=True)
    available = [t for t in ALL_TIMES if t not in booked_times]

    return JsonResponse({'available_times': available})
# ========== KHÁCH HÀNG + ĐIỂM TÍCH LŨY (RECEPTION + MANAGER) ==========

@reception_required
def staff_customer_list(request):
    q = request.GET.get('q', '').strip()
    customer_type = request.GET.get('customer_type', '')  # online / offline / (rỗng = tất cả)

    # Bắt đầu từ toàn bộ khách hàng
    customers = KhachHang.objects.select_related('diemtichluy', 'user').all()

    # 1. Tìm kiếm
    if q:
        customers = customers.filter(
            models.Q(HoTen__icontains=q) |
            models.Q(SDT__icontains=q) |
            models.Q(Email__icontains=q) |
            models.Q(MaKhachHang__icontains=q)
        )

    # 2. Lọc loại khách hàng
    if customer_type == 'online':
        customers = customers.exclude(user__isnull=True)   # có user → đăng ký web
    elif customer_type == 'offline':
        customers = customers.filter(user__isnull=True)     # không có user → tạo tại quầy

    # Gắn điểm hiện tại để hiển thị
    for kh in customers:
        kh.diem_hien_tai = getattr(kh.diemtichluy, 'SoDiemHienTai', 0) if hasattr(kh, 'diemtichluy') else 0

    return render(request, 'staffpanel/customer_list.html', {
        'customers': customers,
        'q': q,
        'customer_type': customer_type,   # để giữ giá trị đã chọn
    })

@reception_required
def staff_customer_edit(request, pk=None):
    # Nếu có pk → sửa, không có → thêm mới
    if pk:
        kh = get_object_or_404(KhachHang, MaKhachHang=pk)
        title = f"Sửa khách hàng {pk}"
    else:
        kh = None
        title = "Thêm khách hàng mới"

    if request.method == 'POST':
        form = KhachHangForm(request.POST, instance=kh)
        if form.is_valid():
            customer = form.save()
            messages.success(request, "Lưu thông tin khách hàng thành công!")
            return redirect('staff_customer_list')
    else:
        form = KhachHangForm(instance=kh)

    return render(request, 'staffpanel/customer_form.html', {
        'form': form,
        'kh': kh,
        'title': title,
    })





# ========== NHÂN VIÊN + NHẬT KÝ (MANAGER) ==========

@manager_required
def staff_employee_list(request):
    employees = NhanVien.objects.select_related('user').all().order_by('MaNhanVien')

    # Tìm kiếm
    q = request.GET.get('q', '').strip()
    if q:
        employees = employees.filter(
            Q(MaNhanVien__icontains=q) |
            Q(user__username__icontains=q) |
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(user__email__icontains=q)
        )

    # Lọc theo vai trò
    vai_tro = request.GET.get('vai_tro')
    if vai_tro:
        employees = employees.filter(VaiTro=vai_tro)

    # Lọc theo trạng thái online
    online = request.GET.get('online')
    if online == '1':
        employees = employees.filter(is_online=True)
    elif online == '0':
        employees = employees.filter(is_online=False)

    return render(request, 'staffpanel/employee_list.html', {
        'employees': employees,
        'q': q,
        'current_vai_tro': vai_tro,
        'current_online': online,
    })

@manager_required
def staff_employee_edit(request, pk):
    nhanvien = get_object_or_404(NhanVien, MaNhanVien=pk)
    user = nhanvien.user

    if request.method == 'POST':
        # Cập nhật User
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip()
        user.save()

        # Cập nhật NhanVien
        nhanvien.VaiTro = request.POST.get('vai_tro')
        nhanvien.save()

        # Đổi mật khẩu nếu có nhập
        new_password = request.POST.get('new_password', '').strip()
        if new_password:
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Đã đổi mật khẩu thành công!')

        messages.success(request, f'Cập nhật nhân viên {nhanvien} thành công!')
        return redirect('staff_employee_list')

    return render(request, 'staffpanel/employee_form.html', {
        'nhanvien': nhanvien,
    })


@manager_required
def staff_employee_delete(request, pk):
    nhanvien = get_object_or_404(NhanVien, MaNhanVien=pk)

    if request.method == 'POST':
        username = nhanvien.user.username if nhanvien.user else 'Không xác định'
        nhanvien.user.delete()  # xóa luôn User liên kết
        messages.success(request, f'Đã xóa nhân viên {username}')
        return redirect('staff_employee_list')

    return render(request, 'staffpanel/confirm_delete.html', {
        'object': nhanvien,
        'title': f'Xóa nhân viên {nhanvien.user.get_full_name() or nhanvien.user.username if nhanvien.user else nhanvien.MaNhanVien}?'
    })

@manager_required
@require_POST
def staff_employee_bulk_delete(request):
    ids = request.POST.getlist('ids[]')
    if not ids:
        messages.error(request, 'Không có nhân viên nào được chọn!')
    else:
        # Xóa cả User liên kết
        nhanvien_list = NhanVien.objects.filter(MaNhanVien__in=ids)
        for nv in nhanvien_list:
            if nv.user:
                nv.user.delete()
            nv.delete()
        messages.success(request, f'Đã xóa thành công {len(ids)} nhân viên!')
    return redirect('staff_employee_list')

@manager_required
def staff_log_list(request):
    logs = NhatKyHoatDong.objects.select_related('nhan_vien')[:100]
    return render(request, 'staffpanel/log_list.html', {'logs': logs})

# ============== LOYALTY (RECEPTION + MANAGER) ==============
from django.views.decorators.csrf import ensure_csrf_cookie

@reception_required
def staff_loyalty_list(request):
    q = request.GET.get('q', '')
    items = DiemTichLuy.objects.select_related('MaKhachHang').all().order_by('-SoDiemHienTai')

    if q:
        items = items.filter(
            models.Q(MaKhachHang__MaKhachHang__icontains=q) |
            models.Q(MaKhachHang__HoTen__icontains=q)
        )
    return render(request, 'staffpanel/loyalty_list.html', {'items': items, 'q': q})


@reception_required
def staff_loyalty_history_ajax(request, makh):
    history = LichSuTichDiem.objects.filter(MaKhachHang__MaKhachHang=makh) \
        .order_by('-NgayGiaoDich') \
        .select_related('NguoiThucHien__user')

    items = []
    is_manager = request.user.nhanvien.VaiTro == 'MANAGER'

    for h in history:
        item = {
            "magd": h.MaGiaoDich,
            "ngay": h.NgayGiaoDich.strftime("%d/%m/%Y %H:%M"),
            "loaigd": h.LoaiGiaoDich,
            "diem": h.SoDiemThayDoi,
            "chitiet": h.ChiTietGiaoDich or "—",
        }
        # Chỉ manager mới thấy người thực hiện
        if is_manager and h.NguoiThucHien:
            nguoi = h.NguoiThucHien
            ten = nguoi.user.get_full_name().strip() or nguoi.user.username
            item["nguoi_thuc_hien"] = f"{nguoi.MaNhanVien} - {ten}"
        items.append(item)

    return JsonResponse({
        "success": True,
        "items": items,
        "is_manager": is_manager,
    })


@reception_required
def staff_loyalty_update_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})

    # Lấy danh sách mã khách hàng
    makh_list = request.POST.getlist('makh[]') or [request.POST.get('makh')]
    if not makh_list or not makh_list[0]:
        return JsonResponse({'success': False, 'error': 'Chưa chọn khách hàng'})

    try:
        diem_thay_doi = int(request.POST.get('diem', 0))
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Số điểm không hợp lệ'})

    lydo = request.POST.get('lydo', '').strip() or 'Cập nhật thủ công'
    loaigd = request.POST.get('loaigd', '').strip()

    # Tự động xác định loại giao dịch nếu chưa có
    if not loaigd:
        loaigd = 'Tích điểm' if diem_thay_doi > 0 else 'Quy đổi điểm'

    # === KIỂM TRA ĐIỂM TRƯỚC KHI LÀM GÌ CẢ ===
    if diem_thay_doi == 0:
        return JsonResponse({'success': False, 'error': 'Số điểm phải khác 0'})
    if diem_thay_doi > 0 and loaigd != 'Tích điểm':
        return JsonResponse({'success': False, 'error': 'Loại giao dịch không khớp (cộng điểm)'})
    if diem_thay_doi < 0 and loaigd != 'Quy đổi điểm':
        return JsonResponse({'success': False, 'error': 'Loại giao dịch không khớp (trừ điểm)'})

    # Đếm thành công và lỗi
    success_count = 0
    errors = []

    for makh in makh_list:
        makh = makh.strip()
        try:
            kh = KhachHang.objects.get(MaKhachHang=makh)
            wallet = DiemTichLuy.objects.select_for_update().get(MaKhachHang=kh)

            # === CHỖ QUAN TRỌNG NHẤT: KIỂM TRA KHÔNG ĐƯỢC TRỪ QUÁ ĐIỂM HIỆN TẠI ===
            if diem_thay_doi < 0:
                diem_can_tru = -diem_thay_doi  # ví dụ: -10 → cần trừ 10
                if diem_can_tru > wallet.SoDiemHienTai:
                    errors.append(f"{makh}: Không đủ điểm (còn {wallet.SoDiemHienTai}, cần {diem_can_tru})")
                    continue

            # Tạo lịch sử giao dịch
            LichSuTichDiem.objects.create(
                MaKhachHang=kh,
                SoDiemThayDoi=diem_thay_doi,
                ChiTietGiaoDich=lydo,
                LoaiGiaoDich=loaigd,
                NguoiThucHien=request.user.nhanvien
            )
            success_count += 1

        except KhachHang.DoesNotExist:
            errors.append(f"{makh}: Không tìm thấy khách hàng")
        except DiemTichLuy.DoesNotExist:
            # Nếu chưa có ví → chỉ cho cộng, không cho trừ
            if diem_thay_doi < 0:
                errors.append(f"{makh}: Chưa có điểm để trừ")
            else:
                # Tạo ví mới và cộng điểm
                DiemTichLuy.objects.create(MaKhachHang=kh, SoDiemHienTai=diem_thay_doi)
                LichSuTichDiem.objects.create(
                    MaKhachHang=kh,
                    SoDiemThayDoi=diem_thay_doi,
                    ChiTietGiaoDich=lydo,
                    LoaiGiaoDich=loaigd,
                    NguoiThucHien=request.user.nhanvien
                )
                success_count += 1
        except Exception as e:
            errors.append(f"{makh}: Lỗi - {str(e)}")

    # Trả kết quả
    if success_count == len(makh_list):
        return JsonResponse({
            'success': True,
            'message': f'Thành công {success_count} khách hàng'
        })
    elif success_count > 0:
        return JsonResponse({
            'success': False,
            'message': f'Thành công {success_count}/{len(makh_list)}',
            'error': '\n'.join(errors)
        })
    else:
        return JsonResponse({
            'success': False,
            'error': '\n'.join(errors) or 'Có lỗi xảy ra'
        })


@staff_required  # chuyên viên
def appointment_staff(request):
    nv = request.user.nhanvien  # lấy nhân viên đang đăng nhập

    lichhen = LichHen.objects.filter(NhanVienThucHien=nv)

    return render(request, "staffpanel/appointment_staff.html", {
        "lichhen": lichhen
    })


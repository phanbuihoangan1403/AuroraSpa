from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from aurora.models import (
    NhanVien, FAQ, Blog, DichVu, LichHen,
    KhachHang, DiemTichLuy
)
from .models import NhatKyHoatDong
from .forms import (
    StaffLoginForm, StaffRegisterForm,UserProfileForm,StaffProfileForm,
    FAQForm, BlogForm, DichVuForm, LichHenForm,
    KhachHangForm, DiemTichLuyForm
)
from .permissions import manager_required, content_required, reception_required


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
    trang_thai = request.GET.get('trang_thai', '')
    lich_hen = LichHen.objects.select_related('DanhMucDichVu', 'DichVu').order_by('-NgayHen')

    if trang_thai:
        lich_hen = lich_hen.filter(TrangThai=trang_thai)

    return render(request, 'staffpanel/appointment_list.html', {
        'lich_hen': lich_hen,
        'trang_thai': trang_thai,
    })


@reception_required
def staff_appointment_edit(request, pk):
    lh = get_object_or_404(LichHen, pk=pk)
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
            messages.success(request, "Cập nhật lịch hẹn thành công.")
            return redirect('staff_appointment_list')
    else:
        form = LichHenForm(instance=lh)

    return render(request, 'staffpanel/appointment_form.html', {'form': form, 'lh': lh})


# ========== KHÁCH HÀNG + ĐIỂM TÍCH LŨY (RECEPTION + MANAGER) ==========

@reception_required
def staff_customer_list(request):
    q = request.GET.get('q', '')
    customers = KhachHang.objects.all()
    if q:
        customers = customers.filter(HoTen__icontains=q)
    return render(request, 'staffpanel/customer_list.html', {'customers': customers, 'q': q})


@reception_required
def staff_customer_edit(request, pk):
    kh = get_object_or_404(KhachHang, pk=pk)
    if request.method == 'POST':
        form = KhachHangForm(request.POST, instance=kh)
        if form.is_valid():
            form.save()
            NhatKyHoatDong.objects.create(
                nhan_vien=request.user.nhanvien,
                hanh_dong="Cập nhật khách hàng",
                doi_tuong='KhachHang',
                object_id=kh.MaKhachHang,
                mo_ta=kh.HoTen[:200]
            )
            messages.success(request, "Cập nhật thông tin khách hàng thành công.")
            return redirect('staff_customer_list')
    else:
        form = KhachHangForm(instance=kh)
    return render(request, 'staffpanel/customer_form.html', {'form': form, 'kh': kh})


@reception_required
def staff_loyalty_list(request):
    ds = DiemTichLuy.objects.select_related('MaKhachHang').all()
    return render(request, 'staffpanel/loyalty_list.html', {'items': ds})


@reception_required
def staff_loyalty_edit(request, pk):
    diem = get_object_or_404(DiemTichLuy, pk=pk)
    if request.method == 'POST':
        form = DiemTichLuyForm(request.POST, instance=diem)
        if form.is_valid():
            form.save()
            NhatKyHoatDong.objects.create(
                nhan_vien=request.user.nhanvien,
                hanh_dong="Điều chỉnh điểm tích lũy",
                doi_tuong='DiemTichLuy',
                object_id=str(diem.pk),
                mo_ta=f"{diem.MaKhachHang.MaKhachHang} - {diem.SoDiemHienTai} điểm"
            )
            messages.success(request, "Cập nhật điểm tích lũy thành công.")
            return redirect('staff_loyalty_list')
    else:
        form = DiemTichLuyForm(instance=diem)
    return render(request, 'staffpanel/loyalty_form.html', {'form': form, 'diem': diem})


# ========== NHÂN VIÊN + NHẬT KÝ (MANAGER) ==========

@manager_required
def staff_employee_list(request):
    ds = NhanVien.objects.select_related('user').all()
    return render(request, 'staffpanel/employee_list.html', {'employees': ds})


@manager_required
def staff_log_list(request):
    logs = NhatKyHoatDong.objects.select_related('nhan_vien')[:100]
    return render(request, 'staffpanel/log_list.html', {'logs': logs})

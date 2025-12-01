from django import forms
from django.contrib.auth.models import User
from aurora.models import (
    NhanVien, FAQ, Blog, DichVu, DanhMucDichVu,
    LichHen, KhachHang, DiemTichLuy
)
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils import timezone  # Thêm import này để check ngày

# 7 KHUNG GIỜ CỐ ĐỊNH
KHUNG_GIO_CHOICES = [
    ("09:00 - 10:30", "09:00 - 10:30"),
    ("10:30 - 12:00", "10:30 - 12:00"),
    ("13:30 - 15:00", "13:30 - 15:00"),
    ("15:00 - 16:30", "15:00 - 16:30"),
    ("16:30 - 18:00", "16:30 - 18:00"),
    ("18:00 - 19:30", "18:00 - 19:30"),
    ("19:30 - 21:00", "19:30 - 21:00"),
]


# ========================================
# LOGIN FORM NHÂN VIÊN
# ========================================
class StaffLoginForm(AuthenticationForm):
    username = forms.CharField(label="Tên đăng nhập")
    password = forms.CharField(label="Mật khẩu", widget=forms.PasswordInput)


# ========================================
# REGISTER FORM NHÂN VIÊN (CHO QUẢN LÝ)
# ========================================
class StaffRegisterForm(forms.ModelForm):
    # Fields của User
    username = forms.CharField(label="Tên đăng nhập", max_length=150, required=True)
    email = forms.EmailField(label="Email", required=True)
    first_name = forms.CharField(label="Họ", max_length=150, required=True)
    last_name = forms.CharField(label="Tên", max_length=150, required=True)
    password1 = forms.CharField(label="Mật khẩu", widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label="Nhập lại mật khẩu", widget=forms.PasswordInput, required=True)

    class Meta:
        model = NhanVien
        fields = ['VaiTro', 'NhomChuyenVien']
        widgets = {
            'VaiTro': forms.Select(),
            'NhomChuyenVien': forms.Select(),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            raise forms.ValidationError("Mật khẩu không trùng khớp")
        return cleaned_data
# ========================================
# HỒ SƠ NHÂN VIÊN
# ========================================
class StaffProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Họ'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }


# ========================================
# FAQ FORM
# ========================================
class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['CauHoi', 'CauTraLoi', 'TrangThaiHienThi']
        widgets = {
            'CauHoi': forms.TextInput(attrs={'class': 'form-control'}),
            'CauTraLoi': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'TrangThaiHienThi': forms.CheckboxInput(),
        }


# ========================================
# BLOG FORM
# ========================================
class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = [
            'TieuDeBaiViet',
            'NoiDungBaiViet',
            'HinhAnh',
            'TrangThaiHienThi'
        ]
        widgets = {
            'TieuDeBaiViet': forms.TextInput(attrs={'class': 'form-control'}),
            'NoiDungBaiViet': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
            'HinhAnh': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'TrangThaiHienThi': forms.CheckboxInput(),
        }


# ========================================
# DỊCH VỤ FORM
# ========================================
class DichVuForm(forms.ModelForm):
    class Meta:
        model = DichVu
        fields = [
            'MaDanhMuc',
            'TenDichVu',
            'MoTa',
            'GiaTien',
            'TrangThaiHienThi',
            'HinhAnh',
        ]
        widgets = {
            'MaDanhMuc': forms.Select(attrs={'class': 'form-control'}),
            'TenDichVu': forms.TextInput(attrs={'class': 'form-control'}),
            'MoTa': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'GiaTien': forms.NumberInput(attrs={'class': 'form-control'}),
            'TrangThaiHienThi': forms.CheckboxInput(),
            'HinhAnh': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


# ========================================
# LỊCH HẸN FORM
# ========================================
class LichHenForm(forms.ModelForm):
    KhungGio = forms.ChoiceField(
        choices=KHUNG_GIO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    nhan_vien_display = forms.CharField(  # Thêm field display read-only
        label='Nhân viên thực hiện',
        disabled=True,
        required=False,
        widget = forms.TextInput(attrs={
            'class': 'form-control',  # ← THÊM DÒNG NÀY
            'readonly': 'readonly',
            'style': 'background-color: #f8f9fa; font-weight: 500; border-color: #ced4da;'
        }))
    class Meta:
        model = LichHen
        fields = [
            'HoTen', 'Email', 'DienThoai', 'DanhMucDichVu', 'DichVu',
            'NgayHen', 'KhungGio', 'MaGiamGia', 'TrangThai',
            'NhanVienThucHien',  # Giữ để bind/save, nhưng ẩn
            'nhan_vien_display'  # Thêm field display
        ]
        widgets = {
            'HoTen': forms.TextInput(attrs={'class': 'form-control'}),
            'Email': forms.EmailInput(attrs={'class': 'form-control'}),
            'DienThoai': forms.TextInput(attrs={'class': 'form-control'}),
            'DanhMucDichVu': forms.Select(attrs={'class': 'form-control'}),
            'DichVu': forms.Select(attrs={'class': 'form-control'}),
            'NgayHen': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'MaGiamGia': forms.TextInput(attrs={'class': 'form-control'}),
            'TrangThai': forms.Select(attrs={'class': 'form-control'}),
            'NhanVienThucHien': forms.HiddenInput(),  # Ẩn hoàn toàn cho tất cả vai trò
        }

    def __init__(self, *args, **kwargs):
        # Nhận request từ view để biết ai đang đăng nhập (giữ nguyên)
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Set initial cho field display
        if self.instance.pk and self.instance.NhanVienThucHien:
            nv = self.instance.NhanVienThucHien
            display_text = f"{nv.MaNhanVien} - {nv.user.username if nv.user else 'Không xác định'}"
            self.fields['nhan_vien_display'].initial = display_text
        else:
            self.fields['nhan_vien_display'].initial = 'Tự động phân nhân viên'

    def clean_NgayHen(self):  # Thêm ràng buộc ngày không được qua
        ngay_hen = self.cleaned_data.get('NgayHen')
        if ngay_hen and ngay_hen < timezone.now().date():
            raise ValidationError("Không thể chọn ngày đã qua.")
        return ngay_hen


# ========================================
# KHÁCH HÀNG FORM
# ========================================
class KhachHangForm(forms.ModelForm):
    class Meta:
        model = KhachHang
        fields = ['HoTen', 'SDT', 'Email', 'DiaChi', 'NgaySinh']
        widgets = {
            'HoTen': forms.TextInput(attrs={'class': 'form-control'}),
            'SDT': forms.TextInput(attrs={'class': 'form-control'}),
            'Email': forms.EmailInput(attrs={'class': 'form-control'}),
            'DiaChi': forms.TextInput(attrs={'class': 'form-control'}),
            'NgaySinh': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Nếu đang SỬA → thêm field MaKhachHang chỉ để hiển thị (readonly)
        if self.instance and self.instance.pk:
            self.fields['MaKhachHang'] = forms.CharField(
                initial=self.instance.MaKhachHang,
                disabled=True,
                widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
            )


# ========================================
# ĐIỂM TÍCH LŨY FORM
# ========================================
class DiemTichLuyForm(forms.ModelForm):
    class Meta:
        model = DiemTichLuy
        fields = ['SoDiemHienTai']
        widgets = {
            'SoDiemHienTai': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
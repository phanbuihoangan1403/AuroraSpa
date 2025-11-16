from django import forms
from django.contrib.auth.models import User
from aurora.models import (
    NhanVien, FAQ, Blog, DichVu, DanhMucDichVu,
    LichHen, KhachHang, DiemTichLuy
)
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


# ========================================
# LOGIN FORM NHÂN VIÊN
# ========================================
class StaffLoginForm(AuthenticationForm):
    username = forms.CharField(label="Tên đăng nhập")
    password = forms.CharField(label="Mật khẩu", widget=forms.PasswordInput)


# ========================================
# REGISTER FORM NHÂN VIÊN (CHO QUẢN LÝ)
# ========================================
class StaffRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    vai_tro = forms.ChoiceField(choices=NhanVien.ROLE_CHOICES, label="Vai trò")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

            NhanVien.objects.create(
                user=user,
                VaiTro=self.cleaned_data['vai_tro']
            )

        return user


# ========================================
# HỒ SƠ NHÂN VIÊN
# ========================================
class StaffProfileForm(forms.ModelForm):
    class Meta:
        model = NhanVien
        fields = ['MaNhanVien', 'VaiTro']
        widgets = {
            'MaNhanVien': forms.TextInput(attrs={'readonly': True}),
            'VaiTro': forms.Select(attrs={'disabled': True}),
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
    class Meta:
        model = LichHen
        fields = [
            'HoTen',
            'Email',
            'DienThoai',
            'DanhMucDichVu',
            'DichVu',
            'NgayHen',
            'KhungGio',
            'MaGiamGia',
            'TrangThai'
        ]
        widgets = {
            'HoTen': forms.TextInput(attrs={'class': 'form-control'}),
            'Email': forms.EmailInput(attrs={'class': 'form-control'}),
            'DienThoai': forms.TextInput(attrs={'class': 'form-control'}),
            'DanhMucDichVu': forms.Select(attrs={'class': 'form-control'}),
            'DichVu': forms.Select(attrs={'class': 'form-control'}),
            'NgayHen': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'KhungGio': forms.TextInput(attrs={'class': 'form-control'}),
            'MaGiamGia': forms.TextInput(attrs={'class': 'form-control'}),
            'TrangThai': forms.Select(attrs={'class': 'form-control'}),
        }


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
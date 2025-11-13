from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from aurora.models import KhachHang
from .models import LichHen, DanhMucDichVu, DichVu #ĐẶT LỊCH

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    sdt = forms.CharField(max_length=10, required=False, label="Số điện thoại")

    class Meta:
        model = User
        fields = ['username','email', 'sdt','password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')

        if commit:
            user.save()

            # tạo khách hàng
            KhachHang.objects.create(
                user=user,
                HoTen=self.cleaned_data.get('HoTen'),
                SDT=self.cleaned_data.get('sdt'),
                Email=user.email,
                NgaySinh=self.cleaned_data.get('NgaySinh'),
                DiaChi=self.cleaned_data.get('DiaChi')
            )
        return user

#FORM: ĐẶT LỊCH
class DatLichForm(forms.ModelForm):
    class Meta:
        model = LichHen
        fields = ['HoTen', 'Email', 'DienThoai', 'DanhMucDichVu', 'DichVu', 'NgayHen', 'KhungGio', 'MaGiamGia']
        widgets = {
            'NgayHen': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'HoTen': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Họ và tên'}),
            'Email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'DienThoai': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SĐT'}),
            'MaGiamGia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mã giảm giá (nếu có)'}),
            'DanhMucDichVu': forms.Select(attrs={'class': 'form-control'}),
            'DichVu': forms.Select(attrs={'class': 'form-control'}),
            'KhungGio': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['DichVu'].queryset = DichVu.objects.none()
        if 'DanhMucDichVu' in self.data:
            try:
                dm_id = self.data.get('DanhMucDichVu')
                self.fields['DichVu'].queryset = DichVu.objects.filter(MaDanhMuc_id=dm_id)
            except:
                pass
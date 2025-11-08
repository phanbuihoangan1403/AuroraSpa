from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from aurora.models import KhachHang

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    sdt = forms.CharField(max_length=10, required=False, label="Số điện thoại")

    class Meta:
        model = User
        fields = ['username', 'email', 'sdt', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')

        if commit:
            user.save()

            # tạo khách hàng
            KhachHang.objects.create(
                user=user,
                SDT=self.cleaned_data.get('sdt'),
                Email=user.email
            )
        return user

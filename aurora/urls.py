from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    home_view, blog_view, dichvu_view, lichhen_view,
    faq_view, lienhe_view, profile_view, diem_view,
    login_view, logout_view, register_view
)

urlpatterns = [
    path('', home_view, name='home'),
    path('blog/', blog_view, name='blog'),
    path('dich-vu/', dichvu_view, name='dichvu'),
    path('lich-hen/', lichhen_view, name='lichhen'),
    path('faq/', faq_view, name='faq'),
    path('lien-he/', lienhe_view, name='lienhe'),
    path('ho-so/', profile_view, name='profile'),
    path('diem-tich-luy/', diem_view, name='diem'),

    # auth
    path('dang-ky/', register_view, name='register'),
    path('dang-nhap/', login_view, name='login'),
    path('dang-xuat/', logout_view, name='logout'),

    #matkhau
    path('quen-mat-khau/', auth_views.PasswordResetView.as_view(
        template_name='auth/password_reset.html'
    ), name='password_reset'),

    path('quen-mat-khau/thanh-cong/', auth_views.PasswordResetDoneView.as_view(
        template_name='auth/password_reset_done.html'
    ), name='password_reset_done'),

    path('dat-lai-mat-khau/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='auth/password_reset_confirm.html'
    ), name='password_reset_confirm'),

    path('dat-lai-mat-khau/xong/', auth_views.PasswordResetCompleteView.as_view(
        template_name='auth/password_reset_complete.html'
    ), name='password_reset_complete'),
]

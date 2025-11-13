from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    home_view, blog_view, chitietblog_view, chitietdichvu_view, dichvu_view, datlichhen_view,
    lichsulichhen_view, faq_view, lienhe_view, profile_view, diem_view,
    login_view, logout_view, register_view,LayDichVuView
)
from . import views

urlpatterns = [
    path('', home_view, name='home'),
    path('blog/', blog_view, name='blog'),
    path('blog/<str:pk>/', chitietblog_view, name='chitietblog'),
    path('dichvu/', dichvu_view, name='dichvu'),
    path('dichvu/<str:madanhmuc>/<str:madichvu>/', chitietdichvu_view, name='chitietdichvu'),
    path('dat-lich-hen/', datlichhen_view, name='dat-lich-hen'),
    path('lich-su-lich-hen/', lichsulichhen_view, name='lich-su-lich-hen'),
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
# THÊM DÒNG NÀY: AJAX LẤY DỊCH VỤ
    path('ajax/lay-dich-vu/', LayDichVuView.as_view(), name='lay_dich_vu'),
    path('ajax/available-times/', views.available_time_slots, name='available_times'),
    path('ajax/save-appointment/',views.save_appointment, name='save_appointment'),
    path('ajax/get-service-by-category/', views.get_service_by_category, name='get_service_by_category'),

# API
    path('api/lich-hen/<str:ma_lichhen>/', views.api_chi_tiet_lich_hen, name='api_lichhen_detail')
]

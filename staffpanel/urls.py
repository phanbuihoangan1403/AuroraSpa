from django.urls import path
from . import views

urlpatterns = [
    # auth
    path('login/', views.staff_login, name='staff_login'),
    path('logout/', views.staff_logout, name='staff_logout'),
    path('register/', views.staff_register, name='staff_register'),
    path('profile/', views.staff_profile, name='staff_profile'),

    # dashboard
    path('', views.staff_dashboard, name='staff_dashboard'),

    # FAQ
    path('faq/', views.staff_faq_list, name='staff_faq_list'),
    path('faq/add/', views.staff_faq_edit, name='staff_faq_add'),
    path('faq/<str:pk>/edit/', views.staff_faq_edit, name='staff_faq_edit'),
    path('faq/<str:pk>/delete/', views.staff_faq_delete, name='staff_faq_delete'),

    # Blog
    path('blog/', views.staff_blog_list, name='staff_blog_list'),
    path('blog/add/', views.staff_blog_edit, name='staff_blog_add'),
    path('blog/<str:pk>/edit/', views.staff_blog_edit, name='staff_blog_edit'),
    path('blog/<str:pk>/delete/', views.staff_blog_delete, name='staff_blog_delete'),

    # Dịch vụ
    path('services/', views.staff_service_list, name='staff_service_list'),
    path('services/add/', views.staff_service_edit, name='staff_service_add'),
    path('services/<str:pk>/edit/', views.staff_service_edit, name='staff_service_edit'),
    path('services/<str:pk>/delete/', views.staff_service_delete, name='staff_service_delete'),

    # Lịch hẹn
    path('appointments/', views.staff_appointment_list, name='staff_appointment_list'),
    path('appointments/<str:pk>/edit/', views.staff_appointment_edit, name='staff_appointment_edit'),

    # Khách hàng
    path('customers/', views.staff_customer_list, name='staff_customer_list'),
    path('customers/<str:pk>/edit/', views.staff_customer_edit, name='staff_customer_edit'),

    # Điểm tích lũy
    path('loyalty/', views.staff_loyalty_list, name='staff_loyalty_list'),
    path('loyalty/<str:pk>/edit/', views.staff_loyalty_edit, name='staff_loyalty_edit'),

    # Nhân viên + nhật ký
    path('employees/', views.staff_employee_list, name='staff_employee_list'),
    path('logs/', views.staff_log_list, name='staff_log_list'),
]

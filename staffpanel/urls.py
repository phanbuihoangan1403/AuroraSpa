from django.urls import path
from . import views

urlpatterns = [
    # auth
    path('login/', views.staff_login, name='staff_login'),
    path('logout/', views.staff_logout, name='staff_logout'),
    path('register/', views.staff_register, name='staff_register'),
    path('profile/', views.staff_profile, name='staff_profile'),

    # dashboard
    path('', views.staff_profile, name='staff_dashboard'),

    # FAQ
    path('faq/', views.staff_faq_list, name='staff_faq_list'),
    path('faq/<str:pk>/edit/', views.staff_faq_edit, name='staff_faq_edit'),
    path('faq/add/', views.staff_faq_edit, name='staff_faq_add'),
    path('faq/<str:pk>/delete/', views.staff_faq_delete, name='staff_faq_delete'),
    # Danh mục FAQ
    path('faq/categories/', views.staff_faq_category_list, name='staff_faq_category_list'),
    path('faq/categories/add/', views.staff_faq_category_add, name='staff_faq_category_add'),
    path('faq/categories/<str:pk>/edit/', views.staff_faq_category_edit, name='staff_faq_category_edit'),
    path('faq/categories/<str:pk>/delete/', views.staff_faq_category_delete, name='staff_faq_category_delete'),
    path('faq/categories/bulk-delete/', views.staff_faq_category_bulk_delete, name='staff_faq_category_bulk_delete'),

    # FAQ theo danh mục (thay staff_faq:faq_list_by_category bằng tên thực nếu khác)
    path('faq/categories/<str:category_pk>/faqs/', views.staff_faq_list_by_category, name='staff_faq_list_by_category'),

    # Thêm FAQ mới (có thể truyền category_pk để mặc định danh mục)
    path('faq/categories/<str:category_pk>/faqs/add/', views.staff_faq_add_in_category,
         name='staff_faq_add_in_category'),
    path('faq/bulk-delete/', views.staff_faq_bulk_delete, name='staff_faq_bulk_delete'),

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
    path('appointments/add/', views.staff_appointment_create, name='staff_appointment_create'),
    path('appointments/bulk-delete/', views.staff_appointment_bulk_delete, name='staff_appointment_bulk_delete'),
    path('appointments/<str:ma_lich_hen>/', views.staff_appointment_detail, name='staff_appointment_detail'),
    path('appointments/<str:ma_lich_hen>/edit/', views.staff_appointment_edit, name='staff_appointment_edit'),
    path('appointments/<str:ma_lich_hen>/delete/', views.staff_appointment_delete, name='staff_appointment_delete'),
    # ====================== AJAX CHO THÊM/SỬA LỊCH HẸN ======================
    path('ajax/get-services/', views.ajax_get_services, name='ajax_get_services'),
    path('ajax/available-times/', views.ajax_available_times, name='available_times'),
    # Khách hàng
    path('customer/', views.staff_customer_list, name='staff_customer_list'),
    path('customer/add/', views.staff_customer_edit, name='staff_customer_add'),
    path('customer/edit/<str:pk>/', views.staff_customer_edit, name='staff_customer_edit'),
# Điểm tích lũy
    path('loyalty/', views.staff_loyalty_list, name='staff_loyalty_list'),

    # Lấy lịch sử + trả về is_manager để ẩn/hiện nút Xóa/Edit
    path('loyalty/history/<str:makh>/', views.staff_loyalty_history_ajax, name='staff_loyalty_history_ajax'),

    # Cộng/trừ điểm nhanh (dùng cho nút +10/-10 hoặc trong popup)
    path('loyalty/update/', views.staff_loyalty_update_ajax, name='staff_loyalty_update_ajax'),

    # Bulk update (checkbox nhiều khách)
    path('loyalty/bulk-update/', views.staff_loyalty_update_ajax, name='staff_loyalty_bulk_update_ajax'),
    # → Dùng chung 1 view với update bình thường, vì nó nhận list makh[] tự động


    # Nhân viên + nhật ký
    path('employees/', views.staff_employee_list, name='staff_employee_list'),
    path('employees/add/', views.staff_employee_create, name='staff_employee_add'),  # dùng chung register
    path('employees/<str:pk>/edit/', views.staff_employee_edit, name='staff_employee_edit'),
    path('employees/<str:pk>/delete/', views.staff_employee_delete, name='staff_employee_delete'),
    path('employees/bulk-delete/', views.staff_employee_bulk_delete, name='staff_employee_bulk_delete'),
#   path('logs/', views.staff_log_list, name='staff_log_list'),


path('customers/bulk-delete/', views.staff_customer_bulk_delete, name='staff_customer_bulk_delete'),

]
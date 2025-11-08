from django.contrib import admin
from django.contrib import admin
from .models import KhachHang, NhanVien, DichVu, DanhMucDichVu, LichHen, DiemTichLuy, LichSuTichDiem, QuyDoiDiem, Blog, FAQ

@admin.register(KhachHang)
class KhachHangAdmin(admin.ModelAdmin):
    readonly_fields = ('MaKhachHang',)  # Ẩn trong form (chỉ đọc)
    list_display = ('MaKhachHang', 'user', 'SDT')

@admin.register(NhanVien)
class NhanVienAdmin(admin.ModelAdmin):
    readonly_fields = ('MaNhanVien',)
    list_display = ('MaNhanVien', 'user', 'ChucVu')

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    readonly_fields = ('MaBaiViet',)  # Ẩn trong form (chỉ đọc)
    list_display = ('MaBaiViet', 'TieuDeBaiViet', 'NgayDang', 'TrangThaiHienThi')

@admin.register(DichVu)
class DichVuAdmin(admin.ModelAdmin):
    readonly_fields = ('MaDichVu',)  # Ẩn trong form (chỉ đọc)
    list_display = ('MaDichVu', 'TenDichVu', 'TrangThaiHienThi')
@admin.register(DanhMucDichVu)
class DanhMucDichVuAdmin(admin.ModelAdmin):
    readonly_fields = ('MaDanhMuc',)  # Ẩn trong form (chỉ đọc)
    list_display = ('MaDanhMuc', 'TenDanhMuc')

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    readonly_fields = ('MaCauHoi',)  # Ẩn trong form (chỉ đọc)
    list_display = ('MaCauHoi', 'CauHoi','NgayCapNhat','TrangThaiHienThi')
# (đăng ký các model còn lại nếu cần)
admin.site.register(LichHen)
admin.site.register(DiemTichLuy)
admin.site.register(LichSuTichDiem)
admin.site.register(QuyDoiDiem)


# Register your models here.

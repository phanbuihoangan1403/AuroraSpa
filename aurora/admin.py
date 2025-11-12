from django.contrib import admin
from django.contrib import admin
from .models import KhachHang, NhanVien, DichVu, DanhMucDichVu, LichHen, DiemTichLuy, LichSuTichDiem, QuyDoiDiem, Blog, FAQ
from django.utils.html import format_html
#TEMPLATE DÙNG CHUNG

def action_icons(obj):
    return format_html(
        '<a class="icon-edit" href="{}">✏️</a>'
        '<a class="icon-trash" href="{}">🗑️</a>',
        f"{obj.pk}/change/",
        f"{obj.pk}/delete/",
    )
action_icons.short_description = "Hành động"

@admin.register(KhachHang)
class KhachHangAdmin(admin.ModelAdmin):
    readonly_fields = ('MaKhachHang',)  # Ẩn trong form (chỉ đọc)
    list_display = ("MaKhachHang", "HoTen", "SDT", "Email", "DiaChi", "NgaySinh", action_icons)
    list_display_links = ("MaKhachHang", "HoTen")
    search_fields = ("MaKhachHang","user__username","HoTen", "SDT", "Email")
    list_filter = ("NgaySinh",)
    ordering = ("MaKhachHang",)
    list_per_page = 15

@admin.register(NhanVien)
class NhanVienAdmin(admin.ModelAdmin):
    readonly_fields = ('MaNhanVien',)
    list_display = ("MaNhanVien", "user", "ChucVu", "NgayVaoLam", action_icons)
    list_display_links = ("MaNhanVien",)
    search_fields = ("MaNhanVien", "user__username", "ChucVu")
    list_filter = ("ChucVu",)
    ordering = ("MaNhanVien",)
    date_hierarchy = "NgayVaoLam"

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    readonly_fields = ('MaBaiViet',)  # Ẩn trong form (chỉ đọc)
    list_display = ("MaBaiViet", "TieuDeBaiViet", "MaNhanVien", "TrangThaiHienThi", "NgayDang", action_icons)
    list_display_links = ("MaBaiViet",)
    list_editable = ("TrangThaiHienThi",)
    search_fields = ("MaBaiViet", "TieuDeBaiViet")
    list_filter = ("TrangThaiHienThi",)
    ordering = ("-NgayDang",)
    date_hierarchy = "NgayDang"
    list_per_page = 10

@admin.register(DichVu)
class DichVuAdmin(admin.ModelAdmin):
    readonly_fields = ('MaDichVu',)  # Ẩn trong form (chỉ đọc)
    list_display = ("MaDichVu", "TenDichVu", "MaDanhMuc", "TrangThaiHienThi", action_icons)
    list_display_links = ("MaDichVu",)
    list_editable = ("TrangThaiHienThi",)
    search_fields = ("MaDichVu", "TenDichVu")
    list_filter = ("TrangThaiHienThi", "MaDanhMuc")
    ordering = ("MaDichVu",)
    list_per_page = 10

@admin.register(DanhMucDichVu)
class DanhMucDichVuAdmin(admin.ModelAdmin):
    readonly_fields = ('MaDanhMuc',)  # Ẩn trong form (chỉ đọc)
    list_display = ("MaDanhMuc", "TenDanhMuc", "MoTa", action_icons)
    list_display_links = ("MaDanhMuc",)
    search_fields = ("MaDanhMuc", "TenDanhMuc")
    ordering = ("MaDanhMuc",)
    list_per_page = 10

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    readonly_fields = ('MaCauHoi',)  # Ẩn trong form (chỉ đọc)
    list_display = ("MaCauHoi", "CauHoi", "TrangThaiHienThi", "NgayCapNhat", action_icons)
    list_display_links = ("MaCauHoi",)
    list_editable = ("TrangThaiHienThi",)
    search_fields = ("MaCauHoi", "CauHoi")
    list_filter = ("TrangThaiHienThi",)
    ordering = ("MaCauHoi",)
    date_hierarchy = "NgayCapNhat"
    list_per_page = 10

@admin.register(LichSuTichDiem)
class LichSuTichDiemAdmin(admin.ModelAdmin):
    readonly_fields = ('MaGiaoDich',)  # Ẩn trong form (chỉ đọc)
    list_display = (
        "MaGiaoDich", "MaKhachHang", "LoaiGiaoDich",
        "SoDiemThayDoi", "NgayGiaoDich", "MaQuyDoi", action_icons
    )
    autocomplete_fields = ['MaKhachHang']
    list_display_links = ("MaGiaoDich",)
    search_fields = ("MaGiaoDich", "MaKhachHang__HoTen","MaKhachHang__MaKhachHang","MaKhachHang__user__username")
    list_filter = ("LoaiGiaoDich", "NgayGiaoDich")
    ordering = ("-NgayGiaoDich",)
    date_hierarchy = "NgayGiaoDich"
    list_per_page = 15


@admin.register(QuyDoiDiem)
class QuyDoiDiemAdmin(admin.ModelAdmin):
    readonly_fields = ('MaQuyDoi',)  # Ẩn trong form (chỉ đọc)
    list_display = ("MaQuyDoi", "GiaTriDiem", "GiaTriQuyDoi", action_icons)
    list_display_links = ("MaQuyDoi",)
    search_fields = ("MaQuyDoi",)
    ordering = ("MaQuyDoi",)
    list_per_page = 10

#LỊCH HẸN
@admin.register(LichHen)
class LichHenAdmin(admin.ModelAdmin):
    list_display = (
        "MaLichHen", "MaKhachHang", "MaNhanVien", "MaDichVu",
        "NgayDatLich", "NgayHen", "TrangThai", action_icons
    )
    list_display_links = ("MaLichHen",)
    list_editable = ("TrangThai",)
    search_fields = ("MaLichHen", "MaKhachHang__HoTen", "MaDichVu__TenDichVu")
    list_filter = ("TrangThai", "NgayHen")
    ordering = ("-NgayHen",)
    date_hierarchy = "NgayHen"
    list_per_page = 15


#ĐIỂM TÍCH LŨY
@admin.register(DiemTichLuy)
class DiemTichLuyAdmin(admin.ModelAdmin):
    list_display = ("MaKhachHang", "SoDiemHienTai", action_icons)
    list_display_links = ("MaKhachHang",)
    search_fields = ("MaKhachHang__MaKhachHang", "MaKhachHang__HoTen")
    ordering = ("MaKhachHang",)
    list_per_page = 10

# Register your models here.
admin.site.site_header = "Aurora Spa Administration"
admin.site.site_title  = "Aurora Spa CMS"
admin.site.index_title = "Bảng điều khiển"




from django.contrib import admin
from django.contrib import admin
from .models import KhachHang, NhanVien, DichVu, DanhMucDichVu, LichHen, DiemTichLuy, LichSuTichDiem, Blog, FAQ, DanhMucFAQ
from django.utils.html import format_html
#TEMPLATE DÙNG CHUNG

def action_icons(obj):
    return format_html(
        '<a class="icon-edit" href="{}">✏️</a>'
        '<a class="icon-trash" href="{}">🗑️</a>',
        f"{obj.pk}/change/",
        f"{obj.pk}/delete/",
    )
action_icons.short_description = "Thao tác"

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
    list_display = ("MaNhanVien", "user", "VaiTro", "NgayVaoLam", action_icons)
    list_display_links = ("MaNhanVien",)
    search_fields = ("MaNhanVien", "user__username", "VaiTro")
    list_filter = ("VaiTro",)
    ordering = ("MaNhanVien",)
    date_hierarchy = "NgayVaoLam"

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    readonly_fields = ('MaBaiViet',)  # Ẩn trong form (chỉ đọc)
    list_display = ("MaBaiViet", "TieuDeBaiViet", "MaNhanVien", "TrangThaiHienThi", "NgayCapNhat", action_icons)
    list_display_links = ("MaBaiViet",)
    list_editable = ("TrangThaiHienThi",)
    search_fields = ("MaBaiViet", "TieuDeBaiViet")
    list_filter = ("TrangThaiHienThi",)
    ordering = ("-NgayCapNhat",)
    date_hierarchy = "NgayCapNhat"
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

# =================================================================
# INLINE: Hiển thị và thêm/sửa/xóa FAQ ngay trong trang Danh mục
# =================================================================
class FAQInline(admin.TabularInline):
   model = FAQ
   extra = 1  # số dòng trống để thêm mới
   fields = ("MaCauHoi", "CauHoi", "TrangThaiHienThi", "NgayCapNhat")
   readonly_fields = ("MaCauHoi", "NgayCapNhat")
   show_change_link = True  # click vào MaCauHoi để mở chi tiết
   ordering = ("-NgayCapNhat",)


   # Rút gọn câu hỏi nếu quá dài trong inline
   def cau_hoi_ngan(self, obj):
       if obj.pk and len(obj.CauHoi) > 50:
           return obj.CauHoi[:50] + "..."
       return obj.CauHoi
   cau_hoi_ngan.short_description = "Câu hỏi"




# =================================================================
# ADMIN DANH MỤC FAQ
# =================================================================
@admin.register(DanhMucFAQ)
class DanhMucFAQAdmin(admin.ModelAdmin):
   list_display = ("MaDanhMuc", "TenDanhMuc", "so_faq_hien_thi", "TrangThaiHienThi", "NgayCapNhat")
   list_filter = ("TrangThaiHienThi", "NgayCapNhat")
   search_fields = ("MaDanhMuc", "TenDanhMuc")
   readonly_fields = ("MaDanhMuc", "NgayCapNhat")
   inlines = [FAQInline]  # ← Đây chính là phần "inline" siêu tiện


   # Đếm số FAQ đang hiển thị trong danh mục
   def so_faq_hien_thi(self, obj):
       count = obj.faq_list.filter(TrangThaiHienThi=True).count()
       return count if count else "-"
   so_faq_hien_thi.short_description = "Số FAQ hiển thị"


   # Tối ưu query
   def get_queryset(self, request):
       qs = super().get_queryset(request)
       return qs.prefetch_related("faq_list")




# =================================================================
# ADMIN CÂU HỎI FAQ
# =================================================================
@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
   list_display = ("MaCauHoi", "cau_hoi_ngan", "danh_muc", "nhan_vien", "TrangThaiHienThi", "NgayCapNhat")
   list_filter = ("TrangThaiHienThi", "MaDanhMuc__TenDanhMuc", "MaNhanVien", "NgayCapNhat")
   search_fields = ("MaCauHoi", "CauHoi", "CauTraLoi", "MaNhanVien__user__username", "MaNhanVien__MaNhanVien")
   readonly_fields = ("MaCauHoi", "NgayCapNhat")
   autocomplete_fields = ("MaDanhMuc", "MaNhanVien")


   fieldsets = (
       ("Nội dung câu hỏi", {"fields": ("MaCauHoi", "CauHoi", "CauTraLoi")}),
       ("Phân loại & trạng thái", {"fields": ("MaDanhMuc", "MaNhanVien", "TrangThaiHienThi")}),
       ("Thông tin hệ thống", {"fields": ("NgayCapNhat",), "classes": ("collapse",)}),
   )


   # Rút gọn câu hỏi
   def cau_hoi_ngan(self, obj):
       if len(obj.CauHoi) > 70:
           return obj.CauHoi[:70] + "..."
       return obj.CauHoi
   cau_hoi_ngan.short_description = "Câu hỏi"


   # Hiển thị danh mục
   def danh_muc(self, obj):
       return obj.MaDanhMuc.TenDanhMuc if obj.MaDanhMuc else "— Chưa phân loại —"
   danh_muc.short_description = "Danh mục"


   # HIỂN THỊ TÊN NHÂN VIÊN ĐÚNG THEO MODEL CỦA BẠN
   def nhan_vien(self, obj):
       if obj.MaNhanVien:
           username = obj.MaNhanVien.user.username if obj.MaNhanVien.user else "Chưa liên kết"
           return f"{obj.MaNhanVien.MaNhanVien} - {username}"
       return "— Chưa chọn —"
   nhan_vien.short_description = "Người tạo/spa"


   # Tối ưu query
   def get_queryset(self, request):
       return super().get_queryset(request).select_related("MaDanhMuc", "MaNhanVien__user")


@admin.register(LichSuTichDiem)
class LichSuTichDiemAdmin(admin.ModelAdmin):
    readonly_fields = ('MaGiaoDich', 'NgayGiaoDich', 'NgayCapNhat', 'NguoiThucHien', 'HanhDong')
    list_display = (
        "MaGiaoDich", "MaKhachHang", "LoaiGiaoDich",
        "formatted_diem", "NgayGiaoDich", "get_nguoi_thuc_hien", "HanhDong", action_icons
    )
    list_display_links = ("MaGiaoDich",)
    autocomplete_fields = ['MaKhachHang']
    search_fields = (
        "MaGiaoDich", "MaKhachHang__HoTen", "MaKhachHang__MaKhachHang",
        "NguoiThucHien__MaNhanVien", "NguoiThucHien__user__username"
    )
    list_filter = ("LoaiGiaoDich", "NgayGiaoDich", "NguoiThucHien")
    ordering = ("-NgayGiaoDich",)
    date_hierarchy = "NgayGiaoDich"
    list_per_page = 20

    def formatted_diem(self, obj):
        if obj.SoDiemThayDoi > 0:
            return f"+{obj.SoDiemThayDoi}"
        elif obj.SoDiemThayDoi < 0:
            return f"{obj.SoDiemThayDoi}"
        return "0"
    formatted_diem.short_description = "Điểm"

    def get_nguoi_thuc_hien(self, obj):
        if not obj.NguoiThucHien:
            return "—"
        nv = obj.NguoiThucHien
        ten = nv.user.get_full_name().strip() or nv.user.username
        return f"{nv.MaNhanVien} - {ten}"
    get_nguoi_thuc_hien.short_description = "Người thực hiện"
    get_nguoi_thuc_hien.admin_order_field = 'NguoiThucHien__MaNhanVien'

    # ĐOẠN QUAN TRỌNG NHẤT – BẮT BUỘC CÓ 2 DÒNG NÀY
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'MaKhachHang',
            'NguoiThucHien__user',   # ← Dòng này là "thần chú" fix 99% trường hợp không hiện tên
            'MaQuyDoi'
        )

    def save_model(self, request, obj, form, change):
        obj.save(current_user=request.user)




#LỊCH HẸN
@admin.register(LichHen)
class LichHenAdmin(admin.ModelAdmin):
    list_display = (
        "MaLichHen",
        "HoTen",
        "Email",
        "DienThoai",
        "get_danh_muc",
        "get_dich_vu",
        "NgayHen",
        "KhungGio",
        "TrangThai",
        "action_icons",
    )

    list_display_links = ("MaLichHen",)
    list_editable = ("TrangThai",)
    search_fields = ("MaLichHen", "HoTen", "Email", "DienThoai")
    list_filter = ("TrangThai", "NgayHen", "DanhMucDichVu")
    ordering = ("-NgayHen",)
    date_hierarchy = "NgayHen"
    list_per_page = 15

    # === Hiển thị tên danh mục ===
    def get_danh_muc(self, obj):
        return obj.DanhMucDichVu.TenDanhMuc if obj.DanhMucDichVu else "—"
    get_danh_muc.short_description = "Danh mục"

    # === Hiển thị tên dịch vụ ===
    def get_dich_vu(self, obj):
        return obj.DichVu.TenDichVu
    get_dich_vu.short_description = "Dịch vụ"

    # === Nếu bạn có action icons trong model ===
    def action_icons(self, obj):
        try:
            return obj.action_icons()
        except:
            return ""
    action_icons.short_description = ""
    action_icons.allow_tags = True


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




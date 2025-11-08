from django.db import models
from django.db.models import F
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinLengthValidator, EmailValidator
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User


class QuyDoiDiem(models.Model):
    MaQuyDoi = models.CharField(
        primary_key=True,   # thêm khóa chính
        max_length=5,
        help_text='Mã quy đổi'
    )
    GiaTriDiem = models.IntegerField(
        help_text='Giá trị điểm (số điểm cần để quy đổi)'
    )
    GiaTriQuyDoi = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Giá trị quy đổi tương ứng (VNĐ)'
    )

    class Meta:
        db_table = 'QuyDoiDiem'
        verbose_name = 'Quy Đổi Điểm'
        verbose_name_plural = 'Quy Đổi Điểm'

    def save(self, *args, **kwargs):
        if not self.MaQuyDoi:
            last = QuyDoiDiem.objects.order_by('-MaQuyDoi').first()
            if last:
                so = int(last.MaQuyDoi.replace("QD", "")) + 1
            else:
                so = 1
            self.MaQuyDoi = f"QD{so:03d}"
        super().save(*args, **kwargs)


class LichSuTichDiem(models.Model):
    MaGiaoDich = models.CharField(
        primary_key=True,   # thêm khóa chính
        max_length=5,
        help_text='Mã giao dịch'
    )

    LOAIGIAODICH_CHOICES = [
        ('Tích điểm', 'Tích điểm'),
        ('Quy đổi điểm', 'Quy đổi điểm'),
    ]

    LoaiGiaoDich = models.CharField(
        choices=LOAIGIAODICH_CHOICES,
        max_length=50,
        help_text='Loại giao dịch'
    )
    ChiTietGiaoDich = models.CharField(
        max_length=300,
        help_text='Chi tiết giao dịch'
    )
    NgayGiaoDich = models.DateTimeField(
        auto_now_add=True,
        help_text='Ngày giao dịch'
    )
    MaQuyDoi = models.ForeignKey(
        QuyDoiDiem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Chính sách quy đổi được áp dụng (nếu có)"
    )
    MaKhachHang = models.ForeignKey(
        "KhachHang",  # giữ dạng chuỗi để tránh lỗi import
        on_delete=models.CASCADE,
        help_text="Khách hàng thực hiện giao dịch"
    )
    SoDiemThayDoi = models.IntegerField(
        help_text="Số điểm thay đổi (+ hoặc -)"
    )

    def save(self, *args, **kwargs):
        from .models import DiemTichLuy  # import cục bộ để tránh vòng lặp

        # TẠO MÃ TỰ ĐỘNG
        if not self.MaGiaoDich:
            last = LichSuTichDiem.objects.order_by('-MaGiaoDich').first()
            if last:
                # Lấy phần số từ mã cuối + 1
                so = int(last.MaGiaoDich.replace("GD", "")) + 1
            else:
                so = 1
            self.MaGiaoDich = f"GD{so:03d}"  # => GD001, GD002,...

        # Lấy ví điểm hiện tại
        diem_tl = DiemTichLuy.objects.get(MaKhachHang=self.MaKhachHang)

        # Kiểm tra không trừ quá số điểm hiện có
        if self.SoDiemThayDoi < 0 and diem_tl.SoDiemHienTai + self.SoDiemThayDoi < 0:
            raise ValidationError("Không thể trừ quá số điểm hiện có!")

        # Lưu bản ghi
        super().save(*args, **kwargs)

        # Cập nhật tổng điểm
        DiemTichLuy.objects.filter(MaKhachHang=self.MaKhachHang).update(
            SoDiemHienTai=F('SoDiemHienTai') + self.SoDiemThayDoi
        )

    class Meta:
        db_table = 'LichSuTichDiem'
        verbose_name = 'Lịch Sử Tích Điểm'
        verbose_name_plural = 'Lịch Sử Tích Điểm'

    def __str__(self):
        sign = "+" if self.SoDiemThayDoi >= 0 else ""
        return f"{self.MaGiaoDich} ({sign}{self.SoDiemThayDoi} điểm)"


# Mỗi khách hàng đăng ký tài khoản đều có điểm tích lũy (tự động tạo khi KhachHang được tạo)
@receiver(post_save, sender="aurora.KhachHang")  # thay 'your_app_name' = tên app thật
def tao_diem_tich_luy(sender, instance, created, **kwargs):
    from .models import DiemTichLuy
    if created:
        DiemTichLuy.objects.create(MaKhachHang=instance, SoDiemHienTai=0)


class FAQ (models.Model):
    MaCauHoi = models.CharField(
        max_length=5,
        primary_key=True,
        help_text='Mã câu hỏi'
    )
    MaNhanVien=models. ForeignKey('NhanVien', on_delete=models.CASCADE, help_text='Mã nhân viên')
    CauHoi=models.CharField(
        max_length=300,
        help_text='Cau Hoi'
    )
    CauTraLoi=models.TextField(
        help_text='Câu trả lời'
    )
    NgayCapNhat=models.DateTimeField(
        auto_now_add=True,
        help_text='Ngày cập nhật gần nhất'
    )
    TrangThaiHienThi=models.BooleanField(default=True, help_text="Trạng thái hiển thị")

    class Meta:
        db_table = 'FAQ'
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQ'

    def save(self, *args, **kwargs):
        if not self.MaCauHoi:
            last = FAQ.objects.order_by('-MaCauHoi').first()
            if last:
                so = int(last.MaCauHoi.replace("CH", "")) + 1
            else:
                so = 1
            self.MaCauHoi = f"CH{so:03d}"
        super().save(*args, **kwargs)


# MODEL: KHÁCH HÀNG
class KhachHang(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    MaKhachHang = models.CharField(
        max_length=5,
        primary_key=True,
        blank=True,  # <— thêm
        # bỏ MinLengthValidator(5) nếu muốn gọn
        help_text="VD: KH001"
    )

    SDT = models.CharField(max_length=10)
    Email = models.EmailField(
        max_length=255,
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'KhachHang'
        verbose_name = 'Khách Hàng'
        verbose_name_plural = 'Khách Hàng'

    def __str__(self):
        return f"{self.MaKhachHang} - {self.user.username if self.user else 'Không có user'}"

    def save(self, *args, **kwargs):
        if not self.MaKhachHang:
            last = KhachHang.objects.order_by('-MaKhachHang').first()
            so = int(last.MaKhachHang.replace("KH", "")) + 1 if last else 1
            self.MaKhachHang = f"KH{so:03d}"
        super().save(*args, **kwargs)

# MODEL: LỊCH HẸN
class LichHen(models.Model):
    # Trạng thái hợp lệ
    TRANG_THAI_CHOICES = [
        ('Đang chờ', 'Đang chờ'),
        ('Đang thực hiện', 'Đang thực hiện'),
        ('Hoàn thành', 'Hoàn thành'),
        ('Đã hủy', 'Đã hủy'),
    ]

    MaLichHen = models.CharField(
        max_length=5,
        primary_key=True,
        validators=[MinLengthValidator(5)],
        help_text="Mã định danh duy nhất cho từng lịch hẹn (LH001, LH002,...)"
    )

    MaKhachHang = models.ForeignKey(
        KhachHang,
        on_delete=models.CASCADE,
        db_column='MaKhachHang',
        help_text="Mã duy nhất đại diện cho mỗi khách hàng"
    )

    MaNhanVien = models.ForeignKey(
        'NhanVien', on_delete=models.CASCADE, db_column='MaNhanVien'
    )
    MaDichVu = models.ForeignKey(
        'DichVu', on_delete=models.CASCADE, db_column='MaDichVu'
    )

    NgayDatLich = models.DateTimeField(
        help_text="Ngày và giờ khách thực hiện đặt lịch"
    )

    NgayHen = models.DateTimeField(
        help_text="Ngày và giờ hẹn thực tế để thực hiện dịch vụ"
    )

    TrangThai = models.CharField(
        max_length=25,
        choices=TRANG_THAI_CHOICES,
        help_text="Mô tả trạng thái hiện tại của lịch hẹn"
    )

    class Meta:
        db_table = 'LichHen'
        verbose_name = 'Lịch Hẹn'
        verbose_name_plural = 'Lịch Hẹn'
        constraints = [
            models.CheckConstraint(
                check=models.Q(TrangThai__in=[
                    'Đang chờ', 'Đang thực hiện', 'Hoàn thành', 'Đã hủy'
                ]),
                name='chk_trangthai_lichhen'
            )
        ]

    def save(self, *args, **kwargs):
        if not self.MaLichHen:
            last = LichHen.objects.order_by('-MaLichHen').first()
            if last:
                so = int(last.MaLichHen.replace("LH", "")) + 1
            else:
                so = 1
            self.MaLichHen = f"LH{so:03d}"
        super().save(*args, **kwargs)


# MODEL: DANH MỤC DỊCH VỤ
class DanhMucDichVu(models.Model):
    MaDanhMuc = models.CharField(
        max_length=5,
        primary_key=True,
        validators=[MinLengthValidator(5)],
        help_text="Mã định danh duy nhất cho từng danh mục dịch vụ Spa (VD: DM001, DM002, ...)"
    )

    TenDanhMuc = models.CharField(
        max_length=200,
        null=False,
        help_text="Tên danh mục dịch vụ (VD: 'Chăm sóc da mặt', 'Massage thư giãn')"
    )

    MoTa = models.TextField(
        null=True,
        blank=True,
        help_text="Mô tả chi tiết về nhóm dịch vụ (VD: các loại liệu trình trong danh mục)"
    )

    class Meta:
        db_table = 'DanhMucDichVu'
        verbose_name = 'Danh Mục Dịch Vụ'
        verbose_name_plural = 'Danh Mục Dịch Vụ'

    def save(self, *args, **kwargs):
        if not self.MaDanhMuc:
            last = DanhMucDichVu.objects.order_by('-MaDanhMuc').first()
            if last:
                so = int(last.MaDanhMuc.replace("DM", "")) + 1
            else:
                so = 1
            self.MaDanhMuc = f"DM{so:03d}"
        super().save(*args, **kwargs)


# MODEL: DỊCH VỤ
class DichVu(models.Model):
    MaDichVu = models.CharField(
        max_length=5,
        primary_key=True,
        validators=[MinLengthValidator(5)],
        help_text="Mã định danh duy nhất cho từng dịch vụ (VD: DV001, DV002, ...)"
    )

    MaDanhMuc = models.ForeignKey(
        DanhMucDichVu,
        on_delete=models.CASCADE,
        db_column='MaDanhMuc',
        help_text="Khóa ngoại liên kết đến bảng DanhMucDichVu (MaDanhMuc)"
    )

    TenDichVu = models.CharField(
        max_length=200,
        null=False,
        help_text="Tên dịch vụ Spa (VD: 'Massage đá nóng', 'Trị mụn chuyên sâu')"
    )

    MoTa = models.TextField(
        null=False,
        help_text="Mô tả nội dung, liệu trình, sản phẩm sử dụng, giá và thời gian dịch vụ"
    )

    TrangThaiHienThi = models.BooleanField(
        default=True,
        help_text="Trạng thái hiển thị dịch vụ (1 = đang kinh doanh, 0 = tạm ẩn)"
    )
    HinhAnh = models.ImageField(upload_to='dichvu/', blank=True, null=True)

    class Meta:
        db_table = 'DichVu'
        verbose_name = 'Dịch Vụ'
        verbose_name_plural = 'Dịch Vụ'

    def save(self, *args, **kwargs):
        if not self.MaDichVu:
            last = DichVu.objects.order_by('-MaDichVu').first()
            if last:
                so = int(last.MaDichVu.replace("DV", "")) + 1
            else:
                so = 1
            self.MaDichVu = f"DV{so:03d}"
        super().save(*args, **kwargs)


# MODEL: ĐIỂM TÍCH LŨY
class DiemTichLuy(models.Model):
    MaKhachHang = models.OneToOneField(
        'KhachHang',                      # Khóa ngoại liên kết đến bảng KhachHang
        on_delete=models.CASCADE,
        db_column='MaKhachHang',
        primary_key=True,                 # Vừa là khóa chính, vừa là khóa ngoại
        validators=[MinLengthValidator(5)],
        help_text="Mã khách hàng (VD: KH001, KH002, ...)"
    )

    SoDiemHienTai = models.IntegerField(
        default=0,
        help_text="Số điểm tích lũy hiện tại của khách hàng"
    )

    class Meta:
        db_table = 'DiemTichLuy'
        verbose_name = 'Điểm Tích Lũy'
        verbose_name_plural = 'Điểm Tích Lũy'

    def __str__(self):
        return f"{self.MaKhachHang.MaKhachHang} - {self.MaKhachHang.user.username if self.MaKhachHang.user else 'Không có user'} ({self.SoDiemHienTai} điểm)"


class NhanVien(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    MaNhanVien = models.CharField(max_length=5, primary_key=True, blank=True)
    ChucVu = models.CharField(max_length=100)
    NgayVaoLam = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'NhanVien'
        verbose_name = 'Nhân Viên'
        verbose_name_plural = 'Nhân Viên'

    def __str__(self):
        return f"{self.MaNhanVien} - {self.user.username if self.user else 'Không có user'}"

    def save(self, *args, **kwargs):
        if not self.MaNhanVien:
            last = NhanVien.objects.order_by('-MaNhanVien').first()
            so = int(last.MaNhanVien.replace("NV", "")) + 1 if last else 1
            self.MaNhanVien = f"NV{so:03d}"
        super().save(*args, **kwargs)

class Blog(models.Model):
    MaBaiViet = models.CharField(max_length=5, primary_key=True)
    MaNhanVien = models.ForeignKey(
        'NhanVien',
        on_delete=models.CASCADE,
        db_column='MaNhanVien',
        help_text='Nhân viên đăng bài viết'
    )
    TieuDeBaiViet = models.CharField(max_length=200)
    NoiDungBaiViet = models.TextField()
    NgayDang = models.DateTimeField()
    TrangThaiHienThi = models.BooleanField(default=True)
    HinhAnh = models.ImageField(upload_to='blog/', blank=True, null=True)

    class Meta:
        db_table = 'Blog'
        verbose_name = 'Blog'
        verbose_name_plural = 'Blog'

    def save(self, *args, **kwargs):
        if not self.MaBaiViet:
            last = Blog.objects.order_by('-MaBaiViet').first()
            if last:
                so = int(last.MaBaiViet.replace("BV", "")) + 1
            else:
                so = 1
            self.MaBaiViet = f"BV{so:03d}"
        super().save(*args, **kwargs)



# Create your models here.

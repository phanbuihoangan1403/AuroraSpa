from django.db import models
from django.db.models import F
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinLengthValidator, EmailValidator
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.db import transaction
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

    def __str__(self):
        return self.MaQuyDoi

class LichSuTichDiem(models.Model):
    MaGiaoDich = models.CharField(
        primary_key=True,
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
        'QuyDoiDiem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Chính sách quy đổi được áp dụng (nếu có)"
    )
    MaKhachHang = models.ForeignKey(
        'KhachHang',
        on_delete=models.CASCADE,
        help_text="Khách hàng thực hiện giao dịch"
    )
    SoDiemThayDoi = models.IntegerField(
        help_text="Số điểm thay đổi (+ hoặc -)"
    )

    def save(self, *args, **kwargs):
        from .models import DiemTichLuy

        # === 1. Tạo mã tự động ===
        if not self.MaGiaoDich:
            last = LichSuTichDiem.objects.order_by('-MaGiaoDich').first()
            so = int(last.MaGiaoDich.replace("GD", "")) + 1 if last else 1
            self.MaGiaoDich = f"GD{so:03d}"

        # === 2. Tính delta (chênh lệch điểm so với lần trước) ===
        old_value = 0
        if self.pk:  # nếu đang sửa bản ghi
            try:
                old_obj = LichSuTichDiem.objects.get(pk=self.pk)
                old_value = old_obj.SoDiemThayDoi
            except LichSuTichDiem.DoesNotExist:
                old_value = 0

        delta = self.SoDiemThayDoi - old_value

        # === 3. Cập nhật ví điểm theo delta ===
        with transaction.atomic():
            wallet, _ = DiemTichLuy.objects.select_for_update().get_or_create(
                MaKhachHang=self.MaKhachHang,
                defaults={"SoDiemHienTai": 0}
            )

            # Kiểm tra không trừ quá số điểm hiện có
            if delta < 0 and wallet.SoDiemHienTai + delta < 0:
                raise ValidationError("Không thể trừ quá số điểm hiện có!")

            # Lưu lịch sử giao dịch
            super().save(*args, **kwargs)

            # Cập nhật ví điểm
            DiemTichLuy.objects.filter(MaKhachHang=self.MaKhachHang).update(
                SoDiemHienTai=F('SoDiemHienTai') + delta
            )

    def clean(self):
        # Ràng buộc giá trị hợp lệ theo loại giao dịch
        if self.LoaiGiaoDich == 'Tích điểm' and self.SoDiemThayDoi < 0:
            raise ValidationError("Giao dịch 'Tích điểm' phải là số dương.")
        if self.LoaiGiaoDich == 'Quy đổi điểm' and self.SoDiemThayDoi > 0:
            raise ValidationError("Giao dịch 'Quy đổi điểm' phải là số âm.")

    class Meta:
        db_table = 'LichSuTichDiem'
        verbose_name = 'Lịch Sử Tích Điểm'
        verbose_name_plural = 'Lịch Sử Tích Điểm'

    def __str__(self):
        sign = "+" if self.SoDiemThayDoi >= 0 else ""
        return f"{self.MaGiaoDich} ({sign}{self.SoDiemThayDoi} điểm)"


# === Signal tạo ví điểm tự động khi có Khách hàng mới ===
@receiver(post_save, sender='aurora.KhachHang')  # thay 'aurora' bằng đúng tên app của bạn
def tao_diem_tich_luy(sender, instance, created, **kwargs):
    from .models import DiemTichLuy
    if created:
        DiemTichLuy.objects.get_or_create(
            MaKhachHang=instance,
            defaults={"SoDiemHienTai": 0}
        )


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
    def __str__(self):
        return f"{self.MaCauHoi} - {self.CauHoi}"


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
    HoTen=models.CharField(max_length=200)
    SDT = models.CharField(max_length=10)
    Email = models.EmailField(
        max_length=255,
        blank=True,
        null=True
    )
    DiaChi=models.CharField(max_length=300)
    NgaySinh=models.DateField(null=True, blank=True)
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

    # Thông tin khách hàng (tách FK hoặc lưu trực tiếp)
    HoTen = models.CharField("Họ và tên", max_length=100,null=True, blank=True)
    Email = models.EmailField("Email",null=True, blank=True)
    DienThoai = models.CharField("SĐT di động", max_length=15,null=True, blank=True)

    # Dịch vụ
    DanhMucDichVu = models.ForeignKey('DanhMucDichVu', on_delete=models.PROTECT, null=True, blank=True)
    DichVu = models.ForeignKey('DichVu', on_delete=models.PROTECT, related_name='lichhen_dichvu', null=True,
    blank=True)

    # Thời gian
    NgayHen = models.DateField("Ngày đặt")
    KhungGio = models.CharField("Khung giờ", max_length=10,null=True, blank=True)  # có thể thêm choices nếu muốn

    # Mã giảm giá & trạng thái
    MaGiamGia = models.CharField("Mã giảm giá", max_length=20, blank=True, null=True)
    TrangThai = models.CharField("Trạng thái", max_length=25, choices=TRANG_THAI_CHOICES, default='Đang chờ')

    class Meta:
        db_table = 'LichHen'
        verbose_name = 'Lịch Hẹn'
        verbose_name_plural = 'Lịch Hẹn'

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
    def __str__(self):
        return f"{self.MaDanhMuc} - {self.TenDanhMuc}"


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

    MoTa = RichTextField()

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
    def __str__(self):
        return f"{self.MaDichVu} - {self.TenDichVu}"


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
    NoiDungBaiViet = RichTextField()
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

    def __str__(self):
        return f"{self.MaBaiViet} - {self.TieuDeBaiViet}"

# Create your models here.

from django.db import models
from django.db import models
from django.utils import timezone

class NhatKyHoatDong(models.Model):
    nhan_vien = models.ForeignKey(
        'aurora.NhanVien',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff_logs'
    )
    hanh_dong = models.CharField(max_length=255)
    doi_tuong = models.CharField(max_length=100, blank=True)   # FAQ, Blog, LichHen...
    object_id = models.CharField(max_length=50, blank=True)
    mo_ta = models.TextField(blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    thoi_gian = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'StaffActivityLog'
        ordering = ['-thoi_gian']

    def __str__(self):
        nv = self.nhan_vien.MaNhanVien if self.nhan_vien else "N/A"
        return f"[{self.thoi_gian:%d/%m %H:%M}] {nv} - {self.hanh_dong}"

# Create your models here.

# aurora/utils.py
from django.db.models import Count
from .models import NhanVien, LichHen

DANH_MUC_TO_NHOM = {
    'DM001': 'DA_MAT',
    'DM002': 'MASSAGE',
    'DM003': 'NAIL',
    'DM004': 'TOAN_THAN',
}

def phan_nhan_vien_tu_dong(ma_danh_muc, ngay_hen, khung_gio):
    nhom = DANH_MUC_TO_NHOM.get(ma_danh_muc)
    if not nhom:
        return None

    candidates = NhanVien.objects.filter(VaiTro='STAFF', NhomChuyenVien=nhom).order_by('MaNhanVien')

    # Loại bỏ nhân viên đã có lịch trong khung giờ đó
    da_dat = LichHen.objects.filter(
        NgayHen=ngay_hen,
        KhungGio=khung_gio,
        TrangThai__in=['Đang chờ', 'Đang thực hiện', 'Hoàn thành']
    ).values_list('NhanVienThucHien', flat=True)

    candidates = candidates.exclude(pk__in=da_dat)
    if not candidates.exists():
        return None

    # Chọn người ít lịch nhất trong ngày
    stats = LichHen.objects.filter(NgayHen=ngay_hen, NhanVienThucHien__in=candidates)\
        .values('NhanVienThucHien').annotate(count=Count('pk'))
    count_dict = {item['NhanVienThucHien']: item['count'] for item in stats}

    best_cv = min(candidates, key=lambda cv: (count_dict.get(cv.pk, 0), cv.MaNhanVien))
    return best_cv
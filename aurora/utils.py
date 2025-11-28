# aurora/utils.py
from django.db.models import Count
from .models import NhanVien, LichHen, DanhMucDichVu

# Mapping chính xác theo dữ liệu thực tế của bạn
DANH_MUC_TO_NHOM = {
    'DM001': 'DA_MAT',      # Chăm sóc da mặt
    'DM002': 'MASSAGE',     # Massage thư giãn
    'DM003': 'NAIL',        # Chăm sóc tay và chân
    'DM004': 'TOAN_THAN',   # Liệu trình làm đẹp toàn thân
}

def phan_nhan_vien_tu_dong(ma_danh_muc, ngay_hen):
    """
    Phân chuyên viên xoay vòng đều theo đúng nhóm danh mục
    """
    nhom = DANH_MUC_TO_NHOM.get(ma_danh_muc)
    if not nhom:
        return None

    # Lấy tất cả chuyên viên trong nhóm, sắp xếp theo mã để xoay vòng ổn định
    candidates = NhanVien.objects.filter(
        VaiTro='STAFF',
        NhomChuyenVien=nhom
    ).order_by('MaNhanVien')

    if not candidates.exists():
        return None

    # Đếm số lịch trong ngày (không tính đã hủy)
    stats = LichHen.objects.filter(
        .filter(
            NgayHen=ngay_hen,
            NhanVienThucHien__in=candidates,
            TrangThai__in=['Đang chờ', 'Đang thực hiện', 'Hoàn thành']
        )        .values('NhanVienThucHien')        .annotate(count=Count('pk'))

    count_dict = {item['NhanVienThucHien']: item['count'] for item in stats}

    # Chọn người có ít lịch nhất → nếu bằng nhau thì chọn người có mã nhỏ nhất (xoay vòng đều đẹp)
    best_cv = min(candidates, key=lambda cv: (count_dict.get(cv.pk, 0), cv.MaNhanVien))
    return best_cv
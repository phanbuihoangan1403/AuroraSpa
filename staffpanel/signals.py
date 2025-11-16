from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.utils import timezone

from aurora.models import NhanVien
from .models import NhatKyHoatDong


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


@receiver(user_logged_in)
def staff_logged_in(sender, request, user, **kwargs):
    try:
        nv = user.nhanvien
    except NhanVien.DoesNotExist:
        return

    nv.is_online = True
    nv.save(update_fields=['is_online'])

    NhatKyHoatDong.objects.create(
        nhan_vien=nv,
        hanh_dong="Đăng nhập hệ thống nhân viên",
        doi_tuong="AUTH",
        object_id=str(user.id),
        ip=get_client_ip(request),
        thoi_gian=timezone.now()
    )


@receiver(user_logged_out)
def staff_logged_out(sender, request, user, **kwargs):
    try:
        nv = user.nhanvien
    except (NhanVien.DoesNotExist, AttributeError):
        return

    nv.is_online = False
    nv.save(update_fields=['is_online'])

    NhatKyHoatDong.objects.create(
        nhan_vien=nv,
        hanh_dong="Đăng xuất hệ thống nhân viên",
        doi_tuong="AUTH",
        object_id=str(user.id),
        ip=get_client_ip(request),
        thoi_gian=timezone.now()
    )

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import NhanVien

@receiver(post_save, sender=User)
def create_staff_profile(sender, instance, created, **kwargs):
    if created and instance.is_staff:
        # Nếu là STAFF thì VaiTro = 'STAFF', nếu là MANAGER thì giữ 'MANAGER'
        vai_tro = 'STAFF' if not hasattr(instance, 'nhanvien') else instance.nhanvien.VaiTro
        NhanVien.objects.get_or_create(user=instance, defaults={'VaiTro': vai_tro})
@receiver(post_save, sender=NhanVien)
def set_user_staff(sender, instance, created, **kwargs):
    if instance.user:
        user = instance.user
        if not user.is_staff:
            user.is_staff = True
            user.save()
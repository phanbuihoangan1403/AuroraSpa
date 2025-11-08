from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import NhanVien

@receiver(post_save, sender=User)
def create_staff_profile(sender, instance, created, **kwargs):
    if instance.is_staff:
        NhanVien.objects.get_or_create(user=instance, defaults={'ChucVu': 'Nhân viên'})

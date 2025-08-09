from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Quản trị viên'),
        ('staff', 'Nhân viên'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Người dùng")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff', verbose_name="Vai trò")
    phone = models.CharField(max_length=15, blank=True, verbose_name="Số điện thoại")
    address = models.TextField(blank=True, verbose_name="Địa chỉ")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Ảnh đại diện")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Hồ sơ người dùng"
        verbose_name_plural = "Hồ sơ người dùng"

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_staff(self):
        return self.role == 'staff'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Đảm bảo luôn có Profile gắn với User; tránh lỗi khi User chưa có profile
    from django.core.exceptions import ObjectDoesNotExist
    try:
        instance.profile  # truy cập để kiểm tra tồn tại
    except ObjectDoesNotExist:
        Profile.objects.get_or_create(user=instance)
    else:
        instance.profile.save()
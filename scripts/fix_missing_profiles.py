from django.contrib.auth import get_user_model
from accounts.models import Profile

User = get_user_model()

def fix_missing_profiles():
    created = 0
    for user in User.objects.all():
        if not hasattr(user, 'profile'):
            Profile.objects.create(user=user, role='admin')  # Hoặc 'staff' nếu muốn
            print(f"Đã tạo profile cho user: {user.username}")
            created += 1
    if created == 0:
        print("Tất cả user đều đã có profile.")
    else:
        print(f"Đã tạo {created} profile bị thiếu.")

if __name__ == "__main__":
    fix_missing_profiles() 
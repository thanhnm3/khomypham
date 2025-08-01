from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .forms import ProfileUpdateForm

@login_required
def profile(request):
    """Hiển thị và cập nhật hồ sơ người dùng"""
    if request.method == 'POST':
        user_form = UserChangeForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Hồ sơ đã được cập nhật thành công!')
            return redirect('profile')
    else:
        user_form = UserChangeForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/profile.html', context)

def logout_view(request):
    """View đăng xuất tùy chỉnh"""
    logout(request)
    messages.success(request, 'Bạn đã đăng xuất thành công!')
    return redirect('login')

@login_required
def user_info(request):
    """Hiển thị thông tin chi tiết của user"""
    user = request.user
    context = {
        'user': user,
        'profile': user.profile,
    }
    return render(request, 'accounts/user_info.html', context) 
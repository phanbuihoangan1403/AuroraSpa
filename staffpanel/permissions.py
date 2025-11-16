from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden


def role_required(*roles):
    """
    Ví dụ:
    @role_required('MANAGER', 'CONTENT')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('staff_login')

            try:
                nv = request.user.nhanvien
            except Exception:
                return HttpResponseForbidden("Bạn không phải nhân viên Aurora.")

            if nv.VaiTro in roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            return HttpResponseForbidden("Bạn không có quyền truy cập chức năng này.")
        return _wrapped
    return decorator


manager_required = role_required('MANAGER')
content_required = role_required('MANAGER', 'CONTENT')
reception_required = role_required('MANAGER', 'RECEPTION')

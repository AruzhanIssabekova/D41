from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView


urlpatterns = [
    path('bboard/', include('bboard.urls', namespace='bboard')),
    path('admin/', admin.site.urls),
    path('captcha/', include('captcha.urls')),


    path('account/login/', LoginView.as_view(next_page='bboard:index'), name='login'),
    path('account/logout/', LogoutView.as_view(), name='logout'),
    path('account/password_change/', PasswordChangeView.as_view(template_name='registration/change_password.html'), name='password_change'),
    path('account/password_change/done/', PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    path('account/password_reset/', PasswordResetView.as_view(template_name='registration/reset_password.html', subject_template_name='C:\\Users\\1\\Desktop\\Новая папка\\samplesite\\templates\\registration\\reset_subject.txt', email_template_name='registration/reset_email.txt'), name='password_reset'),
    path('account/password_reset/done/', PasswordResetDoneView.as_view(template_name='registration/reset_password_done.html'), name='password_reset_done'),
    path('account/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='registration/reset_password_confirm.html'), name='password_reset_confirm'),
    path('account/reset/done/', PasswordResetCompleteView.as_view(template_name='registration/reset_password_complete.html'), name='password_reset_complete'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


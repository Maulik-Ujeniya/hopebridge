from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Onboarding (4 steps)
    path('onboarding/step-1/', views.onboarding_step1, name='onboarding_step1'),
    path('onboarding/step-2/', views.onboarding_step2, name='onboarding_step2'),
    path('onboarding/step-3/', views.onboarding_step3, name='onboarding_step3'),
    path('onboarding/step-4/', views.onboarding_step4, name='onboarding_step4'),
    path('onboarding/success/', views.onboarding_success, name='onboarding_success'),

    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('password/change/', views.change_password_view, name='change_password'),

    path('password/reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset_form.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
        success_url='/accounts/password/reset/done/',
    ), name='password_reset'),
    path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html',
    ), name='password_reset_done'),
    path('password/reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/accounts/password/reset/complete/',
    ), name='password_reset_confirm'),
    path('password/reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html',
    ), name='password_reset_complete'),
]

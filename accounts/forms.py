from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import CustomUser, UserPreference


class RegistrationForm(UserCreationForm):
    """Registration form — Step 1 of the signup flow."""

    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name',
            'autocomplete': 'given-name',
        })
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name',
            'autocomplete': 'family-name',
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
            'autocomplete': 'email',
        })
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number',
            'autocomplete': 'tel',
        })
    )
    country = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Country',
        })
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City',
        })
    )
    pincode = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Pin Code',
        })
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'new-password',
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password',
        })
    )
    agree_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='I agree to the Terms & Conditions'
    )

    class Meta:
        model = CustomUser
        fields = [
            'profile_picture', 'first_name', 'last_name', 'email',
            'phone', 'country', 'city', 'pincode',
            'password1', 'password2',
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email  # Use email as username
        if commit:
            user.save()
        return user


class ProfileEditForm(forms.ModelForm):
    """Form to edit user profile."""

    class Meta:
        model = CustomUser
        fields = [
            'profile_picture', 'first_name', 'last_name',
            'phone', 'country', 'city', 'pincode', 'full_address',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'full_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }


class UserPreferenceEditForm(forms.ModelForm):
    """Form to edit user onboarding preferences."""

    class Meta:
        model = UserPreference
        fields = [
            'wants_to_donate', 'wants_to_volunteer', 'wants_to_manage',
            'preferred_role', 'experience_level', 'skills', 
            'availability_hours', 'availability_days', 
            'motivation', 'future_goals'
        ]
        widgets = {
            'wants_to_donate': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'wants_to_volunteer': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'wants_to_manage': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'preferred_role': forms.Select(attrs={'class': 'form-select'}),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
            'availability_days': forms.Select(attrs={'class': 'form-select'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'motivation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'future_goals': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'availability_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    """Styled password change form."""

    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Current Password',
        })
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New Password',
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm New Password',
        })
    )


# --- Onboarding Step Forms ---

class OnboardingStep1Form(forms.ModelForm):
    """Step 1: What would you like to contribute?"""

    class Meta:
        model = UserPreference
        fields = ['wants_to_donate', 'wants_to_volunteer', 'wants_to_manage']
        widgets = {
            'wants_to_donate': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'wants_to_volunteer': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'wants_to_manage': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class OnboardingStep2Form(forms.ModelForm):
    """Step 2: Role selection."""

    class Meta:
        model = UserPreference
        fields = ['preferred_role', 'experience_level']
        widgets = {
            'preferred_role': forms.Select(
                choices=[
                    ('', 'Select your preferred role'),
                    ('donor', 'Donor — Support through donations'),
                    ('volunteer', 'Volunteer — On-ground work'),
                    ('coordinator', 'Coordinator — Organize drives & events'),
                    ('manager', 'Manager — Lead & manage operations'),
                ],
                attrs={'class': 'form-select'}
            ),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
        }


class OnboardingStep3Form(forms.ModelForm):
    """Step 3: Skills, availability & categories."""

    CATEGORY_CHOICES = [
        ('health', 'Health & Medical'),
        ('education', 'Education'),
        ('food', 'Food Donation'),
        ('clothing', 'Clothing Donation'),
        ('orphanage', 'Orphanage (Anath Ashram)'),
        ('old_age', 'Old-Age Home (Vridha Ashram)'),
        ('animal_rescue', 'Animal Rescue'),
        ('environment', 'Environment & Tree Plantation'),
        ('hospital_build', 'Hospital Building'),
        ('school_build', 'School Building'),
    ]

    preferred_categories = forms.MultipleChoiceField(
        choices=CATEGORY_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )

    class Meta:
        model = UserPreference
        fields = ['preferred_categories', 'skills', 'availability_hours', 'availability_days']
        widgets = {
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'e.g., Teaching, First Aid, Cooking, Driving...'}),
            'availability_hours': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Hours per week', 'min': 0}),
            'availability_days': forms.Select(attrs={'class': 'form-select'}),
        }


class OnboardingStep4Form(forms.ModelForm):
    """Step 4: Goals & motivation."""

    class Meta:
        model = UserPreference
        fields = ['motivation', 'future_goals', 'how_did_you_hear']
        widgets = {
            'motivation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'What inspired you to join HopeBridge? What drives your passion for social work?'
            }),
            'future_goals': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'What do you hope to achieve with HopeBridge in the future?'
            }),
            'how_did_you_hear': forms.Select(
                choices=[
                    ('', 'How did you hear about us?'),
                    ('social_media', 'Social Media'),
                    ('friend', 'Friend / Family'),
                    ('news', 'News / Media'),
                    ('search', 'Google Search'),
                    ('event', 'At an Event'),
                    ('other', 'Other'),
                ],
                attrs={'class': 'form-select'}
            ),
        }

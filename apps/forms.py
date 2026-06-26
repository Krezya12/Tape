from django.contrib.auth import login
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.forms import ModelForm, Form, CharField, Select, ModelChoiceField
from django.contrib import messages
from .models import *


class GroupModelForm(ModelForm):
    teacher = ModelChoiceField(
        queryset=User.objects.filter(role=User.Role.TEACHER),
        label="Teacher",
        widget=Select(attrs={'class': 'form-control'})
    )

    current_module = ModelChoiceField(
        queryset=Module.objects.all(),
        label="Current Module",
        widget=Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Group
        fields = ('technology', )

    def clean(self):
        cleaned_data = super().clean()
        technology = cleaned_data.get('technology')

        if technology:
            first_letter = technology[0].upper()
            count = Group.objects.filter(technology=technology).count() + 1
            cleaned_data['title'] = f"{first_letter}{count}"

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.title = self.cleaned_data.get('title')

        first_module = Module.objects.filter(number=1).first()
        instance.current_module = first_module

        if commit:
            instance.save()

            if first_module:
                GroupModuleTeacher.objects.create(
                    group=instance,
                    module=first_module,
                    teacher=self.cleaned_data.get('teacher')
                )

        return instance


class UserModelForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'phone', 'role', 'password', 'first_name', 'last_name')

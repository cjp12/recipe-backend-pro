"""Django admin customization"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models

# This is a custom user admin class that is going to display
class UserAdmin(BaseUserAdmin):
    """Define the admine pages for users"""

    # Configure how the page is displayed
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None,{'fields': ('email', 'password')}),
        (
            _('Permissions'),
            {
                'fields':(
                    'is_active',
                    'is_staff',
                    'is_superuser'
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login', )})
    )
    readonly_fields = ['last_login']

    # Make sure that this is accepting a tuple.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': {
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser'
            }
        }),
    )

admin.site.register(models.User, UserAdmin)

admin.site.register(models.Recipe)
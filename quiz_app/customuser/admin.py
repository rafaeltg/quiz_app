from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', )
    list_filter = ('sex', )
    exclude = ('password',)
    search_fields = ('first_name', 'last_name', 'email', 'cpf', )

    fieldsets = (
        (_('Personal Information'), {
            'fields': ('first_name', 'last_name', 'cpf', 'birth_date', 'sex', )
        }),
        (_('Contact'), {
             'fields': ('email', 'phone', )
        }),
    )


admin.site.register(User, UserAdmin)


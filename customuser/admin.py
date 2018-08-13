from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', )
    list_filter = ('sex', )
    search_fields = ('first_name', 'last_name', 'email', 'cpf', )


admin.register(User, UserAdmin)

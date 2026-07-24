from django.contrib import admin
from .models import ProgramCategory, Program, ProgramImage, ProgramUpdate

admin.site.register(ProgramCategory)
admin.site.register(Program)
admin.site.register(ProgramImage)
admin.site.register(ProgramUpdate)

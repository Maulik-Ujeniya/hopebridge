from django.contrib import admin
from .models import DriveCategory, Drive, DriveImage, DriveVolunteer, DriveUpdate

admin.site.register(DriveCategory)
admin.site.register(Drive)
admin.site.register(DriveImage)
admin.site.register(DriveVolunteer)
admin.site.register(DriveUpdate)

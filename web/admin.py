from django.contrib import admin

# Register your models here.
from .models import *
# Register your models here.注册
admin.site.register(Line,LineAdmin)
admin.site.register(Timetable,TimetableAdmin)
admin.site.register(Station,StationAdmin)
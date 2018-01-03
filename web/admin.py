from django.contrib import admin

# Register your models here.
admin.site.site_header = '后台管理'
admin.site.site_title = '管理'
from .models import *
# Register your models here.注册
admin.site.register(Line,LineAdmin)
admin.site.register(Timetable,TimetableAdmin)
admin.site.register(Station,StationAdmin)
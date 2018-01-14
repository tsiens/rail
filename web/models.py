from django.db import models
from django.contrib import admin


class Station(models.Model):
    class Meta:
        verbose_name = '车站'
        verbose_name_plural = '车站'

    cn = models.CharField('车站', max_length=20)
    en = models.CharField('代码', max_length=20)
    x = models.FloatField('经度')
    y = models.FloatField('维度')
    province = models.CharField('省', max_length=20)
    city = models.CharField('市', max_length=20)
    county = models.CharField('县', max_length=20)
    date = models.DateField('更新')
    image_date = models.DateField('图片')

    def __str__(self):
        return '%s %s-%s-%s' % (self.cn, self.province, self.city, self.county)


class StationAdmin(admin.ModelAdmin):
    list_display = ('cn', 'en', 'x', 'y', 'province', 'city', 'county', 'date')
    search_fields = ('cn', 'en', 'x', 'y', 'province', 'city', 'county')


class Line(models.Model):
    class Meta:
        verbose_name = '车次'
        verbose_name_plural = '车次'

    line = models.CharField('车次', max_length=20)
    code = models.CharField('代码', max_length=20)
    start = models.CharField('始发', max_length=20)
    start_en = models.CharField('始发代码', max_length=20)
    arrive = models.CharField('终到', max_length=20)
    arrive_en = models.CharField('终到代码', max_length=20)
    runtime = models.IntegerField('运行时长')
    date = models.DateField('更新')

    def __str__(self):
        return '%s %s-%s' % (self.line, self.start, self.arrive)


class LineAdmin(admin.ModelAdmin):
    list_display = ('line', 'code', 'start', 'arrive', 'runtime', 'date')
    search_fields = ('line', 'start', 'arrive')


class Timetable(models.Model):
    class Meta:
        verbose_name = '时刻表'
        verbose_name_plural = '时刻表'

    line = models.CharField('车次', max_length=20)
    code = models.CharField('代码', max_length=20)
    order = models.IntegerField('站序')
    station = models.CharField('车站', max_length=20)
    arrivedate = models.IntegerField('到日')
    arrivetime = models.TimeField('到时')
    leavedate = models.IntegerField('达日')
    leavetime = models.TimeField('达时')
    staytime = models.IntegerField('停时')

    def __str__(self):
        return '%s %s %s' % (self.line, self.order, self.station)


class TimetableAdmin(admin.ModelAdmin):
    list_display = (
        'line', 'code', 'order', 'station', 'arrivedate', 'arrivetime', 'leavedate', 'leavetime', 'staytime')
    search_fields = ('line', 'station')

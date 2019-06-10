#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.utils.safestring import mark_safe
from django.urls import reverse
from stark.service.stark import StarkConfig, get_datetime_text, get_m2m_text, StarkModelForm, Option
from stark.forms.widgets import DateTimePickerInput
from crm import models


class ClassListModelForm(StarkModelForm):
    class Meta:
        model = models.ClassList
        fields = '__all__'
        widgets = {
            'start_date': DateTimePickerInput,
            'graduate_date': DateTimePickerInput,
        }


class ClassListHandler(StarkConfig):

    def display_course(self, row=None, header=None):
        if header:
            return '班级'
        return "%s %s期" % (row.course.name, row.semester,)

    def display_course_record(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '上课记录'
        record_url = reverse('stark:web_courserecord_list', kwargs={'class_id': obj.pk})
        return mark_safe('<a target="_blank" href="%s">上课记录</a>' % record_url)

    list_display = ['school', display_course, 'price', get_datetime_text('开班日期', 'start_date'), 'tutor',
                    get_m2m_text('任课老师', 'teachers'), display_course_record]
    list_filter = [Option('school'), Option('course'),]
    model_form_class = ClassListModelForm

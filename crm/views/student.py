#!/usr/bin/env python
# -*- coding:utf-8 -*-

from django.conf.urls import url
from django.utils.safestring import mark_safe
from django.urls import reverse
from stark.service.stark import StarkConfig,  get_m2m_text, StarkModelForm, Option

from crm import models


class StudentModelForm(StarkModelForm):
    class Meta:
        model = models.Student
        fields = ['qq', 'mobile', 'emergency_contract', 'memo']


class StudentHandler(StarkConfig):
    model_form_class = StudentModelForm

    def display_score(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '积分管理'
        'web_scorerecord_list'
        record_url = reverse('stark:web_scorerecord_list', kwargs={'student_id': obj.pk})
        return mark_safe('<a target="_blank" href="%s">%s</a>' % (record_url, obj.score))

    list_display = ['customer', 'qq', 'mobile', 'emergency_contract', get_m2m_text('已报班级', 'class_list'),
                    display_score,  'student_status']

    def get_add_btn(self, request, *args, **kwargs):
        return None

    def get_list_display(self):
        value = []
        if self.list_display:
            value.extend(self.list_display)
            value.append(type(self).display_edit)
        return value

    def get_urls(self):
        patterns = [
            url(r'^list/$', self.wrapper(self.change_view), name=self.get_list_url_name),
            # url(r'^add/$', self.wrapper(self.add_view), name=self.get_add_url_name),
            url(r'^change/(?P<pk>\d+)/$', self.wrapper(self.change_view), name=self.get_edit_url_name),
            # url(r'^delete/(?P<pk>\d+)/$', self.wrapper(self.delete_view), name=self.get_delete_url_name),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    search_list = ['customer__name', 'qq', 'mobile', ]

    list_filter = [
        Option('class_list', text_func=lambda x: '%s-%s' % (x.school.title, str(x)))
    ]

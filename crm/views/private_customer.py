#!/usr/bin/env python
# -*- coding:utf-8 -*-
from stark.service.stark import StarkConfig, get_m2m_text, StarkModelForm
from crm import models
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.shortcuts import render


class PrivateCustomerModelForm(StarkModelForm):
    class Meta:
        model = models.Customer
        exclude = ['consultant', ]


class PrivateCustomerHandler(StarkConfig):
    model_form_class = PrivateCustomerModelForm

    def display_record(self, row=None, header=None, *args, **kwargs):
        if header:
            return '跟进记录'
        record_url = reverse('stark:crm_consultrecord_changelist', kwargs={'customer_id': row.pk})
        return mark_safe('<a target="_blank" href="%s">跟进记录</a>' % record_url)

    def display_pay_record(self, row=None, header=None, *args, **kwargs):
        if header:
            return '缴费'
        record_url = reverse('stark:web_paymentrecord_list', kwargs={'customer_id': row.pk})
        return mark_safe('<a target="_blank" href="%s">缴费</a>' % record_url)

    list_display = ['name', 'qq', get_m2m_text('咨询课程', 'course'), 'status', display_record, display_pay_record]

    def get_queryset(self, request, *args, **kwargs):
        current_user_id = self.request.session['user_info']['id']
        return self.model_class.objects.filter(consultant_id=current_user_id)

    def record_view(self, request, pk):
        """
        查看跟进记录的视图
        :param request:
        :param pk:
        :return:
        """
        record_list = models.ConsultRecord.objects.filter(customer_id=pk)
        return render(request, 'record_view.html', {'record_list': record_list})

    def save(self, form, request, modify=False, *args, **kwargs):
        if not modify:
            current_user_id = request.session['user_info']['id']
            form.instance.consultant_id = current_user_id
        form.save()

    def multi_remove(self, request):
        '''
        批量移除私有客户
        :param request:
        :return:
        '''
        current_user_id = 1  # 以后要改成取session中获取当前登录用户的ID
        id_list = request.POST.getlist('pk')
        models.Customer.objects.filter(id__in=id_list, status=2, consultant_id=current_user_id).update(consultant=None)



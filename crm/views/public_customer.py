#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.shortcuts import HttpResponse, render
from django.db import transaction
from django.conf import settings
from stark.service.stark import StarkConfig, get_m2m_text, StarkModelForm
from crm import models


class PublicCustomerModelForm(StarkModelForm):
    class Meta:
        model = models.Customer
        exclude = ['consultant', ]


class PublicCustomerHandler(StarkConfig):

    def display_record(self, row=None, header=None):
        if header:
            return '跟进记录'
        record_url = self.reverse_commons_url(self.get_url_name('record_view'), pk=row.pk)
        return mark_safe('<a href="%s">查看跟进</a>' % record_url)

    list_display = ['name', 'qq', get_m2m_text('咨询课程', 'course'), display_record, 'status']

    model_form_class = PublicCustomerModelForm

    def get_queryset(self, request, *args, **kwargs):
        return self.model_class.objects.filter(consultant__isnull=True)

    def extra_urls(self):
        patterns = [
            url(r'^record/(?P<pk>\d+)/$', self.wrapper(self.record_view),
                name=self.get_url_name('record_view')),
        ]
        return patterns

    def record_view(self, request, pk):
        """
        查看跟进记录的视图
        :param request:
        :param pk:
        :return:
        """
        record_list = models.ConsultRecord.objects.filter(customer_id=pk)
        return render(request, 'record_view.html', {'record_list': record_list})

    def multi_apply(self, request):
        '''
        批量申请共有客户
        :param request:
        :return:
        '''
        current_user_id = 1  # 以后要改成取session中获取当前登录用户的ID
        id_list = request.POST.getlist('pk')
        '''
        开启事务，避免并发时产生的问题
        pymsql: select * from crm_custmoer where id in [11,22,33,44] for update;
        结束事务
        '''
        # 获取自己为成单的客户数量
        my_customer_count = models.Customer.objects.filter(consultant_id=current_user_id, status=2).count()
        if my_customer_count + len(id_list) > settings.PRIVATE_CUSTOMER:
            return HttpResponse('超过客户最大限制！')

        # 使用django orm加锁
        flag = False
        with transaction.atomic():
            origin = models.Customer.objects.filter(id__in=id_list, consultant__isnull=True, status=2).select_for_update()
            # 申请的数量要与公户查询到的数量相等
            if origin.count() == len(id_list):
                # 可以申请
                models.Customer.objects.filter(id__in=id_list).update(consultant_id=current_user_id)
                flag = True

            if not flag:
                return HttpResponse('已被其他顾问申请')

    multi_apply.text = "申请到我的私户"
    action_list = [multi_apply]

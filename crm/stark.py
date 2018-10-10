# Author: harry.cai
# DATE: 2018/9/16
from stark.service.stark import site, StarkConfig, Option
from .models import *
from django import forms
from django.shortcuts import HttpResponse, render, redirect
from django.conf import settings
from django.utils.safestring import mark_safe
from django.urls import reverse, re_path
from django.forms import modelformset_factory

class UserInfoConfig(StarkConfig):
    search_list = ['name']
    list_display = ['name']
    action_list = [StarkConfig.multi_delete]
    list_filter = [
        Option('name', condition={'id__gt': 1}, text_func=lambda x: x.name, value_func=lambda x: x.name),
        Option('depart', text_func=lambda x: x.title, is_multi=True)
    ]


class CustomerInfoConfig(StarkConfig):
    search_list = ['name']

    def display_follow(self, row=None, header=False):
        if header:
            return "跟进记录"
        url = reversed("stark:crm_consultrecord_changelist")
        return mark_safe("<a href='%s?cid=%s'>跟进记录</a>" %(url, row.pk))


    list_display = ['name', 'gender', 'qq', 'status', 'education', display_follow]
    list_filter = [
        Option('name', condition={'id__gt': 1}, text_func=lambda x: x.name, value_func=lambda x: x.name),
        Option('education', is_choice=True, text_func=lambda x: x[1]),
        Option('gender', is_choice=True, text_func=lambda x: x[1]),
    ]

    order_by = ['-id']


class PubModelForm(forms.ModelForm):
    '''
    自定制公共客户的modelform
    '''
    class Meta:
        model = Customer
        exclude = ['consultant', 'status']


class PubCustomerInfoConfig(StarkConfig):
    '''
    公共客户配置类
    '''
    search_list = ['name']
    list_display = ['name', 'gender', 'qq', 'status', 'education']
    list_filter = [
        Option('name', condition={'id__gt': 1}, text_func=lambda x: x.name, value_func=lambda x: x.name),
        Option('education', is_choice=True, text_func=lambda x: x[1]),
        Option('gender', is_choice=True, text_func=lambda x: x[1]),
    ]
    model_form_class = PubModelForm
    order_by = ['-id']

    def get_queryset(self):
        return self.model_class.objects.filter(consultant__isnull=True)

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
        my_customer_count = Customer.objects.filter(consultant_id=current_user_id, status=2).count()
        if my_customer_count + len(id_list) > settings.PRIVATE_CUSTOMER:
            return HttpResponse('超过客户最大限制！')

        # 使用django orm加锁
        from django.db import transaction
        flag = False
        with transaction.atomic():
            origin = Customer.objects.filter(id__in=id_list, consultant__isnull=True).select_for_update()
            if origin.count() == len(id_list):
                # 可以申请
                Customer.objects.filter(id__in=id_list).update(consultant_id=current_user_id)
                flag = True

            if not flag:
                return HttpResponse('已被其他顾问申请')

    multi_apply.text = '申请客户'
    action_list = [multi_apply]


class PrivateModelForm(forms.ModelForm):
    '''
    自定制私有客户的modelform
    '''
    class Meta:
        model = Customer
        exclude = ['consultant', 'status']


class PrivateCustomerInfoConfig(StarkConfig):
    '''
    私有客户配置类
    '''
    search_list = ['name']

    list_filter = [
        Option('name', condition={'id__gt': 1}, text_func=lambda x: x.name, value_func=lambda x: x.name),
        Option('education', is_choice=True, text_func=lambda x: x[1]),
        Option('gender', is_choice=True, text_func=lambda x: x[1]),
    ]
    model_form_class = PrivateModelForm
    order_by = ['-id']

    def get_queryset(self):
        current_user_id = 1 # 以后要改成取session中获取当前登录用户的ID
        return self.model_class.objects.filter(consultant_id=current_user_id)

    def save(self, form, modify=False):
        current_user_id = 1
        form.instance.consultant = UserInfo.objects.get(id=current_user_id)
        return form.save()

    def get_list_display(self):
        val = super().get_list_display()
        val.remove(StarkConfig.display_del)
        return val

    def multi_remove(self, request):
        '''
        批量移除私有客户
        :param request:
        :return:
        '''
        current_user_id = 1  # 以后要改成取session中获取当前登录用户的ID
        id_list = request.POST.getlist('pk')
        Customer.objects.filter(id__in=id_list, status=2, consultant_id=current_user_id).update(consultant=None)

    def display_follow(self, row=None, header=False):
        if header:
            return "跟进记录"
        url = reversed("stark:crm_consultrecord_pri_changelist")
        return mark_safe("<a href='%s?cid=%s'>跟进记录</a>" %(url, row.pk))

    multi_remove.text = '移除客户'
    action_list = [multi_remove]
    list_display = ['name', 'gender', 'qq', 'status', 'education', display_follow]


class ClassListConfig(StarkConfig):
    list_display = ['course', 'school', 'semester', 'start_date']


class CourseConfig(StarkConfig):
    list_display = ['name']


class ConsultRecordConfig(StarkConfig):
    '''
    销售跟进记录
    '''
    list_display = ['customer', 'note', 'consult']

    def get_queryset(self):
        cid = self.request.GET.get('cid')
        if cid:
            return ConsultRecord.objects.filter(customer_id=cid)
        return ConsultRecord.objects


class PriConsultRecordConfig(StarkConfig):
    '''
    销售跟进记录
    '''
    list_display = ['customer', 'note', 'consult']

    def get_queryset(self):
        cid = self.request.GET.get('cid')
        current_user_id = 1  # 以后要改成取session中获取当前登录用户的ID
        if cid:
            return ConsultRecord.objects.filter(customer_id=cid, customer__consultant_id=current_user_id)
        return ConsultRecord.objects.filter(consultant_id=current_user_id)


class StudentConfig(StarkConfig):
    list_display = ['username', 'customer']


class CourseRecordConfig(StarkConfig):
    '''
    上课记录
    '''
    def display_title(self, row=None, header=False):
        if header:
            return "上课记录"
        tpl = "%s s%sday%s" %(row.class_obj.course.name, row.class_obj.semester, row.day_num, )
        return tpl

    def multi_init(self, request):
        '''
        批量初始化
        找到选中上课记录的班级
        找到班级下所有人
        为每个人生成一条学习记录
        :param request:
        :return:
        '''

        id_list = request.POST.getlist('pk')
        for nid in id_list:
            record_obj = CourseRecord.objects.get(id=nid)
            stu_list = Student.objects.filter(class_list=record_obj.class_obj)
            exists = StudyRecord.objects.filter(course_record=record_obj).exists()
            if exists:
                continue
            study_record_list = []
            for stu in stu_list:
                study_record_list.append(StudyRecord(course_record=record_obj, student=stu))
            StudyRecord.objects.bulk_create(study_record_list, batch_size=30)

    def display_study_record(self, row=None, header=False):
        if header:
            return "学习记录"
        url = reverse('stark:crm_studyrecord_changelist')
        return mark_safe("<a href='%s?ccid=%s'>学习记录</a>" % (url, row.pk))
    list_display = [display_title]


class StudyRecordModelForm(forms.ModelForm):
    class Meta:
        model = StudyRecord
        fields = ['student', 'record', 'score', 'homework_note']


class StudyRecordConfig(StarkConfig):

    def get_urls(self):
        urlpatterns = [
            re_path(r'^list/$', self.wrapper(self.list_view), name=self.get_list_url_name),
        ]

        return urlpatterns

    def list_view(self, request):
        ccid = request.GET.get('ccid')
        model_formset_cls = modelformset_factory(StudyRecord, StudyRecordModelForm, extra=0)
        queryset = StudyRecord.objects.filter(course_record_id=ccid)
        if request.method == "GET":
            formset = model_formset_cls(queryset=queryset)
            return render(request, 'study_record.html', {'formset': formset})
        formset = model_formset_cls( data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('/stark/crm/studyrecord/list/?ccid=%s' %ccid)
        return render(request, 'study_record.html', {'formset': formset})

site.register(School)
site.register(Course, CourseConfig)
site.register(ClassList, ClassListConfig)
site.register(UserInfo, UserInfoConfig)
site.register(Department)
site.register(Customer, CustomerInfoConfig)
site.register(Customer, PubCustomerInfoConfig, prev='pub')
site.register(Customer, PrivateCustomerInfoConfig, prev='private')
site.register(ConsultRecord, ConsultRecordConfig)
site.register(ConsultRecord, PriConsultRecordConfig, prev='pri')
site.register(Student, StarkConfig)
site.register(StudyRecord, StudyRecordConfig)
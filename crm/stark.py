# Author: harry.cai
# DATE: 2018/9/16
from stark.service.stark import site, StarkConfig, Option
from crm.views.school import SchoolHandler
from crm.views.depart import DepartmentHandler
from crm.views.userinfo import UserInfoHandler
from crm.views.course import CourseHandler
from crm.views.consult_record import ConsultRecordHandler
from crm.views.class_list import ClassListHandler
from crm.views.private_customer import *
from crm.views.public_customer import *

site.register(models.School, SchoolHandler)
site.register(models.Department, DepartmentHandler)
site.register(models.UserInfo, UserInfoHandler)
site.register(models.Course, CourseHandler)
site.register(models.ClassList, ClassListHandler)
site.register(models.Customer, PublicCustomerHandler, prev='pub')
site.register(models.Customer, PrivateCustomerHandler, prev='priv')
site.register(models.ConsultRecord, ConsultRecordHandler)

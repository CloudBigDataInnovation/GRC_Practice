# -*- coding: utf-8 -*-
from django.conf.urls import url
from planning.views import PlanningView, PlanningAuditMonthView, PlanningDayView


urlpatterns = [
    url(r'^$', PlanningView.as_view(), name="planning_list"),
    url(r'^day/$', PlanningDayView.as_view(), name="planning_day"),
    url(r'^audits/$', PlanningAuditMonthView.as_view(), name="planning_audits"),
]

# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views import generic
import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.urls import reverse
from django.db.models import Count
from django.contrib.auth.models import User
from dateutil.relativedelta import relativedelta
from audits.models import Audit #, AuditExecute


class PlanningView(generic.View):

    def get(self, request):
        start_day = datetime.datetime.today().date().replace(day=1)
        end_day = datetime.datetime.today().date() +\
         relativedelta(day=1, months=+1)
        events = Audit.objects.filter(start_date__lte=end_day,
             end_date__gte=start_day).extra(select={'start': 'start_date',
             'end': 'end_date', 'url': 'id', 'status': 'status'}).values('title', 'start', 'end', 'url', 'status')
        for event in events:
            if (event["status"] == "DR"):
                #DRAFT status
                event["backgroundColor"] = "#AAAAAA" 
            elif (event["status"] == "AC"):
                #ACTIVE status
                event["backgroundColor"] = "#00BB00" 
            elif (event["status"] == "AC"):
                #CLOSED status
                event["backgroundColor"] = "#0000BB" 

        return render(request, "planning/list.html",
             {'events': events})


class PlanningAuditMonthView(generic.View):
    @csrf_exempt
    def get(self, request):
        day = request.GET["day"]
        start_day = datetime.datetime.strptime(day, "%d-%m-%Y").date()
        end_day = start_day + relativedelta(day=1, months=+1)

        events = list(Audit.objects.filter(start_date__lte=end_day,
             end_date__gte=start_day).extra(select={'start': 'start_date',
             'end': 'end_date', 'audit_id': 'id', 'status': 'status'}).values('title', 'start', 'end', 'id', 'status'))
        for event in events:
            if (event["status"] == "DR"):
                #DRAFT status
                event["backgroundColor"] = "#AAAAAA" 
            elif (event["status"] == "AC"):
                #ACTIVE status
                event["backgroundColor"] = "#00BB00" 
            elif (event["status"] == "AC"):
                #CLOSED status
                event["backgroundColor"] = "#0000BB" 
        
            event["start"] = event["start"].strftime('%Y-%m-%d')
            event["end"] = event["end"].strftime('%Y-%m-%d 23:59:59')
            event["url"] = reverse('audits:audit', kwargs={'audit_id':event["id"]} )
 
        return JsonResponse({'events': events})


class PlanningDayView(generic.View):
    @csrf_exempt
    def get(self, request):
        data = {}
        day = request.GET["day"]
        selected_day = datetime.datetime.strptime(day, "%d-%m-%Y").date()
        audits_list = Audit.objects.filter(start_date__lte=selected_day,
             end_date__gte=selected_day).values_list('id', flat=True)
        print("ok reached")
        execute = AuditExecute.objects.filter(audit_id__in=audits_list)\
        .values('assigned_to__username').annotate(Count('assigned_to'))
        users = []
        for user in execute:
            u = User.objects.get(username=user['assigned_to__username'])
            users.append({'name': u.get_full_name(),
                 'username': user['assigned_to__username'],
                 'count': user['assigned_to__count']})
        data['html'] = render_to_string('planning/users.html',
             {'users': users, 'audits_list': audits_list})
        return JsonResponse(data)

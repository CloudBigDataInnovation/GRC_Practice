import os
from datetime import date

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Count
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.template import RequestContext
from django.views import generic
from .models import Process, Objective, Risk, Control, Test,\
        Finding, Audit, Attachment
from .forms import AuditForm, AddFromRepoForm, ProcessForm, ObjectiveForm,\
     RiskForm, ControlForm, TestForm, AjaxTestResultForm, AjaxFindingForm,\
      AjaxProcessForm, AjaxObjectiveForm, AjaxRiskForm, AjaxControlForm,\
       AjaxTestForm


class IndexView(generic.ListView):
    template_name = 'audits/index.html'
    context_object_name = 'all_audits'

    def get_queryset(self):
        return Audit.objects.order_by('-start_date')[:10]

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        year = date.today().year - 2
        y = []
        x = []
        for i in range(3):
            a = Audit.objects.filter(fy=int(year) + i, status='AC').count()
            d = Audit.objects.filter(fy=int(year) + i, status='DR').count()
            c = Audit.objects.filter(fy=int(year) + i, status='CL').count()
            y.append([a, d, c])
            x.append(int(year) + i)
        context['x'] = x
        context['y'] = y
        return context


class LoginView(generic.TemplateView):
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        if 'next' in list(self.request.GET.keys()):
            context['next'] = self.request.GET['next']
        return context


def index(request):
    all_audits = Audit.objects.order_by('-start_date')[:10]
    context = {'all_audits': all_audits}
    year = date.today().year - 2
    y = []
    x = []
    for i in range(3):
        a = Audit.objects.filter(fy=int(year) + i, status='AC').count()
        b = Audit.objects.filter(fy=int(year) + i, status='DR').count()
        c = Audit.objects.filter(fy=int(year) + i, status='CL').count()
        y.append([a, b, c])
        x.append(int(year) + i)
    context['x'] = x
    context['y'] = y
    return render(request, 'audits/index.html', context)


def not_implemented(request):
    return render(request, 'not_implemented.html')


class AuditChildView(generic.ListView):
    template_name = 'audits/audit_childs.html'
    #paginate_by = 5

    def get_queryset(self):
        queryset = Process.objects.filter(audit_id=self.kwargs['audit_id'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AuditChildView, self).get_context_data(**kwargs)
        context['type'] = 'process'
        context['audit_id'] = self.kwargs['audit_id']
        context['audit'] = Audit.objects.get(id=int(self.kwargs['audit_id']))
        context['management'] = True
        return context


def audit(request, audit_id):
    aud = get_object_or_404(Audit, pk=audit_id)
    if request.method == "POST":
        form = AuditForm(request.POST, request.FILES, instance=aud)

        if form.is_valid():
            audit = form.save(commit=False)
            audit.changed_by = request.user
            audit.changed_on = timezone.now()
            audit = form.save()
            messages.success(request, 'Audit information was saved')
            papers = request.FILES.getlist('papers')
            try:
                if papers:
                    Attachment.objects.bulk_create(
                        [Attachment(content_object=audit,
                             workpaper=attachment, filename=attachment.name)
                              for attachment in papers])
                
                messages.success(request, 'Attachment saved')
            except:
                messages.error(request, 'Attachment NOT saved') 
                pass

            if request.POST.get('add_from_repo') == "":
                messages.info(request, 'add from repo')
                return render(request, 'audits/not_implemented.html')

            elif request.POST.get('copy_from_audit') == "":
                messages.info(request, 'copy from audit')
                return render(request, 'audits/not_implemented.html')

            elif request.POST.get('add_manually') == "":
                messages.info(request, 'You may now add processes')
                #messages.debug(request, "add manually debug")
                return HttpResponseRedirect(reverse('audits:audit_management',
                 args=[audit.id]))

            elif request.POST.get('delete') == "":
                aud.delete()
                messages.success(request, 'Audit deleted')
                #messages.debug(request, "add manually debug")
                return HttpResponseRedirect(reverse('audits:index'))

            else:
                return HttpResponseRedirect(reverse('audits:audit', args=(audit.id,)))
                #return render(request, "audits/audit.html", {'form': form})

        else:
            messages.error(request, 'Your audit was NOT saved')
            return render(request, "audits/audit.html", {'form': form})
    else:
        form = AuditForm(instance=aud)
        return render(request, "audits/audit.html", {'form': form})


def audit_create(request):
    if request.method == "POST":
        form = AuditForm(request.POST)
        if form.is_valid():
            audit = form.save(commit=False)
            audit.changed_by = request.user
            audit.changed_on = timezone.now()
            audit = form.save()
            messages.success(request, 'Audit was saved')
            papers = request.FILES.getlist('papers')
            try:
                if papers:
                    Attachment.objects.bulk_create(
                        [Attachment(content_object=audit,
                             workpaper=attachment, filename=attachment.name)
                              for attachment in papers])
            except:
                pass

            if request.POST.get('add_from_repo') == "":
                messages.success(request, "add from Repo")
                #return render(request, "audits/add_from_repo.html",
                     #{'form': form})
                return HttpResponseRedirect("audits/not_implemented")

            elif request.POST.get('add_manually') == "":
                messages.success(request, "add manually")
                return HttpResponseRedirect(reverse('audits:audit_management',
                 args=[audit.id]))

            else:
                messages.success(request, "Audit was created")
                return HttpResponseRedirect(reverse('audits:audit',
                 args=(audit.id,)))

        else:
            messages.error(request, 'Your audit was NOT saved')
            return render(request, "audits/audit.html", {'form': form})

    else:
        form = AuditForm()
        return render(request, "audits/audit.html", {'form': form})


def person_view(request, audit_id=None):

    if  audit_id == None:
        audit = Audit()
    else:
        audit = Audit.objects.get(id = audit_id)

    ProcessFormSet = inlineformset_factory(Audit, Process, fields=('title',), can_delete=True)

    if request.method == "POST":
        auditform = AuditForm(request.POST, instance=audit)
        processformset = ProcessFormSet(request.POST, request.FILES, instance=audit)

        if auditform.is_valid() and processformset.is_valid():
            auditform.save()
            processformset.save()

            # Redirect to somewhere
            if '_save' in request.POST:
                return HttpResponseRedirect('/audits/audit/process/create')
            if '_addanother' in request.POST:
                return HttpResponseRedirect('/audits/audit/process/create')

    else:
        auditform = AuditForm(instance=audit)
        processformset = ProcessFormSet(instance=audit)

    return render('process2.html', {
        'auditform'    : auditform,
        'processformset'  : processformset,
    })

@permission_required('audits.add_process','audits.change_process')
def process(request, process_id=None):
    if process_id != None:
        pro = get_object_or_404(Process, pk=process_id)
        if request.method == "POST":
            form = ProcessForm(request.POST, instance=pro)
            if form.is_valid():
                process = form.save(commit=False)
                process.changed_by = request.user
                process.changed_on = timezone.now()
                process = form.save()
                messages.success(request, 'Your process was saved')
                return HttpResponseRedirect(reverse('audits:audit_process', args=(process.id,)))
            else:
                messages.error(request, 'Your process was NOT saved')
                return render(request, "audits/process.html", {'form': form})
        else:
            form = ProcessForm(instance=pro)
            return render(request, "audits/process.html", {'form': form})
    else:
        if request.method == "POST":
            form = ProcessForm(request.POST)
            if form.is_valid():
                process = form.save(commit=False)
                process.changed_by = request.user
                process.changed_on = timezone.now()
                process = form.save()
                messages.success(request, 'Your process was saved')
                return HttpResponseRedirect(reverse('audits:audit_process', args=(process.id,)))
            else:
                return render(request, "audits/process.html", {'form': form})

        else:
            form = ProcessForm()
            return render(request, "audits/process.html", {'form': form})


@permission_required('audits.add_objecive','audits.change_objective')
def objective(request, objective_id=None):
    if objective_id != None:
        obj = get_object_or_404(Objective, pk=objective_id)
        if request.method == "POST":
            form = ObjectiveForm(request.POST, instance=obj)
            if form.is_valid():
                objective = form.save(commit=False)
                objective.changed_by = request.user
                objective.changed_on = timezone.now()
                objective = form.save()
                messages.success(request, 'Your objective was saved')
                return HttpResponseRedirect(reverse('audits:audit_objective', args=(objective.id,)))
            else:
                return render(request, "audits/objective.html", {'form': form})
        else:
            form = ObjectiveForm(instance=obj)
            return render(request, "audits/objective.html", {'form': form})

    else:
        if request.method == "POST":
            form = ObjectiveForm(request.POST)
            if form.is_valid():
                objective = form.save(commit=False)
                objective.changed_by = request.user
                objective.changed_on = timezone.now()
                objective = form.save()
                messages.success(request, 'Your objective was saved')
                return HttpResponseRedirect(reverse('audits:audit_objective', args=(objective.id,)))
            else:
                messages.error(request, 'Your objective was not saved')
                return render(request, "audits/objective.html", {'form': form})
        else:
            form = ObjectiveForm()
            return render(request, "audits/objective.html", {'form': form})


@permission_required('audits.change_risk')
def risk(request, risk_id):
    ri = get_object_or_404(Risk, pk=risk_id)
    if request.method == "POST":
        form = RiskForm(request.POST, instance=ri)
        if form.is_valid():
            risk = form.save()
            messages.success(request, 'Your risk was saved')
            return HttpResponseRedirect(reverse('audits:risk', args=(risk.id,)))
        else:
            return render(request, "repository/risk.html", {'form': form})
    else:
        form = RiskForm(instance=ri)
        return render(request, "repository/risk.html", {'form': form})


@permission_required('repository.add_risk')
def risk_create(request):
    if request.method == "POST":
        form = RiskForm(request.POST)
        if form.is_valid():
            risk = form.save()
            messages.success(request, 'Your risk was saved')
            return HttpResponseRedirect(reverse('audits:risk', args=(risk.id,)))
        else:
            return render(request, "repository/risk.html", {'form': form})

    else:
        form = RiskForm()
        return render(request, "repository/risk.html", {'form': form})


@permission_required('repository.change_control')
def control(request, control_id):
    con = get_object_or_404(Objective, pk=control_id)
    if request.method == "POST":
        form = ControlForm(request.POST, instance=con)
        if form.is_valid():
            control = form.save()
            messages.success(request, 'Your control was saved')
            return HttpResponseRedirect(reverse('audits:control', args=(control.id,)))
        else:
            return render(request, "repository/control.html", {'form': form})
    else:
        form = ControlForm(instance=con)
        return render(request, "repository/control.html", {'form': form})


@permission_required('repository.add_control')
def control_create(request, audit_id):
    if request.method == "POST":
        form = ControlForm(request.POST)
        if form.is_valid():
            control = form.save()
            messages.success(request, 'Your control was saved')
            return HttpResponseRedirect(reverse('audits:control', args=(control.id,)))
        else:
            return render(request, "repository/control.html", {'form': form})

    else:
        form = ControlForm()
        controls = Control.objects.filter(risk__objective__process__audit=audit_id)
        return render(request, "audits/control.html", {'form': form,
                                                           'controls': controls})


@permission_required('repository.change_test')
def test(request, test_id):
    te = get_object_or_404(Test, pk=test_id)
    if request.method == "POST":
        form = TestForm(request.POST, instance=te)
        if form.is_valid():
            test = form.save()
            messages.success(request, 'Your test was saved')
            return HttpResponseRedirect(reverse('audits:test', args=(test.id,)))
        else:
            return render(request, "repository/test.html", {'form': form})
    else:
        form = TestForm(instance=te)
        return render(request, "repository/test.html", {'form': form})


@permission_required('repository.add_test')
def test_create(request):
    if request.method == "POST":
        form = TestForm(request.POST)
        if form.is_valid():
            test = form.save()
            messages.success(request, 'Your test was saved')
            return HttpResponseRedirect(reverse('audits:test', args=(test.id,)))
        else:
            return render(request, "repository/test.html", {'form': form})

    else:
        form = TestForm()
        return render(request, "repository/test.html", {'form': form})


def audit_execute(request, audit_id):
    # audit execute code to be replaced
    aud = get_object_or_404(Audit, pk=audit_id)
    if request.method == "POST":
        form = AuditForm(request.POST, instance=aud)

        if form.is_valid():
            audit = form.save(commit=False)
            audit.changed_by = request.user
            audit.changed_on = timezone.now()
            audit = form.save()
            messages.success(request, 'Audit information was saved')

            if request.POST.get('add_from_repo') == "":
                messages.info(request, 'add from repo')
                return HttpResponseRedirect(reverse('audits:not_implemented',))

            elif request.POST.get('add_manually') == "":
                messages.info(request, 'You may now add processes')
                #messages.debug(request, "add manually debug")
                return HttpResponseRedirect(reverse('audits:process_create'))

            else:
                return HttpResponseRedirect(reverse('audits:audit', args=(audit.id,)))

        else:
            messages.error(request, 'Your audit was NOT saved')
            return render(request, "audits/audit.html", {'form': form})
    else:
        form = AuditForm(instance=aud)
        return render(request, "audits/audit.html", {'form': form})


class AuditExecuteView(generic.ListView):
    template_name = 'audits/execute.html'
    #paginate_by = 5

    def get_queryset(self):
        if self.kwargs['view_type'] == 'process':
            return Process.objects.filter(audit_id=self.kwargs['audit_id'])\
            .order_by('-changed_on').distinct()
        elif self.kwargs['view_type'] == 'objective':
            return Objective.objects.filter(audit_id=self.kwargs['audit_id'])\
                    .order_by('-changed_on').distinct()
        elif self.kwargs['view_type'] == 'risk':
            return Risk.objects.filter(audit_id=self.kwargs['audit_id'])\
                    .order_by('-changed_on').distinct()
        elif self.kwargs['view_type'] == 'control':
            return Control.objects.filter(audit_id=self.kwargs['audit_id'])\
                    .order_by('-changed_on').distinct()
        elif self.kwargs['view_type'] == 'test':
            return Test.objects.filter(audit_id=self.kwargs['audit_id'])\
                    .order_by('-changed_on').distinct()
        return []

    def get_context_data(self, **kwargs):
        context = super(AuditExecuteView, self).get_context_data(**kwargs)
        context['type'] = self.kwargs['view_type']
        context['audit_id'] = self.kwargs['audit_id']
        context['process_id'] = 0
        context['objective_id'] = 0
        context['risk_id'] = 0
        context['control_id'] = 0
        context['test_id'] = 0
        context['audit'] = Audit.objects.get(id=int(self.kwargs['audit_id']))
        return context


@csrf_exempt
def process_objective(request, process_id):
    data = {}
    management = request.GET.get('management', False)
    objectives = Process.objects.get(id=process_id).obj_process.all()\
            .order_by('-changed_on')
    data['html'] = render_to_string('audits/process_objective.html',
         {'objectives': objectives, 'process_id': process_id,
              'management': management})
    return JsonResponse(data)


@csrf_exempt
def objective_risk(request, objective_id):
    data = {}
    management = request.GET.get('management', False)
    process_id = request.GET.get('process')
    risks = Objective.objects.get(id=objective_id).risk_obj.all()\
        .order_by('-changed_on')
    data['html'] = render_to_string('audits/objective_risks.html',
         {'risks': risks, 'objective_id': objective_id,
              'process_id': process_id, 'management': management})
    return JsonResponse(data)


@csrf_exempt
def risk_controller(request, risk_id):
    data = {}
    management = request.GET.get('management', False)
    process_id = request.GET.get('process')
    objective_id = request.GET.get('objective')
    controllers = Risk.objects.get(id=risk_id).control_risk.all()\
        .order_by('-changed_on')
    data['html'] = render_to_string('audits/risk_controllers.html',
         {'controllers': controllers, 'risk_id': risk_id,
              'process_id': process_id, 'objective_id': objective_id,
               'management': management})
    return JsonResponse(data)


@csrf_exempt
def controller_test(request, control_id):
    data = {}
    process_id = request.GET.get('process')
    objective_id = request.GET.get('objective')
    risk_id = request.GET.get('risk')
    tests = Control.objects.get(id=control_id).test_control.all()\
        .order_by('-changed_on')
    if 'management' in list(request.GET.keys()):
        data['html'] = render_to_string('audits/controller_tests_list.html',
             {'tests': tests})
    else:
        data['html'] = render_to_string('audits/controller_tests.html',
             {'tests': tests, 'control_id': control_id, 'risk_id': risk_id,
                  'process_id': process_id, 'objective_id': objective_id})
    return JsonResponse(data)


@csrf_exempt
def test_findings(request, test_id):
    data = {}
    process_id = request.GET.get('process')
    objective_id = request.GET.get('objective')
    risk_id = request.GET.get('risk')
    control_id = request.GET.get('control')
    find = Finding.objects.filter(test_id=test_id).values('id', 'title', 'desc')
    data['html'] = render_to_string('audits/test_findings.html',
         {'findings': find, 'test_id': test_id, 'control_id': control_id,
              'risk_id': risk_id, 'process_id': process_id,
               'objective_id': objective_id})
    return JsonResponse(data)


class AjaxTestResultView(generic.View):
    @csrf_exempt
    def get(self, request, test_id):
        data = {}
        test = Test.objects.get(id=test_id)
        form = AjaxTestResultForm(instance=test)
        csrf_token_value = request.COOKIES['csrftoken']
        data['html'] = render_to_string('audits/right_panel_test_result.html',
         {'form': form, 'test_id': test_id,
              'csrf_token_value': csrf_token_value})
        return JsonResponse(data)

    @csrf_exempt
    def post(self, request, test_id):
        data = {'status': 'failed'}
        test = Test.objects.get(id=test_id)
        form = AjaxTestResultForm(request.POST, instance=test)
        if form.is_valid():
            test = form.save()
            test.changed_by = request.user
            data['status'] = 'success'
        else:
            data['error'] = form.errors
        return JsonResponse(data)


class AjaxFindingView(generic.View):
    @csrf_exempt
    def get(self, request):
        data = {}
        test_id = request.GET.get('test_id')
        form = AjaxFindingForm()
        data = {'form': form, 'test_id': test_id}
        return render(request, 'audits/finding_form_ajax.html', data)

    @csrf_exempt
    def post(self, request):
        data = {'status': 'failed'}
        data['test'] = test_id = request.GET.get('test_id')
        test = Test.objects.get(id=test_id)
        form = AjaxFindingForm(request.POST)
        papers = request.FILES.getlist('papers')
        if form.is_valid():
            obj = form.save(commit=False)
            obj.changed_by = request.user
            obj.test = test
            obj.save()
            try:
                if papers:
                    Attachment.objects.bulk_create(
                        [Attachment(content_object=obj,
                             workpaper=attachment, filename=attachment.name)
                              for attachment in papers])
            except:
                pass
            data['html'] = render_to_string('audits/ajax_bind_findings.html',
                {'obj': obj, 'process_id': 0, 'objective_id': 0, 'risk_id': 0,
                     'control_id': 0, 'test_id': test_id})
            data['status'] = 'success'
        else:
            data['error'] = form.errors
        return JsonResponse(data)


class AjaxAttachmentDeleteView(generic.View):
    @csrf_exempt
    def get(self, request, attachment_id):
        data = {}
        Attachment.objects.get(id=attachment_id).delete()
        data['status'] = 'success'
        return JsonResponse(data)


class AjaxProcessAddEditView(generic.View):
    @csrf_exempt
    def get(self, request, audit_id, process_id=None):
        data = {}
        if process_id:
            obj = Process.objects.get(id=process_id)
            form = AjaxProcessForm(instance=obj)
        else:
            form = AjaxProcessForm()
        csrf_token_value = request.COOKIES['csrftoken']
        data['html'] = render_to_string('audits/right_panel_process.html',
         {'form': form, 'audit_id': audit_id, 'process_id': process_id,
              'csrf_token_value': csrf_token_value})
        return JsonResponse(data)

    @csrf_exempt
    def post(self, request, audit_id, process_id=None):
        data = {'status': 'failed'}
        audit = Audit.objects.get(id=audit_id)
        papers = request.FILES.getlist('papers')
        if process_id:
            obj = Process.objects.get(id=process_id)
            form = AjaxProcessForm(request.POST, instance=obj)
        else:
            form = AjaxProcessForm(request.POST)
        if form.is_valid():
            process = form.save(commit=False)
            if not process_id:
                process.audit = audit
                process.changed_by = request.user
            process.save()
            try:
                if papers:
                    Attachment.objects.bulk_create(
                        [Attachment(content_object=process,
                             workpaper=attachment, filename=attachment.name)
                              for attachment in papers])
            except:
                pass
            data['status'] = 'success'
            data['process_title'] = process.title
            data['process_ref_id'] = process.ref_id
            data['process_desc'] = process.desc
            data['html'] = render_to_string('audits/ajax_binding_process.html',
                                 {'audit_id': audit_id, 'process': process})
        else:
            data['error'] = form.errors
        return JsonResponse(data)


class AjaxProcessDeleteView(generic.View):
    @csrf_exempt
    def get(self, request, process_id):
        data = {}
        Process.objects.get(id=process_id).delete()
        data['status'] = 'success'
        return JsonResponse(data)


class AjaxObjectiveAddEditView(generic.View):
    @csrf_exempt
    def get(self, request, audit_id, objective_id=None):
        audit = get_object_or_404(Audit, id=audit_id)
        data = {}
        if objective_id:
            obj = get_object_or_404(Objective, id=objective_id)
            form = AjaxObjectiveForm(instance=obj, audit=audit)
        else:
            form = AjaxObjectiveForm(audit=audit)
        csrf_token_value = request.COOKIES['csrftoken']
        data['html'] = render_to_string('audits/right_panel_objective.html',
         {'form': form, 'audit_id': audit_id, 'objective_id': objective_id,
              'csrf_token_value': csrf_token_value})
        return JsonResponse(data)

    @csrf_exempt
    def post(self, request, audit_id, objective_id=None):
        data = {'status': 'failed'}
        audit = get_object_or_404(Audit, id=audit_id)
        papers = request.FILES.getlist('papers')
        if objective_id:
            obj = get_object_or_404(Objective, id=objective_id)
            form = AjaxObjectiveForm(request.POST, instance=obj, audit=audit)
        else:
            form = AjaxObjectiveForm(request.POST, audit=audit)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.audit = audit
            obj.changed_by = request.user
            obj.save()
            form.save_m2m()
            try:
                if papers:
                    Attachment.objects.bulk_create(
                        [Attachment(content_object=obj,
                             workpaper=attachment, filename=attachment.name)
                              for attachment in papers])
            except:
                pass
            data['status'] = 'success'
            data['html'] = {}
            for process in obj.process.all().values_list('id', flat=True):
                data['html']['acc_process_%s' % process] = \
                render_to_string('audits/ajax_binding_objective.html',
                    {'audit_id': audit_id, 'obj': obj, 'process_id': process})
        else:
            data['error'] = form.errors
        return JsonResponse(data)


class AjaxObjectiveDeleteView(generic.View):
    @csrf_exempt
    def get(self, request, objective_id):
        data = {}
        get_object_or_404(Objective, id=objective_id).delete()
        data['status'] = 'success'
        return JsonResponse(data)


class AjaxRiskAddEditView(generic.View):
    @csrf_exempt
    def get(self, request, audit_id, risk_id=None):
        audit = get_object_or_404(Audit, id=audit_id)
        data = {}
        if risk_id:
            obj = get_object_or_404(Risk, id=risk_id)
            form = AjaxRiskForm(instance=obj, audit=audit)
        else:
            form = AjaxRiskForm(audit=audit)
        csrf_token_value = request.COOKIES['csrftoken']
        data['html'] = render_to_string('audits/right_panel_risk.html',
         {'form': form, 'audit_id': audit_id, 'risk_id': risk_id,
              'csrf_token_value': csrf_token_value})
        return JsonResponse(data)

    @csrf_exempt
    def post(self, request, audit_id, risk_id=None):
        data = {'status': 'failed'}
        audit = get_object_or_404(Audit, id=audit_id)
        papers = request.FILES.getlist('papers')
        if risk_id:
            obj = get_object_or_404(Risk, id=risk_id)
            form = AjaxRiskForm(request.POST, instance=obj, audit=audit)
        else:
            form = AjaxRiskForm(request.POST, audit=audit)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.audit = audit
            obj.changed_by = request.user
            obj.save()
            form.save_m2m()
            try:
                if papers:
                    Attachment.objects.bulk_create(
                        [Attachment(content_object=obj,
                             workpaper=attachment, filename=attachment.name)
                              for attachment in papers])
            except:
                pass
            data['status'] = 'success'
            data['html'] = {}
            for objective in obj.objective.all():
                for process in objective.process.all()\
                    .values_list('id', flat=True):
                    data['html']['acc_pro_%s_obj_%s' % (process,
                         objective.id)] = \
                    render_to_string('audits/ajax_binding_risk.html',
                        {'audit_id': audit_id, 'obj': obj,
                             'process_id': process,
                             'objective_id': objective.id})
        else:
            data['error'] = form.errors
        return JsonResponse(data)


class AjaxRiskDeleteView(generic.View):
    @csrf_exempt
    def get(self, request, risk_id):
        data = {}
        get_object_or_404(Risk, id=risk_id).delete()
        data['status'] = 'success'
        return JsonResponse(data)


class AjaxControlAddEditView(generic.View):
    @csrf_exempt
    def get(self, request, audit_id, control_id=None):
        audit = get_object_or_404(Audit, id=audit_id)
        data = {}
        if control_id:
            obj = get_object_or_404(Control, id=control_id)
            form = AjaxControlForm(instance=obj, audit=audit)
        else:
            form = AjaxControlForm(audit=audit)
        csrf_token_value = request.COOKIES['csrftoken']
        data['html'] = render_to_string('audits/right_panel_control.html',
         {'form': form, 'audit_id': audit_id, 'control_id': control_id,
              'csrf_token_value': csrf_token_value})
        return JsonResponse(data)

    @csrf_exempt
    def post(self, request, audit_id, control_id=None):
        data = {'status': 'failed'}
        audit = get_object_or_404(Audit, id=audit_id)
        papers = request.FILES.getlist('papers')
        if control_id:
            obj = get_object_or_404(Control, id=control_id)
            form = AjaxControlForm(request.POST, instance=obj, audit=audit)
        else:
            form = AjaxControlForm(request.POST, audit=audit)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.audit = audit
            obj.changed_by = request.user
            obj.save()
            form.save_m2m()
            try:
                if papers:
                    Attachment.objects.bulk_create(
                        [Attachment(content_object=obj,
                             workpaper=attachment, filename=attachment.name)
                              for attachment in papers])
            except:
                pass
            data['status'] = 'success'
            data['html'] = {}
            for risk in obj.risk.all():
                for objective in risk.objective.all():
                    for process in objective.process.all()\
                        .values_list('id', flat=True):
                        data['html']['acc_pro_%s_obj_%s_risk_%s' % (process,
                             objective.id, risk.id)] = \
                        render_to_string('audits/ajax_binding_control.html',
                            {'audit_id': audit_id, 'obj': obj,
                                 'process_id': process, 'risk_id': risk.id,
                                 'objective_id': objective.id})
        else:
            data['error'] = form.errors
        return JsonResponse(data)


class AjaxControlDeleteView(generic.View):
    @csrf_exempt
    def get(self, request, control_id):
        data = {}
        get_object_or_404(Control, id=control_id).delete()
        data['status'] = 'success'
        return JsonResponse(data)


class AjaxTestAddEditView(generic.View):
    @csrf_exempt
    def get(self, request, audit_id, test_id=None):
        audit = get_object_or_404(Audit, id=audit_id)
        data = {}
        if test_id:
            obj = get_object_or_404(Test, id=test_id)
            form = AjaxTestForm(instance=obj, audit=audit)
        else:
            form = AjaxTestForm(audit=audit)
        csrf_token_value = request.COOKIES['csrftoken']
        data['html'] = render_to_string('audits/right_panel_test.html',
         {'form': form, 'audit_id': audit_id, 'test_id': test_id,
              'csrf_token_value': csrf_token_value})
        return JsonResponse(data)

    @csrf_exempt
    def post(self, request, audit_id, test_id=None):
        data = {'status': 'failed'}
        audit = get_object_or_404(Audit, id=audit_id)
        papers = request.FILES.getlist('papers')
        if test_id:
            obj = get_object_or_404(Test, id=test_id)
            form = AjaxTestForm(request.POST, instance=obj, audit=audit)
        else:
            form = AjaxTestForm(request.POST, audit=audit)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.audit = audit
            obj.changed_by = request.user
            obj.save()
            form.save_m2m()
            try:
                if papers:
                    Attachment.objects.bulk_create(
                        [Attachment(content_object=obj,
                             workpaper=attachment, filename=attachment.name)
                              for attachment in papers])
            except:
                pass
            data['status'] = 'success'
            data['html'] = {}
            for control in obj.control.all():
                for risk in control.risk.all():
                    for objective in risk.objective.all():
                        for process in objective.process.all()\
                            .values_list('id', flat=True):
                            data['html']['acc_pro_%s_obj_%s_risk_%s_ctrl_%s' % (process,
                                 objective.id, risk.id, control.id)] = \
                            render_to_string('audits/ajax_binding_test.html',
                                {'audit_id': audit_id, 'obj': obj,
                                     'process_id': process, 'risk_id': risk.id,
                                     'objective_id': objective.id,
                                      'control_id': control.id})
        else:
            data['error'] = form.errors
        return JsonResponse(data)


class AjaxTestDeleteView(generic.View):
    @csrf_exempt
    def get(self, request, test_id):
        data = {}
        get_object_or_404(Test, id=test_id).delete()
        data['status'] = 'success'
        return JsonResponse(data)


class AuditReport(generic.View):

    def get(self, request, pk):
        context = {}
        context['object'] = get_object_or_404(Audit, id=pk)
        context['test_passed_count'] = context['object'].test_audit.all()\
        .filter(result='PS').count()
        context['test_passed'] = context['object'].test_audit.all()\
        .filter(result='PS')
        context['test_failed'] = context['object'].test_audit.all()\
        .filter(result='FL')
        context['controls_passed'] = context['object'].control_audit.all()\
        .filter(test_control__result='PS').exclude(test_control__result='FL')\
        .distinct().count()

        return render(request, "audits/report_template.html", context)


from django import forms
from .models import Audit, Process, Objective, Risk, Control, Test,\
 Finding


class AuditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AuditForm, self).__init__(*args, **kwargs)
        for field_name, field in list(self.fields.items()):
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Audit
        fields = ('title', 'desc', 'status', 'start_date', 'end_date', 'fy')


class AddFromRepoForm(forms.ModelForm):

    all_processes = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Process.objects.all())
    #all_objectives = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Objective.objects.all())
    #all_risks = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Risk.objects.all())
    class Meta:
        model = Risk
        fields = ('all_processes',) #'all_risks','all_objectives'


class ProcessForm(forms.ModelForm):
    #audit = forms.HiddenInput()

    class Meta:
        model = Process
        fields = ('title', 'ref_id', 'desc', 'audit')
        #widgets = {'audit': forms.HiddenInput(),}


#ProcesesFormSet = inlineformset_factory(Audit, Process, can_delete=False, extra=1)


class ObjectiveForm(forms.ModelForm):

    class Meta:
        model = Objective
        fields = ('title', 'ref_id', 'desc', 'process')


class RiskForm(forms.ModelForm):

    class Meta:
        model = Risk
        fields = ('title','ref_id', 'desc', 'objective')


class ControlForm(forms.ModelForm):

    class Meta:
        model = Control
        fields = ('title','ref_id', 'desc', 'risk')


class TestForm(forms.ModelForm):

    class Meta:
        model = Test
        fields = ('title','ref_id', 'desc', 'control')


class AjaxTestResultForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AjaxTestResultForm, self).__init__(*args, **kwargs)
        for field_name, field in list(self.fields.items()):
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Test
        fields = ('result', 'result_desc')


class AjaxFindingForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AjaxFindingForm, self).__init__(*args, **kwargs)
        for field_name, field in list(self.fields.items()):
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Finding
        fields = ('title', 'desc')


class AjaxProcessForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AjaxProcessForm, self).__init__(*args, **kwargs)
        for field_name, field in list(self.fields.items()):
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Process
        fields = ('title','ref_id', 'desc')


class AjaxObjectiveForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        audit = kwargs.pop('audit', None)
        super(AjaxObjectiveForm, self).__init__(*args, **kwargs)
        for field_name, field in list(self.fields.items()):
            field.widget.attrs['class'] = 'form-control'
        self.fields['process'].queryset = audit.process_audit.all()

    class Meta:
        model = Objective
        fields = ('title','ref_id', 'desc', 'process')


class AjaxRiskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        audit = kwargs.pop('audit', None)
        super(AjaxRiskForm, self).__init__(*args, **kwargs)
        for field_name, field in list(self.fields.items()):
            field.widget.attrs['class'] = 'form-control'
        self.fields['objective'].queryset = audit.objective_audit.all()

    class Meta:
        model = Risk
        fields = ('title','ref_id', 'desc', 'objective')


class AjaxControlForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        audit = kwargs.pop('audit', None)
        super(AjaxControlForm, self).__init__(*args, **kwargs)
        for field_name, field in list(self.fields.items()):
            field.widget.attrs['class'] = 'form-control'
        self.fields['risk'].queryset = audit.risk_audit.all()

    class Meta:
        model = Control
        fields = ('title','ref_id', 'desc', 'control_type', 'risk')


class AjaxTestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        audit = kwargs.pop('audit', None)
        super(AjaxTestForm, self).__init__(*args, **kwargs)
        for field_name, field in list(self.fields.items()):
            field.widget.attrs['class'] = 'form-control'
        self.fields['control'].queryset = audit.control_audit.all()

    class Meta:
        model = Test
        fields = ('title','ref_id', 'desc', 'control')


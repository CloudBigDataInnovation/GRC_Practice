from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey,\
         GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_delete


class Attachment(models.Model):
    workpaper = models.FileField('Workpapers',
         upload_to='attachments/')
    filename = models.CharField(max_length=200)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    #def delete(self, *args, **kwargs):
        #super(Attachment, self).delete(*args, **kwargs)

    #def filename(self):
        #return self.workpaper.name.split('/')[-1]


class Audit(models.Model):
    DRAFT = "DR"
    ACTIVE = "AC"
    CLOSED = "CL"
    status_choices = (
        (DRAFT, 'Draft Status'),
        (ACTIVE, 'Active Status'),
        (CLOSED, 'Closed Status'),
        )
    title = models.CharField(max_length=200)
    desc = models.TextField('audit description', blank=True)
    status = models.CharField(max_length=2,
                              choices=status_choices,
                            default=DRAFT)
    start_date = models.DateField()
    end_date = models.DateField()
    fy = models.CharField('fiscal year', max_length=4)
    changed_by = models.ForeignKey('auth.User',on_delete=models.DO_NOTHING,)
    changed_on = models.DateTimeField(auto_now=True)
    papers = GenericRelation(Attachment)

    def __str__(self):
        return self.title

    def get_risks(self):
        try:
            obj_ids = Objective.objects\
            .filter(process__in=self.process_audit.all())\
                    .values_list('id', flat=True)
            return Risk.objects.filter(objective__in=obj_ids).distinct()
        except:
            return None

    def get_controls(self):
        try:
            risk_ids = self.get_risks().values_list('id', flat=True)
            return Control.objects.filter(risk__in=risk_ids).distinct()
        except:
            return None


class Process(models.Model):
    audit = models.ForeignKey(Audit, related_name="process_audit", on_delete=models.CASCADE,)
    title = models.CharField(max_length=200)
    ref_id = models.CharField('reference ID', max_length=200, null=True, blank=True, default="")
    desc = models.TextField('process description', blank=True)
    changed_by = models.ForeignKey('auth.User',on_delete=models.DO_NOTHING,)
    changed_on = models.DateTimeField(auto_now=True)
    papers = GenericRelation(Attachment)

    def __str__(self):
        return self.title


class Objective(models.Model):
    audit = models.ForeignKey(Audit, related_name="objective_audit", on_delete=models.CASCADE,)
    process = models.ManyToManyField(Process, verbose_name="related processes",
         blank=False, related_name="obj_process")
    title = models.CharField(max_length=200)
    ref_id = models.CharField('reference ID', max_length=200, null=True, blank=True, default="")
    desc = models.TextField('objective description', blank=True)
    changed_by = models.ForeignKey('auth.User',on_delete=models.DO_NOTHING,)
    changed_on = models.DateTimeField(auto_now=True)
    papers = GenericRelation(Attachment)

    def __str__(self):
        return self.title


class Risk(models.Model):
    audit = models.ForeignKey(Audit, related_name="risk_audit", on_delete=models.CASCADE,)
    objective = models.ManyToManyField(Objective, related_name="risk_obj",
         verbose_name="related objectives", blank=False)
    title = models.CharField(max_length=200)
    ref_id = models.CharField('reference ID', max_length=200, null=True, blank=True, default="")
    desc = models.TextField('risk description', blank=True)
    changed_by = models.ForeignKey('auth.User',on_delete=models.DO_NOTHING,)
    changed_on = models.DateTimeField(auto_now=True)
    papers = GenericRelation(Attachment)

    def __str__(self):
        return self.title


class Control(models.Model):
    KEY = "KY"
    SECONDARY = "SC"
    con_type = (
        (KEY, 'Key Control'),
        (SECONDARY, 'Secondary Control'),
        )
    
    audit = models.ForeignKey(Audit, related_name="control_audit", on_delete=models.CASCADE,)
    risk = models.ManyToManyField(Risk, verbose_name="related risks",
         blank=False, related_name="control_risk")
    title = models.CharField(max_length=200)
    ref_id = models.CharField('reference ID', max_length=200, null=True, blank=True, default="")
    desc = models.TextField('control description', blank=True)
    control_type = models.CharField(max_length=2,
                              choices=con_type,
                            default=KEY)
    changed_by = models.ForeignKey('auth.User',on_delete=models.DO_NOTHING,)
    changed_on = models.DateTimeField(auto_now=True)
    papers = GenericRelation(Attachment)

    def __str__(self):
        return self.title


class Test(models.Model):
    PASSED = "PS"
    FAILED = "FL"
    status_choices = (
        (PASSED, 'Passed'),
        (FAILED, 'Failed'),
        )
    audit = models.ForeignKey(Audit, related_name="test_audit", on_delete=models.CASCADE,)
    control = models.ManyToManyField(Control, verbose_name="related controls",
         blank=False, related_name="test_control")
    title = models.CharField(max_length=200)
    ref_id = models.CharField('reference ID', max_length=200, null=True, blank=True, default="")
    desc = models.TextField('test description', blank=True)
    result = models.CharField(max_length=2,
                              choices=status_choices,
                            default=FAILED)
    result_desc = models.TextField('test result description', blank=True)
    changed_by = models.ForeignKey('auth.User',on_delete=models.DO_NOTHING,)
    changed_on = models.DateTimeField(auto_now=True)
    papers = GenericRelation(Attachment)

    def __str__(self):
        return self.title


class Finding(models.Model):
    test = models.ForeignKey(Test, verbose_name="related tests",
         blank=False, related_name="find_test", on_delete=models.CASCADE,)
    title = models.CharField(max_length=200)
    desc = models.TextField('finding description', blank=True)
    changed_by = models.ForeignKey('auth.User',on_delete=models.DO_NOTHING,)
    changed_on = models.DateTimeField(auto_now=True)
    papers = GenericRelation(Attachment)

    def __str__(self):
        return self.title


class Action(models.Model):
    finding = models.ManyToManyField(Finding, verbose_name="related findings",
         blank=False, related_name="action_find")
    title = models.CharField(max_length=200)
    desc = models.TextField('finding description', blank=True)
    changed_by = models.ForeignKey('auth.User',on_delete=models.DO_NOTHING,)
    changed_on = models.DateTimeField(auto_now=True)
    #assigned_to = models.ForeignKey('auth.User')

    def __str__(self):
        return self.title


class Auditors(models.Model):
    audit = models.ForeignKey('Audit', on_delete=models.CASCADE,)
    auditor_assigned = models.ForeignKey('auth.User', blank=False, on_delete=models.DO_NOTHING,)
    assigned_date = models.DateTimeField(auto_now=True)


def delete_attachment(sender, instance, **kwargs):
    instance.workpaper.delete()

pre_delete.connect(delete_attachment, sender=Attachment)


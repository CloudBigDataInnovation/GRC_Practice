from django.contrib import admin

# Register your models here.
from .models import Audit, Process, Objective, Risk, Control,\
 Test, Finding, Action, Attachment

admin.site.register(Audit)
admin.site.register(Process)
admin.site.register(Objective)
admin.site.register(Risk)
admin.site.register(Control)
admin.site.register(Test)
admin.site.register(Finding)
admin.site.register(Action)
admin.site.register(Attachment)

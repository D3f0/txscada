from django.contrib.admin.actions import delete_selected
import object_tools
import models
from django.http import HttpResponse


class ImportFormulasFromExcel(object_tools.ObjectTool):
    name = 'import'
    label = 'Import from XLS'

    def view(self, request, extra_context=None):
        return HttpResponse("Hello")
        queryset = self.model.objects.all()
        response = delete_selected(self.modeladmin, request, queryset)
        if response:
            return response
        else:
            return self.modeladmin.changelist_view(request)

object_tools.tools.register(ImportFormulasFromExcel, models.Formula)
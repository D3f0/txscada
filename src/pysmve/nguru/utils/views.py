from django.views.generic.base import TemplateView


class URLBasedTemplateView(TemplateView):

    def get_template_names(self):
        return self.kwargs['template_name']
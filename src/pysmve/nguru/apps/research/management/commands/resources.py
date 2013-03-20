from django.core.management.base import NoArgsCommand
from django.db.models.loading import get_models


RESOURCE = '''
class {resource}(ModelResource):
    """REST resource for {object_name}"""
    class Meta:
        resource_name = '{module_name}'
        queryset = {object_name}.objects.all()
        allowed_methods = ['get', ]
'''


class Command(NoArgsCommand):

    def handle_noargs(self, **options):

        include = lambda model: model._meta.app_label in ('hmi', 'mara')
        models = filter(include, get_models())
        resources = []
        for model in models:
            meta = model._meta
            resource = '%sResource' % meta.object_name
            print RESOURCE.format(
                resource=resource,
                module_name=meta.module_name,
                object_name=meta.object_name
            )
            resources.append(resource)
        print "api = Api(api_name='v1')"
        print
        for resource in resources:
            print "api.register({resource}())".format(resource=resource)

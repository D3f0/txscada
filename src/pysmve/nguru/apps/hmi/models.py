from django.db import models


class Screen(models.Model):
    parent = models.ForeignKey('self',
                                related_name='children',
                                null=True,
                                blank=True)

    class Meta:
        abstract = True

class SVGScreen(Screen):
    svg = models.FileField(upload_to="svg_screens")
    name = models.CharField(max_length=60)
    root = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


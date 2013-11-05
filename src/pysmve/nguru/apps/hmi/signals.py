import os
# These two auto-delete files from filesystem when they are unneeded:
#@receiver(models.signals.post_delete, sender=SVGScreen)
def auto_delete_file_on_delete(sender, instance, file_field_name='svg', **kwargs):
    """Deletes file from filesystem
    when corresponding `SVGScreen` object is deleted.
    """
    f = getattr(instance, file_field_name, None)
    if f:
        if os.path.isfile(f.path):
            os.remove(f.path)

#@eceiver(models.signals.pre_save, sender=SVGScreen)
def auto_delete_file_on_change(sender, instance, file_field_name='svg', **kwargs):
    """Deletes file from filesystem
    when corresponding `SVGScreen` object is changed.
    """
    print sender
    if not instance.pk:
        return False

    try:
        old = sender.objects.get(pk=instance.pk)
        old_file = getattr(old, file_field_name, None)
    except sender.DoesNotExist:
        return False

    new_file = getattr(instance, file_field_name)
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)

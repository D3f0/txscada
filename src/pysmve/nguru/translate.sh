# Translation is hard to be constructed as
# a fabric task, so this shell script executes all the required steps

# Search for all string
python manage.py makemessages -a 
xdg-open conf/locale/es/LC_MESSAGES/django.po
python manage.py compilemessages

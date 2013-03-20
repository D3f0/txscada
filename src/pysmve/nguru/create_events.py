from apps.mara.models import *

from itertools import chain
from string import digits, ascii_uppercase as letters
from random import choice, sample
from datetime import datetime, timedelta
dis = DI.objects.all()


# for i in range(1000):
#     date = datetime.now() + timedelta(days=choice([-2, -1, 0, 1, 2]))

#     Event.objects.create(di=choice(dis),
#                         value=choice([0,1]),
#                         q=choice([0,1,2]),
#                         timestamp=date)


for di in dis:
    di.tag = ''.join(chain(sample(letters, 2), sample(digits, 4), sample(letters, 2)))
    di.save()
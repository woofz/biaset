
from allenatorestrategy import AllenatoreStrategy
from castrategy import CaStrategy
from strategy import Context
import sys, os
sys.path.append("/app/biaset")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biaset.settings')
import django
django.setup()

from django.contrib.auth.models import User


if __name__ == '__main__':
    strategy = Context(CaStrategy())
    user = User.objects.get(pk=19)
    print(strategy.doOperation(user))
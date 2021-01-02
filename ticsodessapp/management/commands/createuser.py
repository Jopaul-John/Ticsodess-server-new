from django.conf import settings
from django.core.management.base import BaseCommand
from ticsodessapp.models import User

class Command(BaseCommand):

    def handle(self, *args, **options):
        if User.objects.count() == 0:
            admin = User.objects.create_superuser(email="jopauljohn@gmail.com", password="rememberthis")
            admin.save()
        else:
            print('Admin accounts can only be initialized if no Accounts exist')
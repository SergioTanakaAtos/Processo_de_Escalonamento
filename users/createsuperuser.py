import os 
from dotenv import load_dotenv
from django.contrib.auth.models import User
load_dotenv()

# Path: users/createsuperuser.py

if not User.objects.filter(username=os.getenv('SUPERUSER_NAME')).exists():
    User.objects.create_superuser(os.getenv('SUPERUSER_NAME'), os.getenv('SUPERUSER_EMAIL'), os.getenv('SUPERUSER_PASSWORD'))
print('Superuser already exists')
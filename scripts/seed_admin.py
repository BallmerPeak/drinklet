## Run `python manage.py runscript seed_admin`

from django.db import IntegrityError
from user.models import UserProfile
from django.contrib.auth.models import User

username = 'admin'
password = 'admin1'
email = 'admin@admin.com'

try:
	user = User.objects.create_user(username, email, password)
	UserProfile.get_or_create_profile(user)
except IntegrityError as e:
	print("Admin already in the database.")

print("** Admin Seeded **")
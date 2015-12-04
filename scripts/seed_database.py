from django.core.management import execute_from_command_line

execute_from_command_line(["manage.py", "migrate"])

from scripts import seed_admin
from scripts import seed_ingredients
from scripts import seed_recipes
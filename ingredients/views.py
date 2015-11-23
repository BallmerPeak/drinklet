from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.context_processors import csrf

import json

from .models import Ingredient
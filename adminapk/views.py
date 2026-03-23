from django.shortcuts import render
from .models import *
from core.models import *
from seller.models import *
from customer.models import *

# Create your views here.
def admin_dashboard(request):
    return render(request,"adminapk/admin_dashboard.html")
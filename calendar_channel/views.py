from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import CreateUserForm
from django.contrib import messages
from django.forms.models import model_to_dict
from .models import UserEvents
import datetime
import json
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY
from django.core import serializers


# Create your views here.


def home(request):
    return render(request, "home.html")


def register_page(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)
            return redirect('login')

    context = {'form': form}
    return render(request, 'register.html', context)


def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Username OR Password is Incorrect')

    return render(request, 'login.html')


def logout_user(request):
    logout(request)
    return redirect('/')


def calendar_month(request):
    if request.method == 'POST':
        year = request.POST['year']
        month = request.POST['month']
        day = request.POST['day']
        request.session['date'] = {'year': year, 'month': month, 'day': day}
        print(year, month, day)
    return render(request, 'calendar.html')


def calendar_day(request):
    current_user = request.user
    date = request.session['date']
    month_number = datetime.datetime.strptime(date['month'][0:3], '%b').month
    dt_obj = datetime.date(int(date['year']), month_number, int(date['day']))
    if request.method == 'POST':
        event = request.POST.get('event')
        begin_hr = request.POST.get('begin_hr')
        begin_min = request.POST.get('begin_min')
        end_hr = request.POST.get('end_hr')
        end_min = request.POST.get('end_min')
        description = request.POST.get('description')
        repeat = request.POST.get('repeat')
        repeat_end = request.POST.get('repeat_end')


        if request.POST.get("create"):
            if event == "" or begin_hr == '' or begin_min == '' or end_hr == '' or end_min == '':
                messages.info(request, 'Key features are empty')
            else:
                begin_time = int(begin_hr) * 100 + int(begin_min)
                end_time = int(end_hr) * 100 + int(end_min)
                if begin_time >= end_time:
                    messages.info(request, 'End time is earlier than and equal to Begin time')
                else:
                    if repeat == 'once':
                        UserEvents.objects.create(event=event, date=dt_obj, beginning=begin_time, end=end_time,
                                                  user_id_id=current_user.id, description=description)
                    elif repeat_end == '':
                        messages.info(request, 'End date is blank')
                    else:
                        repeat_end = datetime.datetime.strptime(repeat_end, "%Y-%m-%d").date()
                        if repeat_end < dt_obj:
                            messages.info(request, 'End date is earlier than Current date')
                        else:
                            if repeat == 'daily':
                                for dt in rrule(DAILY, dtstart=dt_obj, until=repeat_end):
                                    UserEvents.objects.create(event=event, date=dt.date(), beginning=begin_time,
                                                              end=end_time,
                                                              user_id_id=current_user.id, description=description)
                            elif repeat == 'weekly':
                                for dt in rrule(WEEKLY, dtstart=dt_obj, until=repeat_end):
                                    UserEvents.objects.create(event=event, date=dt.date(), beginning=begin_time,
                                                              end=end_time,
                                                              user_id_id=current_user.id, description=description)
                            elif repeat == 'monthly':
                                for dt in rrule(MONTHLY, dtstart=dt_obj, until=repeat_end):
                                    UserEvents.objects.create(event=event, date=dt.date(), beginning=begin_time,
                                                              end=end_time,
                                                              user_id_id=current_user.id, description=description)

        if request.POST.get("delete"):
            try:
                begin_time = int(begin_hr) * 100 + int(begin_min)
                end_time = int(end_hr) * 100 + int(end_min)
                UserEvents.objects.filter(event=event, date=dt_obj, beginning=begin_time, end=end_time,
                                          user_id_id=current_user.id, description=description).delete()
            except Exception:
                messages.info(request, 'Event Not Found')

    context = {}
    event_list = []

    event_query = UserEvents.objects.filter(user_id=current_user.id, date=dt_obj)
    for event in event_query:
        event_list.append(model_to_dict(event))
    event_js = json.dumps(event_list, default=str)
    context['events'] = event_js
    context['date'] = str(dt_obj)

    print(event_js)
    return render(request, 'calendar_day.html', context)

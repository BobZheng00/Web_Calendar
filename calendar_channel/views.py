import datetime
import json

from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from .forms import CreateUserForm
from .models import UserEvents, Follower


@csrf_exempt
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


# Create your views here.

@csrf_exempt
def home(request):
    return render(request, "home.html")


@csrf_exempt
def testing(request):
    return render(request, "test.html")


@csrf_exempt
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


@csrf_exempt
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


@csrf_exempt
def logout_user(request):
    logout(request)
    return redirect('/')


@csrf_exempt
def friends_view(request):
    current_user = request.user
    friends = {'followed': Follower.objects.filter(requester_id=current_user.id, is_agreed=True).count(),
               'follower': Follower.objects.filter(receiver_id=current_user.id, is_agreed=True).count(),
               'requesting': []}

    for requesting in Follower.objects.filter(receiver_id=current_user.id, is_agreed=False).values():
        for single_request in User.objects.filter(id=requesting["requester_id"]).values():
            friends['requesting'].append(single_request["username"])

    if is_ajax(request=request):
        if "requester" in request.GET:
            requester_id = User.objects.filter(username=request.GET['requester']).get().id
            Follower.objects.filter(receiver_id=current_user.id, requester_id=requester_id).update(is_agreed=True)
        else:
            requester_id = User.objects.filter(username=request.GET['requester_decline']).get().id
            Follower.objects.filter(receiver_id=current_user.id, requester_id=requester_id).delete()

    elif request.method == 'POST' and request.POST['action'] == "Sent Request":
        username = request.POST.get('username')
        if username == request.user.username:
            messages.info(request, 'You Cannot Follow Yourself')
        elif not User.objects.filter(username=username).exists():
            messages.info(request, 'User Not Exist')
        elif Follower.objects.filter(requester_id=request.user, receiver__username=username).exists():
            messages.info(request, 'You have Followed the User')
        else:
            Follower.objects.create(requester_id=request.user.id,
                                    receiver_id=User.objects.get(username=username).id)

    return render(request, 'friends.html', friends)


@csrf_exempt
def calendar_month(request):
    if request.method == 'POST':
        year = request.POST['year']
        month = request.POST['month']
        day = request.POST['day']
        request.session['date'] = {'year': year, 'month': month, 'day': day}
        print(year, month, day)
    return render(request, 'calendar.html')


def create_repeated_events(user_id, event_info, start_date, end_date, repeat_rule):
    for dt in rrule(repeat_rule, dtstart=start_date, until=end_date):
        UserEvents.objects.create(
            event=event_info["event"],
            date=dt.date(),
            beginning=event_info["begin_time"],
            end=event_info["end_time"],
            user_id_id=user_id,
            description=event_info["description"]
        )


def handle_create_event(request, current_user, dt_obj, event_info) -> bool:
    if event_info["repeat"] == 'once':
        UserEvents.objects.create(event=event_info["event"],
                                  date=dt_obj,
                                  beginning=event_info["begin_time"],
                                  end=event_info["end_time"],
                                  user_id_id=current_user.id,
                                  description=event_info["description"])
        return False

    if event_info["repeat_end"] == '':
        messages.info(request, 'End date is blank')
        return True

    repeat_end = datetime.datetime.strptime(event_info["repeat_end"], "%Y-%m-%d").date()

    if repeat_end < dt_obj:
        messages.info(request, 'End date is earlier than Current date')
        return True

    repeat_rules = {
        'daily': DAILY,
        'weekly': WEEKLY,
        'monthly': MONTHLY
    }
    repeat_rule = repeat_rules.get(event_info["repeat"])

    if repeat_rule:
        create_repeated_events(current_user.id, event_info, dt_obj, repeat_end, repeat_rule)
        return False

    messages.info(request, 'Invalid create event request')
    return True


def handle_delete_event(request, current_user, dt_obj, event_info) -> bool:
    if UserEvents.objects.filter(event=event_info["event"], date=dt_obj, beginning=event_info["begin_time"],
                                 end=event_info["end_time"],
                                 user_id_id=current_user.id, description=event_info["description"]).exists():
        UserEvents.objects.filter(event=event_info["event"], date=dt_obj, beginning=event_info["begin_time"],
                                  end=event_info["end_time"],
                                  user_id_id=current_user.id, description=event_info["description"]).delete()
        return False

    messages.info(request, 'Event Not Found')
    return True


def handle_event(request, current_user, dt_obj) -> bool:
    event = request.POST.get('event')
    begin_hr = request.POST.get('begin_hr')
    begin_min = request.POST.get('begin_min')
    end_hr = request.POST.get('end_hr')
    end_min = request.POST.get('end_min')

    if any(key == '' for key in [event, begin_hr, begin_min, end_hr, end_min]):
        messages.info(request, 'Key information is empty')
        return True

    begin_time = int(begin_hr) * 100 + int(begin_min)
    end_time = int(end_hr) * 100 + int(end_min)
    if begin_time >= end_time:
        messages.info(request, 'End time is earlier than and equal to Begin time')
        return True

    event_info = {
        'event': event,
        'begin_time': begin_time,
        'end_time': end_time,
        'description': request.POST.get('description'),
        'repeat': request.POST.get('repeat'),
        'repeat_end': request.POST.get('repeat_end')
    }

    if request.POST.get("create"):
        return handle_create_event(request, current_user, dt_obj, event_info)

    if request.POST.get("delete"):
        return handle_delete_event(request, current_user, dt_obj, event_info)

    return False


@csrf_exempt
def calendar_day(request):
    current_user = request.user
    date = request.session['date']
    month_number = datetime.datetime.strptime(date['month'][0:3], '%b').month
    dt_obj = datetime.date(int(date['year']), month_number, int(date['day']))
    error_display = False

    if request.method == 'POST':
        error_display = handle_event(request, current_user, dt_obj)

    context = {}
    event_list = []

    event_query = UserEvents.objects.filter(user_id=current_user.id, date=dt_obj)
    for event in event_query:
        event_list.append(model_to_dict(event))
    event_js = json.dumps(event_list, default=str)
    context['events'] = event_js
    context['date'] = str(dt_obj)
    context['error_display'] = error_display

    print(event_js)
    return render(request, 'calendar_day.html', context)
import datetime
import json

from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.forms.models import model_to_dict
from django.http import HttpRequest, JsonResponse
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
               'followed_list': {},
               'follower_list': {},
               'requesting': []}

    for followed in Follower.objects.filter(requester_id=current_user.id, is_agreed=True).values():
        for single_followed in User.objects.filter(id=followed["receiver_id"]).values():
            friends['followed_list'][single_followed["username"]] = followed['allowed_access']

    for follower in Follower.objects.filter(receiver_id=current_user.id, is_agreed=True).values():
        for single_follower in User.objects.filter(id=follower["requester_id"]).values():
            friends['follower_list'][single_follower["username"]] = follower['allowed_access']

    for requesting in Follower.objects.filter(receiver_id=current_user.id, is_agreed=False).values():
        for single_request in User.objects.filter(id=requesting["requester_id"]).values():
            friends['requesting'].append(single_request["username"])

    friends["follower_list_json"] = json.dumps(friends["follower_list"], default=str)
    friends["followed_list_json"] = json.dumps(friends["followed_list"], default=str)

    if is_ajax(request=request):
        if "requester" in request.GET:
            requester_id = User.objects.filter(username=request.GET['requester']).get().id
            Follower.objects.filter(receiver_id=current_user.id, requester_id=requester_id).update(is_agreed=True)
        elif "requester_decline" in request.GET:
            requester_id = User.objects.filter(username=request.GET['requester_decline']).get().id
            Follower.objects.filter(receiver_id=current_user.id, requester_id=requester_id).delete()
        elif "change_accessibility" in request.GET:
            follower_id = User.objects.filter(username=request.GET['follower']).get().id
            Follower.objects.filter(receiver_id=current_user.id, requester_id=follower_id).update(
                allowed_access=(request.GET['change_accessibility'] == 'true'))

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
    print(friends)
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


def create_repeated_events(user_id: int, event_info: dict[str, str],
                           start_date: datetime.date, end_date: datetime.date, repeat_rule: int):
    for dt in rrule(repeat_rule, dtstart=start_date, until=end_date):
        UserEvents.objects.create(
            event=event_info["event"],
            date=dt.date(),
            beginning=event_info["begin_time"],
            end=event_info["end_time"],
            user_id_id=user_id,
            description=event_info["description"]
        )


def handle_create_event(request: WSGIRequest, current_user: User,
                        dt_obj: datetime.date, event_info: dict[str, str]) -> bool:
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


def handle_delete_event(request: WSGIRequest, current_user: User,
                        dt_obj: datetime.date, event_info: dict[str, str]) -> bool:
    if UserEvents.objects.filter(event=event_info["event"], date=dt_obj, beginning=event_info["begin_time"],
                                 end=event_info["end_time"],
                                 user_id_id=current_user.id, description=event_info["description"]).exists():
        UserEvents.objects.filter(event=event_info["event"], date=dt_obj, beginning=event_info["begin_time"],
                                  end=event_info["end_time"],
                                  user_id_id=current_user.id, description=event_info["description"]).delete()
        return False

    messages.info(request, 'Event Not Found')
    return True


def handle_event(request: WSGIRequest, current_user: User, dt_obj: datetime.date) -> bool:
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
        messages.info(request, 'End time is earlier than or equal to Begin time')
        return True

    event_info = {
        'event': event,
        'begin_time': begin_time,
        'end_time': end_time,
        'description': request.POST.get('description'),
        'repeat': request.POST.get('repeat'),
        'repeat_end': request.POST.get('repeat_end')
    }

    if request.POST.get("create"):  # TODO: event that ends at 0:00(24:00) cannot be handled
        return handle_create_event(request, current_user, dt_obj, event_info)

    if request.POST.get("delete"):
        return handle_delete_event(request, current_user, dt_obj, event_info)

    return False


@csrf_exempt
def calendar_day(request):
    current_user = request.user
    error_display = False
    date = request.session['date']
    month_number = datetime.datetime.strptime(date['month'][0:3], '%b').month
    dt_obj = datetime.date(int(date['year']), month_number, int(date['day']))

    if request.method == 'POST' and request.POST.get("change"):
        dt_obj = reload_date(request)
    elif request.method == 'POST':
        error_display = handle_event(request, current_user, dt_obj)
        if not error_display:
            return redirect("/calendar/day")

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


def calendar_week(request):
    current_user = request.user
    error_display = False
    date = request.session['date']
    month_number = datetime.datetime.strptime(date['month'][0:3], '%b').month
    dt_obj = datetime.date(int(date['year']), month_number, int(date['day']))
    dt_obj = dt_obj - datetime.timedelta(days=dt_obj.weekday())  # dt_obj will always be a Sunday

    if request.method == 'POST' and request.POST.get("change"):
        dt_obj = reload_date(request)
    elif request.method == 'POST' and request.POST.get('switch_day'):
        reload_date(request)
        return redirect("/calendar/day")
    elif request.method == 'POST':
        if request.POST.get('date'):
            target_date = datetime.datetime.strptime(request.POST.get('date'), "%Y-%m-%d").date()
            error_display = handle_event(request, current_user, target_date)
        else:
            error_display = True
            messages.info(request, 'Date is missing')

        if not error_display:
            return redirect("/calendar/week")

    context = {}
    event_list = {}

    for i in range(7):
        event_query = UserEvents.objects.filter(user_id=current_user.id, date=dt_obj + datetime.timedelta(days=i))
        event_list[str(i)] = []
        for event in event_query:
            event_list[str(i)].append(model_to_dict(event))

    event_js = json.dumps(event_list, default=str)
    context['events'] = event_js
    context['date'] = str(dt_obj)
    context['error_display'] = error_display
    print(event_js)

    return render(request, 'calendar_week.html', context)


def reload_date(request):
    request.session['date'] = {'year': request.POST['year'],
                               'month': request.POST['month'],
                               'day': request.POST['day']}
    return datetime.date(int(request.POST.get('year')),
                         datetime.datetime.strptime(request.POST.get('month')[0:3], '%b').month,
                         int(request.POST.get('day')))

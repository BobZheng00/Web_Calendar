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
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from allauth.socialaccount.models import SocialAccount

from .events import InputEvents
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
        if request.POST.get('access_calendar'):
            return JsonResponse({'redirect': ''})
        elif "requester" in request.GET:
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
    return render(request, 'calendar.html', {"friend_username": 'default'})


@csrf_exempt
def calendar_day(request):
    current_user = request.user
    valid_request = True
    error_message = ""
    date = request.session['date']
    dt_obj = datetime.date(int(date['year']),
                           datetime.datetime.strptime(date['month'][0:3], '%b').month,
                           int(date['day']))

    if request.POST.get("change"):
        dt_obj = reload_date(request)
    elif request.method == 'POST':
        input_event = InputEvents(user_id=current_user.id, event=request.POST.get('event'),
                                  date=dt_obj, begin_hr=request.POST.get('begin_hr'),
                                  begin_min=request.POST.get('begin_min'), end_hr=request.POST.get('end_hr'),
                                  end_min=request.POST.get('end_min'), description=request.POST.get('description'),
                                  is_private=False if request.POST.get('is_private') is None
                                  else request.POST.get('is_private').lower() == 'on',
                                  is_pined=False if request.POST.get('is_pined') is None
                                  else request.POST.get('is_pined').lower() == 'on',
                                  hex_color="#11be7c" if request.POST.get('hex_color') is None
                                  else request.POST.get('hex_color'),
                                  repeated_rule=request.POST.get('repeat'),
                                  repeated_end=None if request.POST.get(
                                      'repeat_end') == "" else datetime.datetime.strptime(
                                      request.POST.get('repeat_end'), "%Y-%m-%d").date())

        if request.POST.get("create"):
            valid_request, error_message = input_event.create_event()
        elif request.POST.get("delete"):
            valid_request, error_message = input_event.delete_event()
        else:
            messages.info(request, "Invalid request")

        messages.info(request, error_message)

        if valid_request:
            return redirect("/calendar/day")

    context = {}
    event_list = []

    for event in UserEvents.objects.filter(user_id=current_user.id, date=dt_obj):
        event_list.append(model_to_dict(event))

    context['pinned'] = get_pinned_events(current_user.id)
    print(event_list)
    context['events'] = json.dumps(event_list, default=str)
    context['date'] = str(dt_obj)
    context['valid_request'] = valid_request
    context["friend_username"] = 'default'

    return render(request, 'calendar_day.html', context)


def calendar_week(request):
    current_user = request.user
    valid_request = True
    error_message = ""
    date = request.session['date']
    dt_obj = datetime.date(int(date['year']),
                           datetime.datetime.strptime(date['month'][0:3], '%b').month,
                           int(date['day']))
    dt_obj = dt_obj - datetime.timedelta(days=dt_obj.weekday())  # dt_obj will always be a Sunday

    if request.POST.get("change"):
        dt_obj = reload_date(request)
    elif request.POST.get('switch_day'):
        reload_date(request)
        return JsonResponse({'redirect': '/calendar/day'})
    elif request.method == 'POST':
        input_event = InputEvents(user_id=current_user.id,
                                  event=request.POST.get('event'),
                                  date=None if request.POST.get('date') == ""
                                  else datetime.datetime.strptime(request.POST.get('date'), "%Y-%m-%d").date(),
                                  begin_hr=request.POST.get('begin_hr'), begin_min=request.POST.get('begin_min'),
                                  end_hr=request.POST.get('end_hr'), end_min=request.POST.get('end_min'),
                                  description=request.POST.get('description'),
                                  is_private=False if request.POST.get('is_private') is None
                                  else request.POST.get('is_private').lower() == 'on',
                                  is_pined=False if request.POST.get('is_pined') is None
                                  else request.POST.get('is_pined').lower() == 'on',
                                  hex_color="#11be7c" if request.POST.get('hex_color') is None
                                  else request.POST.get('hex_color'),
                                  repeated_rule=request.POST.get('repeat'),
                                  repeated_end=None if request.POST.get('repeat_end') == ""
                                  else datetime.datetime.strptime(request.POST.get('repeat_end'), "%Y-%m-%d").date())

        if request.POST.get("create"):
            valid_request, error_message = input_event.create_event()
        elif request.POST.get("delete"):
            valid_request, error_message = input_event.delete_event()
        else:
            messages.info(request, "Invalid request")

        messages.info(request, error_message)

        if valid_request:
            return redirect("/calendar/week")

    context = {}
    event_list = {}

    for i in range(7):
        event_list[str(i)] = []
        for event in UserEvents.objects.filter(user_id=current_user.id, date=dt_obj + datetime.timedelta(days=i)):
            event_list[str(i)].append(model_to_dict(event))

    context['events'] = json.dumps(event_list, default=str)
    context['pinned'] = get_pinned_events(current_user.id)
    context['date'] = str(dt_obj)
    context['valid_request'] = valid_request
    context["friend_username"] = 'default'

    return render(request, 'calendar_week.html', context)


def reload_date(request, session_name='date'):
    request.session[session_name] = {'year': request.POST['year'],
                                     'month': request.POST['month'],
                                     'day': request.POST['day']}
    return datetime.date(int(request.POST.get('year')),
                         datetime.datetime.strptime(request.POST.get('month')[0:3], '%b').month,
                         int(request.POST.get('day')))


def friend_calendar(request, username: str):
    if request.method == 'POST':
        year = request.POST['year']
        month = request.POST['month']
        day = request.POST['day']
        request.session['friend_date'] = {'username': username, 'year': year, 'month': month, 'day': day}
        print(year, month, day)
    return render(request, 'calendar.html', {"friend_username": username})


def friend_calendar_week(request, username: str):
    friend_id = User.objects.filter(username=username).get().id
    date = request.session['friend_date']
    month_number = datetime.datetime.strptime(date['month'][0:3], '%b').month
    dt_obj = datetime.date(int(date['year']), month_number, int(date['day']))
    dt_obj = dt_obj - datetime.timedelta(days=dt_obj.weekday())  # dt_obj will always be a Sunday

    if request.method == 'POST' and request.POST.get("change"):
        dt_obj = reload_date(request, 'friend_date')
    elif request.method == 'POST' and request.POST.get('switch_day'):
        reload_date(request, 'friend_date')
        return JsonResponse({'redirect': '/' + username + '/calendar/day'})

    context = {}
    event_list = {}

    for i in range(7):
        event_query = UserEvents.objects.filter(user_id=friend_id, date=dt_obj + datetime.timedelta(days=i))
        event_list[str(i)] = [model_to_dict(event) for event in event_query if not model_to_dict(event)['is_private']]

    event_js = json.dumps(event_list, default=str)
    context['friend_username'] = username
    context['events'] = event_js
    context['date'] = str(dt_obj)
    context['error_display'] = 'no_need'
    print(event_js)
    return render(request, 'calendar_week.html', context)


def friend_calendar_day(request, username: str):
    friend_id = User.objects.filter(username=username).get().id
    date = request.session['friend_date']
    month_number = datetime.datetime.strptime(date['month'][0:3], '%b').month
    dt_obj = datetime.date(int(date['year']), month_number, int(date['day']))

    if request.POST.get("change"):
        dt_obj = reload_date(request, "friend_date")

    context = {}

    event_query = UserEvents.objects.filter(user_id=friend_id, date=dt_obj)
    event_list = [model_to_dict(event) for event in event_query if not model_to_dict(event)['is_private']]
    event_js = json.dumps(event_list, default=str)
    context['friend_username'] = username
    context['events'] = event_js
    context['date'] = str(dt_obj)
    context['error_display'] = "no_need"

    print(event_js)
    return render(request, 'calendar_day.html', context)


def get_pinned_events(user_id: int) -> str:
    pinned_list = [model_to_dict(event) for event in
                   UserEvents.objects.filter(user_id=user_id, is_pined=True).order_by("date")]
    return json.dumps(pinned_list, default=str)


class UserDataView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, discord_id, *args, **kwargs):
        user = SocialAccount.objects.filter(provider='discord', uid=discord_id).first()
        if user is None:
            return Response({"error": "User not found"}, status=404)
        if "fetch" in request.query_params:
            start_date = datetime.datetime.strptime(request.query_params['start_date'], "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(request.query_params['end_date'], "%Y-%m-%d").date()

            events = UserEvents.objects.filter(
                user_id=user.user.id,
                date__gte=start_date,
                date__lte=end_date
            ).order_by('date', 'beginning')

            events_data = [{
                'event': event.event,
                'date': event.date,
                'beginning': event.beginning,
                'end': event.end,
                'description': event.description,
                'is_private': event.is_private,
                'is_pined': event.is_pined,
                'hex_color': event.hex_color
            } for event in events]
            return Response(events_data, content_type='application/json')
        if "create" in request.query_params:
            input_event = InputEvents(
                user_id=user.user.id,
                event=request.query_params['event_name'],
                date=datetime.datetime.strptime(request.query_params['start_date'], "%Y-%m-%d").date(),
                begin_hr=request.query_params['begin_hr'],
                begin_min=request.query_params['begin_min'],
                end_hr=request.query_params['end_hr'],
                end_min=request.query_params['end_min'],
                description=request.query_params['description'],
                is_private=request.query_params['is_private'].lower() == 'true',
                is_pined=request.query_params['is_pinned'].lower() == 'true',
                hex_color="#11be7c",
                repeated_rule=request.query_params['repeat_pattern'],
                repeated_end=datetime.datetime.strptime(request.query_params['end_date'], "%Y-%m-%d").date()
            )
            valid_request, error_message = input_event.create_event()
            if valid_request:
                return Response({"status": "success"}, content_type='application/json', status=status.HTTP_200_OK)
            else:
                return Response({"status": "error", "message": error_message}, content_type='application/json',
                                status=status.HTTP_400_BAD_REQUEST)
        if "delete" in request.query_params:
            input_event = InputEvents(
                user_id=user.user.id,
                event=request.query_params['event_name'],
                date=datetime.datetime.strptime(request.query_params['date'], "%Y-%m-%d").date(),
                begin_hr=request.query_params['begin_hr'],
                begin_min=request.query_params['begin_min'],
                end_hr=request.query_params['end_hr'],
                end_min=request.query_params['end_min'],
            )
            valid_request, error_message = input_event.delete_event()
            if valid_request:
                return Response({"status": "success"}, content_type='application/json', status=status.HTTP_200_OK)
            else:
                return Response({"status": "error", "message": error_message}, content_type='application/json',
                                status=status.HTTP_400_BAD_REQUEST)
        data = {"username": user.extra_data}
        return Response(data)

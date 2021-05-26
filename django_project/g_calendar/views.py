import requests

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages

from datetime import date, timedelta

from google_auth_oauthlib.flow import InstalledAppFlow
from github import Github

from .db.config import db
from .main.app_logic import g_service as srv
from .main.app_logic import generate_timeMin_timeMax, get_events_from_calendar, CALENDAR_ID, \
    generate_today_available_hours, generate_tomorrow_available_hours, build_event, get_access_token, \
    get_user_info
from .main.email_sender import send_confirmation
from .github.config import gh_client_id, gh_client_secret

# Create your views here.


def home(request):
    request.session.clear()

    context = {
        'title': 'Home',
    }
    return render(request, 'g_calendar/home.html', context)


def calendar(request):
    request.session.clear()

    service = srv

    today = 'today'
    time_min, time_max = generate_timeMin_timeMax(today)
    events_today = get_events_from_calendar(service, CALENDAR_ID, time_min, time_max)
    available_hours = generate_today_available_hours(events_today)

    today = str(date.today())

    tomorrow = 'tomorrow'
    time_min_2, time_max_2 = generate_timeMin_timeMax(tomorrow)
    events_tomorrow = get_events_from_calendar(service, CALENDAR_ID, time_min_2, time_max_2)
    available_hours_2 = generate_tomorrow_available_hours(events_tomorrow)

    tomorrow = str(date.today() + timedelta(days=1))

    context = {
        'title': 'Calendar',
        'available_hours': available_hours,
        'available_hours_2': available_hours_2,
        'today': today,
        'tomorrow': tomorrow
    }

    return render(request, 'g_calendar/calendar.html', context)


def event(request):
    service = srv

    event_date = request.session['event_date']
    event_time = request.session['event_time']

    if 'login' in request.session:
        name = request.session['login']
    else:
        name = 'Enter your name here.'

    if 'email' in request.session:
        email = request.session['email']
    else:
        email = 'Enter your email here.'

    if request.method == 'POST':
        name = request.POST['name']
        mail = request.POST['email']
        title = request.POST['m_title']

        new_event = build_event(name, mail, title, event_time, event_date)

        if 'gmail' in mail:
            add_event = service.events().insert(calendarId=CALENDAR_ID, body=new_event, sendUpdates="all",
                                                conferenceDataVersion=1).execute()
        else:
            add_event = service.events().insert(calendarId=CALENDAR_ID, body=new_event,
                                                conferenceDataVersion=1).execute()

        send_confirmation(mail, title, event_date, event_time)

        db_event_body = {
            'recipient': name,
            'recipient_mail': mail,
            'title': title,
            'event_date': event_date,
            'event_time': event_time,
            'event_datetime': event_date + ' ' + event_time
        }

        checkbox_data = request.POST.get('remind', None)
        if checkbox_data:
            db_event_body['reminded'] = False
        else:
            db_event_body['reminded'] = True

        db.calendar.events.insert_one(db_event_body)

        request.session.clear()

        return redirect('calendar')

    context = {
        'title': 'Make an appointment',
        'e_date': event_date,
        'e_time': event_time,
        'name': name,
        'email': email,
        'client_id': gh_client_id
    }

    return render(request, 'g_calendar/event.html', context)


def login(request, event_date, event_time):
    request.session['event_date'] = event_date
    request.session['event_time'] = event_time

    return render(request, 'g_calendar/login.html')


def login_with_github(request):
    url = f"https://github.com/login/oauth/authorize?scope=read:user&client_id={gh_client_id}"
    return redirect(url)


def github_authorized(request):
    if 'event_date' not in request.session:
        messages.error(request, 'Sorry, something went wrong. Please try again.')
        return redirect('calendar')

    if 'event_time' not in request.session:
        messages.error(request, 'Sorry, something went wrong. Please try again.')
        return redirect('calendar')

    request.session['code'] = request.GET.get('code', '')
    messages.success(request, 'Thank you for logging with GitHub')
    url = f'https://github.com/login/oauth/access_token?client_id={gh_client_id}&client_secret={gh_client_secret}' \
          f'&code={request.session["code"]}'
    response = requests.get(url, allow_redirects=True)
    response_in_str = str(response.content, 'utf-8')
    access_token = get_access_token(response_in_str)
    github = Github(access_token)
    user = github.get_user()
    request.session['login'] = user.login
    if user.email:
        request.session['email'] = user.email
    request.session.pop('code')

    return redirect('event')


def login_with_google(request):
    if 'event_date' not in request.session:
        messages.error(request, 'Sorry, something went wrong. Please try again.')
        return redirect('calendar')

    if 'event_time' not in request.session:
        messages.error(request, 'Sorry, something went wrong. Please try again.')
        return redirect('calendar')

    scopes = 'https://www.googleapis.com/auth/userinfo.email openid'
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes=scopes)
    credentials = flow.run_local_server(port=0)

    user_info = get_user_info(credentials)
    user_email = user_info['email']
    request.session['email'] = user_email

    messages.success(request, 'Thank you for logging with Google')

    return redirect('event')

# views.py
from django.http import HttpResponseRedirect
from django.views import View
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from rest_framework.response import Response
from rest_framework.views import APIView
from .config import CLIENT_SECRET_PATH

CLIENT_SECRET_FILE = CLIENT_SECRET_PATH
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'


class GoogleCalendarInitView(View):
    def get(self, request):
        flow = Flow.from_client_secrets_file(CLIENT_SECRET_FILE, scopes=SCOPES)
        flow.redirect_uri = request.build_absolute_uri(
            '/rest/v1/calendar/redirect/')
        authorization_url, state = flow.authorization_url(
            access_type='offline', include_granted_scopes='true')
        request.session['oauth_state'] = state
        return HttpResponseRedirect(authorization_url)


class GoogleCalendarRedirectView(APIView):
    def get(self, request):
        state = request.session.pop('oauth_state', '')
        flow = Flow.from_client_secrets_file(CLIENT_SECRET_FILE,
                                             scopes=SCOPES,
                                             state=state)
        flow.redirect_uri = request.build_absolute_uri(
            '/rest/v1/calendar/redirect/')
        authorization_response = request.build_absolute_uri()
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        service = build(API_SERVICE_NAME,
                        API_VERSION,
                        credentials=credentials,
                        static_discovery=False)
        events_result = service.events().list(calendarId='primary',
                                              maxResults=10).execute()
        events = events_result.get('items', [])
        return Response(events)

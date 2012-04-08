# Create your views here.
from django.http import HttpResponse


def feature_under_maintenance(request):
    html = u'''
<html>
<body>
<h1>301: This feature is under maintenance. We apologize for the inconvenience.</h1>
</body>
</html>
'''
    return HttpResponse(html, status=301)


def feature_is_no_longer_available(request):
    html = u'''
<html>
<body>
<h1>301: This feature is no longer available.</h1>
</body>
</html>
'''
    return HttpResponse(html, status=301)

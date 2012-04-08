# -*- coding: utf-8 -*-
from django.core import urlresolvers
from django.core.exceptions import ImproperlyConfigured

from intruder.models import IntruderRule, UrlIntruderRule, ViewIntruderRule


class IntruderMiddleware(object):
    def process_rule(self, request, rule):
        if not rule:
            return # if there is no rules to this path, Django-Intruder do nothing.

        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "Django-Intruder requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the IntruderMiddleware class.")

        if rule.super_user_can_ignore_this_rule and request.user.is_superuser:
            return # user has permission to ignore this rule
        if rule.user_with_permission_can_ignore_this_rule and request.user.has_perm(IntruderRule.PERMISSION_KEY):
            return # user has permission to ignore this rule
        try:
            return urlresolvers.get_callable(rule.redirect_view)(request)
        except:
            # it the view is no longer invalid (text injection or deprecated view), the intruder rule will be ignore
            return

    def process_request(self, request):
        try:
            if request.path_info.startswith('/admin'):
                return None
            rule = UrlIntruderRule.objects.get_first_rule_that_matches_this_url(request.path_info)
            return self.process_rule(request, rule)
        except:
            # If any error occur in the middleware, it will be ignored and the original view will be processed normally.
            return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            if request.path_info.startswith('/admin'):
                return None
            view_name = '%s.%s' % (view_func.__module__, view_func.__name__) # view_func.func_name has problems
            rule = ViewIntruderRule.objects.get_first_rule_that_matches_this_view_name(view_name)
            return self.process_rule(request, rule)
        except:
            # If any error occur in the middleware, it will be ignored and the original view will be processed normally.
            return None

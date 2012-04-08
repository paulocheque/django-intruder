# -*- coding: utf-8 -*-
import re

from django.core.cache import cache
from django.db import models
from django.utils.datastructures import SortedDict


class IntruderRule(models.Model):
    PERMISSION_KEY = u'intruder.can_use_this_feature'

    redirect_view = models.CharField(max_length=255, default='intruder.views.feature_under_maintenance',
                                     help_text='If the view no longer exist, this rule will be ignored.')

    # Who can ignore this rule
    super_user_can_ignore_this_rule = models.BooleanField(default=True)
    user_with_permission_can_ignore_this_rule = models.BooleanField(default=True,
                                    help_text='Permission name: intruder | intruder rule | can_use_this_feature')

    class Meta:
        permissions = ((u'can_use_this_feature', u'Can use this feature'),)
        abstract = True

    def save(self, **kwargs):
        super(IntruderRule, self).save(**kwargs)
        self.__class__.objects.clear_cache()

    def delete(self, **kwargs):
        super(IntruderRule, self).delete(**kwargs)
        self.__class__.objects.clear_cache()


class ViewIntruderRuleManager(models.Manager):
    CACHE_KEY = 'ViewIntruderRules'

    def cached_rules(self):
        rules = cache.get(ViewIntruderRuleManager.CACHE_KEY)
        if rules is None:
            rules = self.all()
            cache.set(ViewIntruderRuleManager.CACHE_KEY, rules)
        return SortedDict([(rule.view_name, rule) for rule in rules])

    def clear_cache(self):
        """
        QuerySet.delete() or QuerySet.update() will not clear the cache. 
        Thus you must call this method by yourself. 
        Examples of QuerySets:
        - ViewIntruderRuleManager.objects.all().delete()
        - ViewIntruderRuleManager.objects.all().update(...)
        """
        cache.delete(ViewIntruderRuleManager.CACHE_KEY)

    def get_first_rule_that_matches_this_view_name(self, view_name):
        try:
            return self.cached_rules()[view_name]
        except KeyError:
            pass


class ViewIntruderRule(IntruderRule):
    # https://docs.djangoproject.com/en/dev/ref/databases/
    # Using max_length=255 to avoid problems with MySQL
    view_name = models.CharField(max_length=255, unique=True, db_index=True,
                                 help_text='Must be a valid view path (app_name.views.view_name). Examples: myapp.views.a_bugged_view')

    objects = ViewIntruderRuleManager()

    def __unicode__(self):
        return '%s => %s' % (self.view_name, self.redirect_view)


class UrlIntruderRuleManager(models.Manager):
    CACHE_KEY = 'UrlIntruderRules'

    def cached_rules(self):
        rules = cache.get(UrlIntruderRuleManager.CACHE_KEY)
        if rules is None:
            rules = self.all()
            cache.set(UrlIntruderRuleManager.CACHE_KEY, rules)
        return SortedDict([(rule.url_pattern, rule) for rule in rules])

    def clear_cache(self):
        """
        QuerySet.delete() or QuerySet.update() will not clear the cache. 
        Thus you must call this method by yourself. 
        Examples of QuerySets:
        - UrlIntruderRuleManager.objects.all().delete()
        - UrlIntruderRuleManager.objects.all().update(...)
        """
        cache.delete(UrlIntruderRuleManager.CACHE_KEY)

    def get_first_rule_that_matches_this_url(self, path):
        rules = self.cached_rules().values()
        for rule in rules:
            if re.match(rule.url_pattern, path):
                return rule


class UrlIntruderRule(IntruderRule):
    # https://docs.djangoproject.com/en/dev/ref/databases/
    # Using max_length=255 to avoid problems with MySQL
    url_pattern = models.CharField(max_length=255, unique=True, db_index=True,
                                   help_text='Example: /myapp')

    objects = UrlIntruderRuleManager()

    def __unicode__(self):
        return '%s => %s' % (self.url_pattern, self.redirect_view)

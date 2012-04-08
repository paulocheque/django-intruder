# -*- coding: utf-8 -*-
from django.test import TestCase
from django_dynamic_fixture import get
from django_dynamic_fixture.ddf import BadDataError

from intruder.models import IntruderRule, ViewIntruderRule, UrlIntruderRule


class ViewIntruderRuleTest(TestCase):

    def test_view_name_is_required_and_must_be_unique(self):
        self.assertRaises(BadDataError, get, ViewIntruderRule, view_name=None)
        get(ViewIntruderRule, view_name='x')
        self.assertRaises(BadDataError, get, ViewIntruderRule, view_name='x')


class ViewIntruderRuleManagerTest(TestCase):

    def setUp(self):
        ViewIntruderRule.objects.clear_cache()

    def test_get_first_rule_that_matches_this_view_name_must_return_None_if_not_found(self):
        self.assertEquals(None, ViewIntruderRule.objects.get_first_rule_that_matches_this_view_name('x'))

    def test_get_first_rule_that_matches_this_view_name(self):
        rule = get(ViewIntruderRule, view_name='example.views.view_a')

        self.assertEquals(rule, ViewIntruderRule.objects.get_first_rule_that_matches_this_view_name('example.views.view_a'))


class UrlIntruderRuleManagerTest(TestCase):

    def setUp(self):
        UrlIntruderRule.objects.clear_cache()

    def test_get_first_rule_that_matches_this_url_must_return_None_if_no_rules_matches_the_url(self):
        self.assertEquals(None, UrlIntruderRule.objects.get_first_rule_that_matches_this_url('x'))

    def test_get_first_rule_that_matches_this_url(self):
        rule = get(UrlIntruderRule, url_pattern='/myapp')
        get(UrlIntruderRule, url_pattern='/myapp/mymodel')

        self.assertEquals(rule, UrlIntruderRule.objects.get_first_rule_that_matches_this_url('/myapp/mymodel/1'))

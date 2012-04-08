# -*- coding: utf-8 -*-

from django.test import TestCase
from intruder.admin import ViewIntruderRuleAdminForm, UrlIntruderRuleAdminForm


class ViewIntruderRuleAdminFormTest(TestCase):

    def test_success_case(self):
        form = ViewIntruderRuleAdminForm({'view_name': 'example.views.view_a',
                                          'redirect_view_1': 'example.views.view_b'})
        self.assertEquals(True, form.is_valid(), msg=form.errors)

    def test_view_name_must_be_valid(self):
        form = ViewIntruderRuleAdminForm({'view_name': 'example.views.inexistent_view',
                                          'redirect_view': 'example.views.view_b'})
        self.assertEquals(False, form.is_valid())

    def test_view_name_must_not_be_an_intruder_view(self):
        form = ViewIntruderRuleAdminForm({'view_name': 'intruder.views.feature_under_maintenance',
                                          'redirect_view': 'example.views.view_b'})
        self.assertEquals(False, form.is_valid())

    def test_view_name_must_not_be_the_same_as_the_redirect_view(self): # it does not make sense
        form = ViewIntruderRuleAdminForm({'view_name': 'example.views.view_a',
                                          'redirect_view': 'example.views.view_a'})
        self.assertEquals(False, form.is_valid())

    def test_redirect_view_must_be_valid(self):
        form = ViewIntruderRuleAdminForm({'view_name': 'example.views.view_a',
                                          'redirect_view': 'example.views.inexistent_view'})
        self.assertEquals(False, form.is_valid())


class UrlIntruderRuleAdminFormTest(TestCase):

    def test_success_case(self):
        form = UrlIntruderRuleAdminForm({'url_pattern': '/x',
                                         'redirect_view_1': 'example.views.view_b'})
        self.assertEquals(True, form.is_valid())

    def test_redirect_view_must_be_valid(self):
        form = UrlIntruderRuleAdminForm({'url_pattern': '',
                                      'view_name': 'example.views.view_a',
                                      'redirect_view': 'example.views.inexistent_view'})
        self.assertEquals(False, form.is_valid())

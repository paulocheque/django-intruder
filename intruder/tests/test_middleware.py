# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import Permission, User
from django_dynamic_fixture import get
from intruder.models import ViewIntruderRule, UrlIntruderRule


URL_A = '/example/view-a'
VIEW_A = 'example.views.view_a'
VIEW_A_RESULT = 'OK: A'

URL_B = '/example/view-b'
VIEW_B = 'example.views.view_b'
VIEW_B_RESULT = 'OK: B'


def create_user(is_superuser):
    user = get(User, is_active=True, is_superuser=is_superuser)
    user.set_password('x')
    user.save()
    user.password = 'x' # raw password: hack for test simplicity
    return user


class CommonUserIntruderMiddlewareTest(TestCase):

    def setUp(self):
        ViewIntruderRule.objects.clear_cache()
        UrlIntruderRule.objects.clear_cache()
        user = create_user(is_superuser=False)
        self.client = Client()
        assert self.client.login(username=user.username, password=user.password)

    def test_common_user_can_see_a_page_without_intruder_rules(self):
        response = self.client.get(URL_A)
        self.assertEquals(VIEW_A_RESULT, response.content)

    def test_common_user_can_not_see_a_page_with_intruder_rules(self):
        get(UrlIntruderRule, url_pattern=URL_A, redirect_view=VIEW_B)
        response = self.client.get(URL_A)
        self.assertEquals(VIEW_B_RESULT, response.content)

    def test_common_user_can_not_see_a_page_with_view_intruder_rules(self):
        get(ViewIntruderRule, view_name=VIEW_A, redirect_view=VIEW_B)
        response = self.client.get(URL_A)
        self.assertEquals(VIEW_B_RESULT, response.content)


class SuperUserIntruderMiddlewareTest(TestCase):

    def setUp(self):
        ViewIntruderRule.objects.clear_cache()
        UrlIntruderRule.objects.clear_cache()
        user = create_user(is_superuser=True)
        self.client = Client()
        assert self.client.login(username=user.username, password=user.password)

    def test_super_user_can_see_a_page_without_intruder_rules(self):
        response = self.client.get(URL_A)
        self.assertEquals(VIEW_A_RESULT, response.content)

    def test_super_user_can_see_a_page_with_intruder_rules_if_this_was_activated(self):
        get(UrlIntruderRule, url_pattern=URL_A,
            super_user_can_ignore_this_rule=True,
            user_with_permission_can_ignore_this_rule=False)
        response = self.client.get(URL_A)
        self.assertEquals(VIEW_A_RESULT, response.content)

    def test_super_user_can_see_a_page_with_view_intruder_rules_if_this_was_activated(self):
        get(ViewIntruderRule, view_name=VIEW_A,
            super_user_can_ignore_this_rule=True,
            user_with_permission_can_ignore_this_rule=False)
        response = self.client.get(URL_A)
        self.assertEquals(VIEW_A_RESULT, response.content)

    def test_super_user_can_not_see_a_page_with_intruder_rules_if_this_was_not_activated(self):
        get(UrlIntruderRule, url_pattern=URL_A, redirect_view=VIEW_B,
            super_user_can_ignore_this_rule=False,
            user_with_permission_can_ignore_this_rule=False)
        response = self.client.get(URL_A)
        self.assertEquals(VIEW_B_RESULT, response.content)

    def test_super_user_can_not_see_a_page_with_view_intruder_rules_if_this_was_not_activated(self):
        get(ViewIntruderRule, view_name=VIEW_A, redirect_view=VIEW_B,
            super_user_can_ignore_this_rule=False,
            user_with_permission_can_ignore_this_rule=False)
        response = self.client.get(URL_A)
        self.assertEquals(VIEW_B_RESULT, response.content)


class SpecialUserIntruderMiddlewareTest(TestCase):

    def setUp(self):
        ViewIntruderRule.objects.clear_cache()
        UrlIntruderRule.objects.clear_cache()
        user = create_user(is_superuser=False)
        user.user_permissions.add(Permission.objects.filter(codename='can_use_this_feature')[0])
        self.client = Client()
        assert self.client.login(username=user.username, password=user.password)

    def test_special_user_can_see_a_page_without_intruder_rules(self):
        response = self.client.get(URL_A)
        self.assertEquals(VIEW_A_RESULT, response.content)

    def test_special_user_can_see_a_page_with_intruder_rules_if_this_was_activated(self):
        get(UrlIntruderRule, url_pattern=URL_A,
            super_user_can_ignore_this_rule=False,
            user_with_permission_can_ignore_this_rule=True)
        response = self.client.get(URL_A)
        self.assertEquals(VIEW_A_RESULT, response.content)

    def test_special_user_can_see_a_page_with_view_intruder_rules_if_this_was_activated(self):
        get(ViewIntruderRule, view_name=VIEW_A,
            super_user_can_ignore_this_rule=False,
            user_with_permission_can_ignore_this_rule=True)
        response = self.client.get(URL_A)
        self.assertEquals(VIEW_A_RESULT, response.content)

    def test_special_user_can_not_see_a_page_with_intruder_rules_if_this_was_not_activated(self):
        get(UrlIntruderRule, url_pattern=URL_A, redirect_view=VIEW_B,
            super_user_can_ignore_this_rule=False,
            user_with_permission_can_ignore_this_rule=False)
        response = self.client.get(URL_A)
        self.assertEquals(VIEW_B_RESULT, response.content)

    def test_special_user_can_not_see_a_page_with_view_intruder_rules_if_this_was_not_activated(self):
        get(ViewIntruderRule, view_name=VIEW_A, redirect_view=VIEW_B,
            super_user_can_ignore_this_rule=False,
            user_with_permission_can_ignore_this_rule=False)
        response = self.client.get(URL_A)
        self.assertEquals(VIEW_B_RESULT, response.content)


class OtherScenariosIntruderMiddlewareTest(TestCase):

    def setUp(self):
        ViewIntruderRule.objects.clear_cache()
        UrlIntruderRule.objects.clear_cache()
        user = create_user(is_superuser=False)
        self.client = Client()
        assert self.client.login(username=user.username, password=user.password)

    def test_rule_will_be_ignored_if_the_rediret_view_is_invalid_or_inexistent(self):
        get(UrlIntruderRule, url_pattern=URL_A, redirect_view='invalid view name')
        response = self.client.get(URL_A)
        self.assertEquals(VIEW_A_RESULT, response.content)

    def test_admin_interface_must_ignore_all_rules(self):
        get(UrlIntruderRule, url_pattern='/admin', redirect_view=VIEW_B)
        response = self.client.get('/admin/')
        self.assertNotEquals(VIEW_B_RESULT, response.content)

    # TODO: redirect view must have only the request parameter!?

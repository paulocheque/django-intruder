# -*- coding: utf-8 -*-
from django.contrib import admin
from django.conf import settings
from django import forms
from django.forms import widgets
from django.utils.safestring import mark_safe

from intruder.models import UrlIntruderRule, ViewIntruderRule

#Useful for development
#from django.conf import settings
#if settings.DEBUG: # precaution
#    from django.contrib.auth.models import Permission
#    admin.site.register(Permission)


class ViewSelectorWidget(widgets.MultiWidget):
    INTRUDER_VIEWS = (('', '-----'),
                      ('intruder.views.feature_under_maintenance', 'Feature under maintenance'),
                      ('intruder.views.feature_is_no_longer_available', 'Feature is no longer available'))

    def __init__(self, attrs=None):
        choices = settings.INTRUDER_DEFAULT_REDIRECT_VIEWS if hasattr(settings, 'INTRUDER_DEFAULT_REDIRECT_VIEWS') else self.INTRUDER_VIEWS
        widgets = [forms.Select(choices=choices), forms.TextInput]
        super(ViewSelectorWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            for choice in self.widgets[0].choices:
                if choice[0] == value:
                    return [value, '']
            return ['', value]
        return ['', '']

    def format_output(self, rendered_widgets):
        # TODO: need a smart way to do this.
        x = rendered_widgets[1].replace('type=', mark_safe(' class="vTextField" max_length="300" type='))
        return u'%s<span> or </span>%s' % (rendered_widgets[0], x)


class FlexibleChoiceField(forms.ChoiceField):
    def validate(self, value):
        pass # we do not want to valid choices


class ViewSelectorField(forms.MultiValueField):
    widget = ViewSelectorWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.CharField(min_length=2, max_length=300),
            FlexibleChoiceField(),
        )
        super(ViewSelectorField, self).__init__(fields, required=False, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            if data_list[1]:
                return data_list[1][0:300]
            else:
                return data_list[0]
        return ''


class IntruderRuleAdminForm(forms.ModelForm):
    redirect_view = ViewSelectorField()

    def validate_view_path_exists(self, lookup_view):
        from django.core import urlresolvers
        try:
            lookup_view = lookup_view.encode('ascii')
            mod_name, func_name = urlresolvers.get_mod_func(lookup_view)
            lookup_view = getattr(urlresolvers.import_module(mod_name), func_name)
            if not callable(lookup_view):
                raise forms.ValidationError("'%s.%s' is not a callable." % (mod_name, func_name))
        except ImportError as e:
            mod_name, _ = urlresolvers.get_mod_func(lookup_view)
            raise forms.ValidationError("Could not import %s. Error was: %s" % (mod_name, str(e)))
        except AttributeError as e:
            mod_name, func_name = urlresolvers.get_mod_func(lookup_view)
            raise forms.ValidationError("Tried %s in module %s. Error was: %s" % (func_name, mod_name, str(e)))
        except Exception as e:
            raise forms.ValidationError("Invalid lookup_view %s. Error was: %s" % (lookup_view, str(e)))


    def clean_redirect_view(self):
        self.validate_view_path_exists(self.cleaned_data['redirect_view'])
        return self.cleaned_data['redirect_view']


class ViewIntruderRuleAdminForm(IntruderRuleAdminForm):
    class Meta:
        model = ViewIntruderRule

    def can_not_set_an_intruder_view(self, lookup_view):
        if lookup_view.startswith('intruder.views'):
            raise forms.ValidationError('Can not select an Intruder\'s view')

    def clean_view_name(self):
        self.validate_view_path_exists(self.cleaned_data['view_name'])
        self.can_not_set_an_intruder_view(self.cleaned_data['view_name'])
        return self.cleaned_data['view_name']

    def clean(self):
        # if there is a validation error in the view_name, it would raise an KeyError
        if 'view_name' in self.cleaned_data and 'redirect_view' in self.cleaned_data and \
            self.cleaned_data['view_name'] == self.cleaned_data['redirect_view']:
            raise forms.ValidationError('Redirect view is equal to the selected view.')
        return self.cleaned_data


class UrlIntruderRuleAdminForm(IntruderRuleAdminForm):
    class Meta:
        model = UrlIntruderRule


def clean_cache(modeladmin, request, queryset):
    modeladmin.form._meta.model.objects.clear_cache()
clean_cache.short_description = "Clear Intruder cache"


class ViewIntruderRuleAdmin(admin.ModelAdmin):
    form = ViewIntruderRuleAdminForm
    actions = [clean_cache]

    list_display = ('id', 'view_name', 'redirect_view', 'super_user_can_ignore_this_rule', 'user_with_permission_can_ignore_this_rule')
    list_filter = ('super_user_can_ignore_this_rule', 'user_with_permission_can_ignore_this_rule',)
    ordering = ('view_name',)
    search_fields = ('view_name',)


class UrlIntruderRuleAdmin(admin.ModelAdmin):
    form = UrlIntruderRuleAdminForm
    actions = [clean_cache]

    list_display = ('id', 'url_pattern', 'redirect_view', 'super_user_can_ignore_this_rule', 'user_with_permission_can_ignore_this_rule')
    list_filter = ('super_user_can_ignore_this_rule', 'user_with_permission_can_ignore_this_rule',)
    ordering = ('url_pattern',)
    search_fields = ('url_pattern',)


admin.site.register(ViewIntruderRule, ViewIntruderRuleAdmin)
admin.site.register(UrlIntruderRule, UrlIntruderRuleAdmin)

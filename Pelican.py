
import sublime, sublime_plugin
import re

import datetime

pelican_slug_template = {
    "md": "slug: %s\n",
    "rst": ":slug: %s\n",
}

def strDateNow():
    now = datetime.datetime.now()
    return datetime.datetime.strftime(now, "%Y-%m-%d %H:%M:%S")

class PelicanSetting():
    _singleton_instance = None

    def __new__(cls):
        if not cls._singleton_instance:
            cls._singleton_instance = super(PelicanSetting, cls).__new__()
        return cls._singleton_instance

    def __init__(self):
        self.global_settings = sublime.load_settings(__name__ + '.sublime-settings')

    def load_setting(self, view, setting_name, default_value):
        if len(setting_name) < 1:
            if default_value:
                return default_value
            else:
                return None

        return view.settings().get(setting_name, self.global_settings.get(setting_name, default_value))

class PelicanGenerateSlugCommand(sublime_plugin.TextCommand):
    def slugify(self, value):
        """
        Normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens.

        Took from django sources.
        """
        value = re.sub('[^\w\s-]', '', value).strip().lower()
        value = re.sub('[-\s]+', '-', value)
        # we want only ASCII chars
        value = value.encode('ascii', 'ignore')
        # but Pelican should generally use only unicode
        return value.decode('ascii')

    def run(self, edit):
        slug_region = self.view.find(':?slug:.+\s*', 0, sublime.IGNORECASE)
        if slug_region > -1:
            self.view.erase(edit, slug_region)

        title_region = self.view.find(':?title:.+\s*', 0, sublime.IGNORECASE)
        if title_region > -1:
            orig_title_str = self.view.substr(title_region).strip()

            regex = re.compile(":?title:(?P<title>.+)\s*",re.IGNORECASE)
            r = regex.search(orig_title_str)
            if not r:
                return

            title_str = r.groupdict()['title'].strip()

            slug = self.slugify(title_str)

            if re.search(":title:", orig_title_str, re.IGNORECASE):
                meta_type = "rst"
            else: # "title: ..."
                meta_type = "md"

            slug_insert_position = title_region.end()
            self.view.insert(edit, slug_insert_position, pelican_slug_template[meta_type] % slug)


class PelicanAutogenSlug(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        auto_generate_slug_on_save = pelican_setting.load_setting(view, "auto_generate_slug_on_save", True)
        if not auto_generate_slug_on_save:
            return

        filepath_filter = pelican_setting.load_setting(view, "filepath_filter", '*')
        if not re.search(filepath_filter, view.file_name()):
            return

        if view.find(':?slug:\s*\w+', 0, sublime.IGNORECASE) > -1:
            force_slug_regeneration_on_save = pelican_setting.load_setting(view, "force_slug_regeneration_on_save", False)
            if not force_slug_regeneration_on_save:
                return

        view.run_command('pelican_generate_slug' )

class PelicanNewMarkdownCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        pelican_setting = PelicanSetting()
        pelican_meta_template = pelican_setting.load_setting(self.view, "pelican_meta_template", {})
        if len(pelican_meta_template) < 1:
            return
        for key, value in pelican_meta_template.iteritems():
            pelican_meta_template[key] = "\n".join(value)

        new_view = self.view.window().new_file()
        new_view.insert(edit, 0, pelican_meta_template["md"] % {"date": strDateNow()})

class PelicanNewRestructuredtextCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        pelican_setting = PelicanSetting()
        pelican_meta_template = pelican_setting.load_setting(self.view, "pelican_meta_template", {})
        if len(pelican_meta_template) < 1:
            return
        for key, value in pelican_meta_template.iteritems():
            pelican_meta_template[key] = "\n".join(value)

        new_view = self.view.window().new_file()
        new_view.insert(edit, 0, pelican_meta_template["rst"] % {"date": strDateNow()})

class PelicanInsertMarkdownCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        pelican_setting = PelicanSetting()
        pelican_meta_template = pelican_setting.load_setting(self.view, "pelican_meta_template", {})
        if len(pelican_meta_template) < 1:
            return
        for key, value in pelican_meta_template.iteritems():
            pelican_meta_template[key] = "\n".join(value)

        self.view.insert(edit, 0, pelican_meta_template["md"] % {"date": strDateNow()})


class PelicanInsertRestructuredtextCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        pelican_setting = PelicanSetting()
        pelican_meta_template = pelican_setting.load_setting(self.view, "pelican_meta_template", {})
        if len(pelican_meta_template) < 1:
            return
        for key, value in pelican_meta_template.iteritems():
            pelican_meta_template[key] = "\n".join(value)

        self.view.insert(edit, 0, pelican_meta_template["rst"] % {"date": strDateNow()})

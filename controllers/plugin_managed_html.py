# -*- coding: utf-8 -*-
#from plugin_bootstrap import Messaging
from plugin_managed_html import ManagedHTML
from gluon.storage import Storage

### setup core objects #########################################################
managed_html = ManagedHTML(globals(), db)
managed_html.settings.table_content_name = 'plugin_managed_html_content'
managed_html.settings.table_file_name = 'plugin_managed_html_file'
managed_html.settings.extra_fields = {
    'plugin_managed_html_content': [
        Field('created_on', 'datetime', default=request.now, 
              readable=False, writable=False)],
    'plugin_managed_html_file': [
        Field('created_on', 'datetime', default=request.now, 
              readable=False, writable=False)],
}

### define tables ##############################################################
managed_html.define_tables()
table_content = managed_html.settings.table_content
table_file = managed_html.settings.table_file

### populate records ###########################################################
import datetime
if db(table_content.created_on<request.now-datetime.timedelta(minutes=60)).count():
    table_content.truncate()
    table_file.truncate()
    session.flash = 'the database has been refreshed'
    redirect(URL('index'))

### managed_html detail settings ###############################################

managed_html.settings.home_url = URL('web2py_plugins', 'index')
managed_html.settings.home_label = 'Web2py plugins'
managed_html.switch_mode()
    
### demo functions #############################################################


def index():
    return dict(page1=A('page1', _href=managed_html.edit_url('page1')),
                page2=A('page2', _href=managed_html.edit_url('page2')))
    
def page1():
    response.view = 'plugin_managed_html/page1.html'
    return dict(managed_html=managed_html, URL=managed_html.url, ORIGINAL_URL=URL)
                
def page2():
    response.view = 'plugin_managed_html/page2.html'
    return dict(managed_html=managed_html, URL=managed_html.url, ORIGINAL_URL=URL)
    
def download():
    return response.download(request, db)

    
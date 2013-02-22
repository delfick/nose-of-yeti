import os

def moreContext(app, pagename, templatename, context, doctree):
    def p(url):
        parts = pagename.split('/')[:-1]
        if len(parts) == 0:
            return url[1:]
        return os.path.relpath(url, '/%s' % '/'.join(parts))

    context['toplinks'] = [
          ('Overview', p('/index.html')    , pagename=='index')
        , ('Examples', p('/examples.html') , pagename=='examples')
        , ('Usage',    p('/usage.html')    , pagename=='usage')
        , ('Features', p('/features.html') , pagename=='features')
        , ('Dev',      p('/dev/index.html'), pagename.startswith('dev'))
        ]

def setup(app):
    app.connect("html-page-context", moreContext)


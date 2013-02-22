from sphinx.util.compat import Directive
from docutils import nodes

from noseOfYeti.plugins.support.spec_options import spec_options

class SpecOptionsDirective(Directive):
    has_content = True

    def run(self):
        # Create bullet list
        bullet = nodes.bullet_list()

        # Determine what to put in the list
        # sort items alphabetically and by length
        items = [(name, options['help']) for name, options in spec_options.items()]
        items.sort()
        items.sort(cmp=lambda a, b: len(a[0]) - len(b[0]))

        # Put items in the list
        for name, options in items:
            item = nodes.emphasis()
            item += nodes.Text(name)
            item += nodes.Text(": %s" % options)

            list_item = nodes.list_item()
            list_item += item
            bullet.append(list_item)

        return [bullet]

def setup(app):
    app.add_directive('spec_options', SpecOptionsDirective)


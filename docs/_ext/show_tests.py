from docutils.nodes import fully_normalize_name as normalize_name
from sphinx.directives.code import LiteralInclude
from sphinx.util.compat import Directive
from pinocchio.spec import testName
from docutils import nodes
import inspect
import os

class ShowTestsDirective(Directive):
    """Directive for outputting all the specs found in noseOfYeti/specs"""
    has_content = True

    def run(self):
        """For each file in noseOfYeti/specs, output nodes to represent each spec file"""
        env = self.env = self.state.document.settings.env
        specdir = os.path.join(env.srcdir, '../noseOfYeti/specs')
        files = [f for f in os.listdir(specdir) if f.endswith('_test.py')]
        tokens = []
        for f in files:
            name = str(f[:-3])
            module = getattr(__import__('noseOfYeti.specs', globals(), locals(), [name], -1), name)

            section = nodes.section()
            name = normalize_name(f)
            section['names'].append(name)
            section['ids'].append(name)

            header = nodes.title()
            header += nodes.Text(f)
            section.append(header)

            section.extend(self.nodes_for_module(module))
            tokens.append(section)

        return tokens

    def nodes_for_module(self, module):
        """
            Determine nodes for a module/class
            Taking into account nested modules
        """
        info = {}
        nodes = []
        tests = []
        groups = []
        support = []

        for name in dir(module):
            if name.startswith("Test"):
                item = getattr(module, name)
                info[name] = (name, item, [])
                if hasattr(item, '__childof__'):
                    spr = item.__childof__.__name__
                else:
                    spr = inspect.getmro(item)[1].__name__

                if spr in info:
                    info[spr][2].append((info[name]))
                else:
                    groups.append(name)

            elif name.startswith("test_"):
                tests.append(name)

            elif name in ('setUp', 'tearDown'):
                support.append(name)

        for name in support:
            item = getattr(module, name)
            if callable(item):
                nodes.extend(self.nodes_for_support(name, item))

        tests.sort()
        tests.sort(cmp = lambda a, b: len(a) - len(b))
        for name in tests:
            item = getattr(module, name)
            if callable(item):
                nodes.extend(self.nodes_for_test(name, item))

        for name in groups:
            _, item, children = info[name]
            if isinstance(item, object):
                nodes.extend(self.nodes_for_class(name, item, children))

        return nodes

    def nodes_for_class(self, name, item, children):
        """
            Determine nodes for a class
            @param name: name of the class
            @param item: The class itself
            @param children: A list of (name, item, children) for all logicallynested classes
        """
        container = nodes.container(classes=["nose_kls"])
        para = nodes.paragraph(classes=["kls_title"])
        name = testName(item)
        para += nodes.Text(name)
        container.append(para)
        subnodes = self.nodes_for_module(item)
        if not subnodes and not children:
            # Probably not a test class
            return []

        container.extend(subnodes)
        for child in children:
            container.extend(self.nodes_for_class(*child))

        return [container]

    def nodes_for_support(self, name, item):
        """
            Determine nodes for a setup/teardown function
            @param name: name of the function
            @param item: The function itself
        """
        container = nodes.container(classes=["has_info", "nose_support"])

        para = nodes.paragraph(classes=["kls_support"])
        para.extend(self.nodes_for_arrow())
        para += nodes.Text(name)

        container.append(para)
        container.append(self.include_source(item))

        return [container]

    def nodes_for_test(self, name, item):
        """
            Determine nodes for a single test function
            @param name: name of the function
            @param item: The function itself
        """
        container = nodes.container(classes=["has_info", "nose_test"])

        para = nodes.paragraph()
        para.extend(self.nodes_for_arrow())

        name = testName(item)
        para += nodes.Text(name)

        container.append(para)
        container.append(self.include_source(item))

        return [container]

    def nodes_for_arrow(self):
        """Create inline for an arrow"""
        arrow = nodes.inline(classes=["arrow", "arrow-closed"])
        return [arrow]

    def include_source(self, item):
        """Return nodes representing the original source code of the item"""
        func = item
        if hasattr(item, 'im_func'):
            func = item.im_func

        try:
            func.func_code
        except:
            from pdb import set_trace; set_trace()
        code = func.func_code
        filename = code.co_filename

        first_line = code.co_firstlineno
        num_lines = inspect.getsource(item).strip().count('\n')
        last_line = first_line + num_lines

        info = nodes.container(classes=["hidden_info"])
        info.extend(self.literalinclude('/%s' % filename, first_line, last_line))
        return info


    def literalinclude(self, filename, first_line, last_line):
        """Use literalinclude directive to return nodes for a literalinclude of specified lines in some file"""
        lines = "%s-%s" % (first_line, last_line)
        lineno = 0
        options = dict(lines=lines)
        content = ":lines: %s" % lines
        arguments = [filename]
        block_text = ""
        content_offset = 0

        directive_instance = LiteralInclude('literalinclude'
            , arguments, options, content, lineno
            , content_offset, block_text, self.state, self.state.state_machine
            )

        return directive_instance.run()

def setup(app):
    """Setup the show_tests directive"""
    app.add_directive('show_tests', ShowTestsDirective)


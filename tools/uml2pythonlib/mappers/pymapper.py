import copy
from encodings.base64_codec import base64_decode
import jinja2

_LOADER = jinja2.DictLoader({})
ENV = jinja2.Environment(loader=_LOADER)

class NoValue(object): pass


def strLappend(iterable, values, indent, append_empty_line):
    if values == None:
        return
    if isinstance(values, basestring):
        values = [ values, ]
    for value in values:
        iterable += [ indent + value, ]
    if append_empty_line:
        iterable += [ '', ]


class AttributeBase(object):
    INDENT = " "*4
    def __repr__(self):
        return "<%s name='%s'>" % (self.__class__.__name__,
                                    self.name)
    @property
    def default(self):
        return self._default

    @default.setter 
    def default(self, value):
        self._default = value

    def __init__(self, name, default=NoValue):
        self.name = name
        self.default = default

    def signature(self):
        tag = "{name}"
        data = { 'name': self.name }
        if self.default is not NoValue:
            data['default'] = self.default
            tag = "{name}={default}"
            if isinstance(self.default, basestring):
                tag = "{name}=\"{default}\""
        return tag.format(**data)

    def initval(self, join=False):
        return "self.{0} = {0}".format(self.name)

    def generate_methods(self):
        return None


class AttributeReference(AttributeBase):
    def signature(self):
        return "{name}=None".format(name=self.name)

    def initval(self, join=False):
        result = []
        result += [ "self._{name} = []".format(name=self.name), ]
        result += [ "self.{name} = [] if {name} is None else {name}".format(name=self.name), ]
        return result if join == False else '\n'.join(result)

    def generate_methods(self):
        if not hasattr(self, "linkto"):
            raise RuntimeError("missing linkto attribute")

        result = """
def get{name}(self):
    \"\"\"The topological nodes at the base voltage.
    \"\"\"
    return self._{name}

def set{name}(self, value):
    for x in self._{name}:
        x.{linkto} = None
    for y in value:
        y._{linkto} = self
    self._{name} = value

{name} = property(get{name}, set{name})
        """.strip().format(name=self.name, linkto=self.linkto)
        return result


class Mapper(object):
    _LOADER.mapping["Mapper"] = """

{% if s.package %}
from {{ s.package }} import {{ s.base }}
{% endif %}

class {{ s.name }}({{ s.base }}):
    {%- if s.doc %}
    \"\"\"{{ s.doc | indent(width=7, indentfirst=False) }}
    \"\"\"
    {% endif %}

    def __init__(self, {{ s.signature + "," if signature else "" -}} *args, **kw_args):
        \"\"\"Initialises a new '{{ s.name }}' instance.
        {% for attr in s.attributes %}
        @param {{ attr.name }}: {{ attr.doc }}
        {%- endfor %}
        \"\"\"

{% for attr in s.attributes %}
{{ attr.initval(True) | indent(width=8, indentfirst=True)}}
{% endfor %}

        super({{name}}, self).__init__(*args, **kw_args)

{% for attr in attributes if attr.generate_methods() != None  %}
{{ attr.generate_methods() | indent(width=8, indentfirst=True) }}
{% endfor %}
"""

    INDENT = " "*4
    def __init__(self, name, base="object", package=None):
        self.name, self.base, self.package = name, base, package
        self._doc = []

        self.attributes = []
        self.initdoc = ""


    @property
    def doc(self):
        return '\n'.join(self._doc)

    @doc.setter
    def doc(self, value):
        if isinstance(value, basestring):
            value = [ value, ]
        self._doc.extend(value)
    
    def append(self, attribute):
        if isinstance(attribute, AttributeReference):
            attribute.linkto = self.name
        self.attributes.append(attribute)    

    def __repr__(self):
        return "<%s name='%s'>" % (self.__class__.__name__,
                                    self.name)
    def signature(self, attributes=None):
        # generate a method signature out of the attributes
        attributes = attributes if attributes else self.attributes

        result = []
        for attr in attributes:
            result.append(attr.signature())
        return ", ".join(result)

    def generate_init(self):
        result = []
        result.append("def __init__(%s):" % self.signature())

        indent = self.INDENT

        # documentation part
        result += [ indent + '"""Initialises a new \'%s\' instance.' % self.name , ]
        result += [ '', ]
        
        for attr in self.attributes:
            result += [ indent + '@param %s: ' % attr.name + getattr(attr, 'doc', ""), ]
        result += [ indent + '"""', ]
        result += [ '', ]
        
        for attr in self.attributes:
            line = attr.initval()
            strLappend(result, line, indent="", append_empty_line=True)
        return [ indent + ln for ln in result ]

    def generate_methods(self):
        result = []
        for attr in self.attributes:
            line = attr.generate_methods(self.name)
            strLappend(result, line, indent=self.INDENT, append_empty_line=True)
        return [ self.INDENT + ln for ln in result ]

    def render(self):
        return ENV.get_template(self.__class__.__name__)\
                .render(s=self)


def _test():
    m = Mapper("BaseVoltage", "IdentifiedObject", "Blha")
    m.classdoc = [ "Initialises a new 'BaseVoltage' instance.", "And move on", ]

    attr = AttributeBase("nominalVoltage")
    attr.default = 1.0
    m.attributes.append(attr)

    attr = AttributeBase("isDC")
    attr.default = False
    m.append(attr)


    attr = AttributeReference("TopologicalNode")
    m.append(attr)

    attr = AttributeReference("ConductingEquipment")
    m.append(attr)


    print m.render()
    import sys; sys.exit(0)
    print "\n".join(m.generate_init())
    print "\n".join(m.generate_methods())

if __name__ == "__main__":
    _test()
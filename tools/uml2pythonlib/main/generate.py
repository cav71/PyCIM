import logging

from lxml import etree as et

import uml2pythonlib.utils
from uml2pythonlib.mappers import pymapper
from uml2pythonlib import maintenance


logger = logging.getLogger(__name__)


def verify(doc):
    root = doc.getroot()
    ns = root.nsmap
    
    expected = '2.1'
    found = root.attrib.get('{{{xmi}}}version'.format(**ns))
    if expected != found:
        raise ValueError('expected version "%s" bt found "%s"' % (expected, found) )
    logger.debug('detected version "%s"' % (found))


def create_package_dirs(outdir, doc):
    "generates the package dirs under outdir"
    packages = set()

    root = doc.getroot()
    find = et.XPath("./uml:Model//packagedElement[@xmi:type='uml:Class']", namespaces=root.nsmap)
    for n in find(root):
        if not 'name' in n.attrib:
            continue
        klass, ns = extract_class_and_package(n)
        packages.update((tuple(ns),))

    for package in packages:
        pdir = npath(*([outdir,] + list(package)))
        if not os.path.exists(pdir):
            os.makedirs(pdir)
        dst = npath(pdir, "__init__.py")
        if os.path.exists(dst):
            continue
        logger.info("creating package: %s" % '.'.join(package))
        fp = open(npath(pdir, "__init__.py"), "w")
        fp.close()


def extract_class_and_package(node):
    """extracts class name and package from a uml node

"""
    result = [ None, None, ]
    if not 'name' in node.attrib:
        return result

    result = node.attrib['name'], []
    for p in maintenance.parents(node, include_node=False):
        the_type = p.attrib.get('{http://schema.omg.org/spec/XMI/2.1}type', None)
        if the_type != "uml:Package":
            continue
        result[1].append(p.attrib.get('name')) 
    return result


def extract_class_get_documentation(doc, nodeid, nsmap):
    find_elements = et.XPath("/xmi:XMI/xmi:Extension/elements/element[@xmi:idref='%s']/properties" % nodeid, namespaces=nsmap)
    elements = find_elements(doc)
    if elements and 'documentation' in elements[0].attrib:
        return elements[0].attrib['documentation']
    return None


def find_map_class_base(doc, node):
    find_generalizations = et.XPath("./generalization[@xmi:type='uml:Generalization']", namespaces=node.nsmap)

    #TODO: support multiple inheritance
    generalizations = find_generalizations(node)
    if len(generalizations) > 1:
        logger.warn("multiple generalizations not supported for node: %s", doc.getpath(node))
        return None

    # no parent so we derive from the object
    if len(generalizations) == 0:
        return ("object", None)
    
    generalization = generalizations[0]
    parentid = generalization.attrib['general']
    root = doc.getroot()
    pfind = et.XPath("./uml:Model//packagedElement[@xmi:id='%s']" % parentid, namespaces=root.nsmap)
    # returning the base class and the packages list
    return extract_class_and_package(pfind(root)[0])


def generate_class_modules(outdir, doc, classmap):
    root = doc.getroot()

    #find_classes = et.XPath("./uml:Model//packagedElement[@xmi:type='uml:Class']", namespaces=root.nsmap)
    find_classes = et.XPath("./uml:Model//packagedElement[@xmi:id='EAID_2E70DC9D_AEAE_46cc_B20A_C20A636AE9B0']", namespaces=root.nsmap)

    for node_class in find_classes(root):
        # We extract the class id
        nodeid = node_class.attrib["{{{xmi}}}id".format(**node_class.nsmap)]
        logger.debug("node id '%s'" % nodeid)

        derived = find_map_class_base(doc, node_class) #ex. map_class_getbase
        logger.debug("node id '%s' derived from: %s" % (nodeid, str(derived)))
        if not derived:
            continue

        name, ns =  extract_class_and_package(node_class) #ex. map_class_get_documentation
        if not ns:
            logger.warn("no namespace for node: %s", doc.getpath(node_class))
            continue
        logger.debug("node id '%s' instance of: %s %s" % (nodeid, name, str(ns)))


        # getting the class documentation
        documentation = extract_class_get_documentation(doc, nodeid, node_class.nsmap) #ex. map_class_get_documentation

        obj = classmap.Mapper(name, derived)
        obj.doc = documentation

        fileName = npath(*([outdir, ] + ns + [name,])) + '.py'
        open(fileName, 'w').write(obj.render())
        logger.info('generate %s in %s' % (name, fileName))


def cli_options(parser):
    def pathtype(text):
        return uml2pythonlib.utils.npath(text)
    parser.add_argument("outdir", type=pathtype, help="output directory")
    parser.add_argument("umlfile", type=pathtype, help="uml xml file")


def main(options):
    logger.info('loading xml file "%s"' % options.umlfile)
    logger.info('output dir %s' % options.outdir)


    # parsing into doc the whole uml file
    parser = et.XMLParser(remove_blank_text=True)
    doc = et.parse(options.umlfile, parser)

    # verifying the doc is a uml 2.1
    verify(doc)


    # generating the whole hierarchy
    # (only the package directories)
    create_package_dirs(options.outdir, doc)


    generate_class_modules(options.outdir, doc, pymapper)

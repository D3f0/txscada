from lxml.etree import ElementTree
from functools import partial


nsmap = {
    'sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd',
    'cc': 'http://web.resource.org/cc/',
    'svg': 'http://www.w3.org/2000/svg',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'xlink': 'http://www.w3.org/1999/xlink',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'inkscape': 'http://www.inkscape.org/namespaces/inkscape'
}


tree = ElementTree(file='source.svg')
find = partial(tree.xpath, namespaces=nsmap)
# print find('//svg:rect')


print find('//svg:rect[@class="electric"]')
from IPython import embed; embed()

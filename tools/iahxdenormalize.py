# coding: utf-8

from lxml import etree as ET
import json
from base28 import reprbase

ALLOWED_ANALITICAL_ELEMENT = ['au', 'ti_pt', 'fo']
ADDED_FIELDS = set()


filestring = ' '.join(open('scielobooks_iahx2.xml').read().splitlines())

o_add = ET.fromstring(filestring)
add = ET.Element('add')

mono_struct_dic = {}
mono_list = (i for i in o_add.findall('.//doc/field[@name="type"]') if not i.text.startswith('a'))

for mono_elem in mono_list:
    struct = {}
    for field in mono_elem.itersiblings():
        if field.attrib['name'] == 'isbn':
            key = unicode(field.text).strip()
        else:
            struct[field.attrib['name']] = unicode(field.text).strip()
    mono_struct_dic[key] = json.dumps(struct, ensure_ascii=False)

anali_struct_dic = {}
anali_list = (i for i in o_add.findall('.//doc/field[@name="type"]') if i.text.startswith('a'))
for anali_elem in anali_list:
    struct = {}
    for field in anali_elem.itersiblings():
        if field.attrib['name'] == 'isbn':
            key = unicode(field.text).strip()
        elif field.attrib['name'] in ALLOWED_ANALITICAL_ELEMENT:
            struct[field.attrib['name']] = unicode(field.text).strip()

    if not anali_struct_dic.has_key(key):
        anali_struct_dic[key] = []

    anali_struct_dic[key].append(struct)


for o_doc in o_add.findall('doc'):
    doc = ET.SubElement(add, o_doc.tag)
    isbn = unicode(o_doc.xpath('./field[@name="isbn"]')[0].text).strip()

    for o_elem in o_doc.getchildren():
        elem = ET.SubElement(doc, o_elem.tag, name='%s' % o_elem.attrib['name'])

        if o_elem.attrib['name'] == 'type':
            elem.text = unicode(o_elem.text).strip()[:1]
            if o_elem.text.startswith('a'):
                mono_struct = ET.SubElement(doc, o_elem.tag, name='mono_struct')
                mono_struct.text = mono_struct_dic[isbn]
            else:
                for doc_dic in anali_struct_dic[isbn]:
                    for key, value in doc_dic.items():
                        if value not in ADDED_FIELDS:
                            doc_struct = ET.SubElement(doc, o_elem.tag, name='am_%s' % key)
                            doc_struct.text = value
                            ADDED_FIELDS.add(value)
        elif o_elem.attrib['name'] == 'id':
            elem.text = reprbase(int(o_elem.text))
        else:
            elem.text = unicode(o_elem.text).strip()

print ET.tostring(add, encoding='utf-8', pretty_print=True, xml_declaration=True)


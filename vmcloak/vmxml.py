import xml.etree.ElementTree as etree
from vmcloak.misc import append_child

class Element(object):

    def __init__(self, tagName, text=None, namespace=None, namespace_uri=None,
                 **attrs):
        if namespace_uri is not None:
            tagName = '{%s}%s' % (namespace_uri, tagName,)
            if namespace is not None:
                etree.register_namespace(namespace, namespace_uri)
        self._elem = etree.Element(tagName)
        self.setAttrs(**attrs)
        if text is not None:
            self.appendTextNode(text)

    def __getattr__(self, name):
        return getattr(self._elem, name)

    def __len__(self):
        return len(self._elem)

    def __iter__(self):
        return iter(self._elem)

    def setAttrs(self, **attrs):
        for attrName, attrValue in attrs.items():
            self._elem.set(attrName, attrValue)

    def setAttr(self, attrName, attrValue):
        self._elem.set(attrName, attrValue)

    def appendTextNode(self, text):
        self._elem.text = text

    def appendChild(self, element=None, etree_element=None):
        append_child(self._elem, element, etree_element)

    def appendChildWithArgs(self, childName, text=None, **attrs):
        child = Element(childName, text, **attrs)
        append_child(self._elem, child)
        return child

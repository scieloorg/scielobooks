import copy
import uuid

import colander


class AnyType(colander.SchemaType):
    def serialize(self, node, appstruct):
        return appstruct

    def deserialize(self, node, cstruct):
        return cstruct


class Property:
    def __init__(self, required=False):
        self.required = required
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self.name in instance._data:
            return instance._data[self.name]
        raise AttributeError(self.name)

    def __set__(self, instance, value):
        instance._data[self.name] = value

    def schema_node(self):
        missing = colander.required if self.required else None
        return colander.SchemaNode(colander.String(), name=self.name, missing=missing)


class TextProperty(Property):
    pass


class BooleanProperty(Property):
    def schema_node(self):
        missing = colander.required if self.required else None
        return colander.SchemaNode(colander.Boolean(), name=self.name, missing=missing)


class CompositeTextProperty(Property):
    def __init__(self, subkeys, required=False):
        super().__init__(required=required)
        self.subkeys = list(subkeys)

    def schema_node(self):
        node = colander.SchemaNode(colander.Mapping(), name=self.name, missing=None)
        for key in self.subkeys:
            node.add(colander.SchemaNode(colander.String(), name=key, missing=None))
        return node


class MultiCompositeTextProperty(Property):
    def __init__(self, subkeys, required=False):
        super().__init__(required=required)
        self.subkeys = list(subkeys)

    def schema_node(self):
        child = colander.SchemaNode(colander.Mapping(), name="item")
        for key in self.subkeys:
            child.add(colander.SchemaNode(colander.String(), name=key, missing=None))
        return colander.SchemaNode(colander.Sequence(), child, name=self.name, missing=[])


class FileProperty(Property):
    def schema_node(self):
        # Minimal representation compatible with current views.
        node = colander.SchemaNode(colander.Mapping(), name=self.name, missing=None)
        node.add(colander.SchemaNode(AnyType(), name="fp", missing=None))
        node.add(colander.SchemaNode(colander.String(), name="filename", missing=None))
        node.add(colander.SchemaNode(colander.String(), name="uid", missing=""))
        return node


class CouchdbDocument:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        props = {}
        for base in reversed(cls.__mro__[1:]):
            props.update(getattr(base, "_properties", {}))
        for name, value in cls.__dict__.items():
            if isinstance(value, Property):
                props[name] = value
        cls._properties = props

    def __init__(self, **kwargs):
        self._data = {}
        self._id = kwargs.pop("_id", kwargs.pop("id", str(uuid.uuid4())))
        self._rev = kwargs.pop("_rev", None)
        for key, value in kwargs.items():
            self._data[key] = value

    @classmethod
    def get_schema(cls):
        schema = colander.Schema()
        hidden = set(getattr(getattr(cls, "Meta", None), "hide", ()))
        for name, prop in cls._properties.items():
            if name in hidden:
                continue
            schema.add(prop.schema_node())
        schema.add(colander.SchemaNode(colander.String(), name="_id", missing=None))
        schema.add(colander.SchemaNode(colander.String(), name="_rev", missing=None))
        return schema

    @classmethod
    def from_python(cls, data):
        if data is None:
            return None
        return cls(**copy.deepcopy(data))

    @classmethod
    def get(cls, db, doc_id):
        doc = db.get(doc_id)
        return cls.from_python(doc)

    def to_python(self):
        data = copy.deepcopy(self._data)
        data["_id"] = self._id
        if self._rev:
            data["_rev"] = self._rev
        return data

    def _prepare_doc(self):
        doc = self.to_python()
        for name, prop in self._properties.items():
            if isinstance(prop, FileProperty):
                value = doc.get(name)
                if isinstance(value, dict):
                    value = dict(value)
                    value.pop("fp", None)
                    doc[name] = value
        return doc

    def save(self, db):
        response = db.save_doc(self._prepare_doc())
        self._id = response.get("id", self._id)
        self._rev = response.get("rev", self._rev)
        return response

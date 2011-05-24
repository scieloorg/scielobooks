from models import Monograph

import deform
import colander

class MemoryTmpStore(dict):
    def preview_url(self, name):
        return None


class EvaluationForm():

    tmpstore = MemoryTmpStore()

    base_schema = Monograph.get_schema()
    base_schema.add(colander.SchemaNode(
        colander.String(),
        name='publisher_url',
        missing=None))    
    base_schema.add(colander.SchemaNode(
        deform.FileData(),
        name='editorial_decision',
        widget=deform.widget.FileUploadWidget(tmpstore),
        missing=None))
    base_schema.add(colander.SchemaNode(
        deform.FileData(),
        name='toc',
        widget=deform.widget.FileUploadWidget(tmpstore),
        missing=None))
       
    @classmethod
    def get_form(cls):
        return deform.Form(cls.base_schema, buttons=('submit',))
    

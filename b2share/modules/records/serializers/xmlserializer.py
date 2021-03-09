from invenio_records_rest.serializers.base import PreprocessorMixin
from lxml import etree
from lxml.builder import E
from invenio_records.api import Record

class XMLSerializer(PreprocessorMixin):
    schema_class = None

    def __init__(self, schema, replace_refs=True):
        self.schema_class = schema
        self.replace_refs = replace_refs

    def serialize_oaipmh(self, pid, record):
        rec = None
        if isinstance(record, Record):
            rec = self.preprocess_record(pid=pid, record=record)
        elif isinstance(record['_source'], Record):
            rec = self.preprocess_record(pid=pid, record=record['_source'])
        return self.schema_class().dump_etree(pid, rec)
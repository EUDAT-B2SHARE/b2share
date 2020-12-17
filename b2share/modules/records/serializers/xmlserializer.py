from invenio_records_rest.serializers.base import PreprocessorMixin
from lxml import etree
from lxml.builder import E
from b2share.modules.records.api import B2ShareRecord

class XMLSerializer(PreprocessorMixin):
    schema_class = None

    def __init__(self, schema, replace_refs=False):
        self.schema_class = schema
        self.replace_refs = replace_refs

    def serialize_oaipmh(self, pid, record):
        rec = self.preprocess_record(pid, B2ShareRecord.get_record(record['_source']['_deposit']['id']))
        return self.schema_class().dump_etree(pid, rec)
from datacite.schema43 import *
import pkg_resources

root_attribs = {
    '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation':
    'http://datacite.org/schema/kernel-4 '
    'http://schema.datacite.org/meta/kernel-4.4/metadata.xsd',
}

del rules.rules['identifiers']

validator.schema['definitions']['resourceTypeGeneral']['enum'] += [
    "BookChapter",
    "ComputationalNotebook",
    "ConferencePaper",
    "ConferenceProceeding",
    "Dissertation",
    "Journal",
    "JournalArticle",
    "OutputManagementPlan",
    "PeerReview",
    "Preprint",
    "Report",
    "Standard"
]
validator.schema['definitions']['relationType']['enum'].append("IsPublishedIn")

def dump_etree(data):
    """Convert JSON dictionary to DataCite v4.3 XML as ElementTree."""
    return dump_etree_helper(data, rules, ns, root_attribs)


def tostring(data, **kwargs):
    """Convert JSON dictionary to DataCite v4.3 XML as string."""
    return etree_to_string(dump_etree(data), **kwargs)


def validate(data):
    """Validate DataCite v4.3 JSON dictionary."""
    return validator.is_valid(data)


@rules.rule('identifiers')
def identifiers(path, values):
    doi = ''
    for value in values:
        if value['identifierType'] == 'DOI':
            if doi != '':
                # Don't know what to do with two DOIs
                # Which is the actual identifier?
                raise TypeError
            doi = E.identifier(
                value['identifier'],
                identifierType='DOI'
            )
    return doi

@rules.rule('alternateIdentifiers')
def alternate_identifiers(path, values):
    """Transform alternateIdentifiers."""
    if not values:
        return
    root = E.alternateIdentifiers()
    for value in values:
        elem = E.alternateIdentifier()
        elem.text = value['alternateIdentifier']
        elem.set('alternateIdentifierType', value['alternateIdentifierType'])
        root.append(elem)
    return root

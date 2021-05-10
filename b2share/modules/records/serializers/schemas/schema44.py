from datacite.schema43 import *

del rules.rules['identifiers']

@rules.rule('identifiers')
def identifiers(path, values):
    doi = ''
    for value in values:
        print(value['identifierType'] == 'DOI')
        print(value['identifierType'])
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

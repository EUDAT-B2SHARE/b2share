from flask import url_for
from lxml.builder import E
from .eudatcore import EudatCoreSchema
from lxml import etree
from .dc import record_url
from datetime import datetime

def add_affiliations(source, target):
    if source.get('affiliations', []):
        for a in source['affiliations']:
            affiliation = E.affiliation(a['affiliation_name'])
            if a.get('affiliation_identifier'):
                affiliation.set('affiliationIdentifier', a['affiliation_identifier'])
                if a.get('scheme'):
                    affiliation.set('affiliationIdentifierScheme', a['scheme'])
            target.append(affiliation)

def add_name_identifiers(source, target):
    if source.get('name_identifiers'):
        for i in source['name_identifiers']:
            name_id = E.nameIdentifier(i['name_identifier'], nameIdentifierScheme=i['scheme'])
            if 'scheme_uri' in i:
                name_id.set('schemeUri', i['scheme_uri'])
            target.append(name_id)

class EudatExtendedSchema(EudatCoreSchema):
    def identifiers(self, metadata, root):
        ids = E.identifiers()
        for item in metadata['_pid']:
            if item['type']  == 'DOI':
                ids.append(E.identifier(item['value'], identifierType=item['type']))
            if item['type'] == 'b2rec':
                ids.append(E.identifier(record_url(item['value']), identifierType='URL'))
        root.append(ids)

    def community(self, metadata, root):
        community_url = url_for('b2share_communities.communities_item', community_id=metadata['community'], _external=True)
        root.append(E.community(community_url, communityIdentifierType='URL'))

    def creators(self, metadata, root):
        ret = E.creators()
        for c in metadata.get('creators', []):
            creator = E.creator()
            creator_name = E.creatorName()
            if c.get('name_type'):
                creator_name.set('nameType', c['name_type'])
            creator.append(creator_name)
            if 'given_name' in c:
                creator.append(E.givenName(c['given_name']))
            if 'family_name' in c:
                creator.append(E.familyName(c['family_name']))
            add_name_identifiers(c, creator)
            add_affiliations(c, creator)
            ret.append(creator)
        root.append(ret)

    def titles(self, metadata, root):
        titles = E.titles()
        for t in metadata['titles']:
            title = E.title(t['title'])
            if t.get('type'):
                title.set('type', t['type'])
            titles.append(title)
        root.append(titles)


    def publisher(self, metadata, root):
        if 'publisher' in metadata:
            root.append(E.publisher(metadata['publisher']))

    def keywords(self, metadata, root):
        if 'keywords' in metadata:
            keywords = E.keywords()
            for s in metadata['keywords']:
                if isinstance(s, str):
                    keywords.append(E.keyword(s))
                else:
                    keyword = E.keyword(s['keyword'])
                    if s.get('scheme'):
                        keyword.set('keywordScheme', s['scheme'])
                    if s.get('scheme_uri'):
                        keyword.set('schemeURI', s['scheme_uri'])
                    keywords.append(keyword)
            root.append(keywords)

    def disciplines(self, metadata, root):
        if 'disciplines' in metadata:
            disciplines = E.disciplines()
            for d in metadata['disciplines']:
                if isinstance(d, str):
                    disciplines.append(E.discipline(d))
                else:
                    discipline = E.discipline(d['discipline_name'].split('→')[-1])
                    if d.get('scheme_uri'):
                        discipline.set('schemeURI', d['scheme_uri'])
                    if d.get('scheme'):
                        discipline.set('disciplineScheme', d['scheme'])
                    if d.get('discipline_identifier'):
                        discipline.set('disciplineIdentifier', d['discipline_identifier'])
                    disciplines.append(discipline)
            root.append(disciplines)

    def contributors(self, metadata, root):
        if 'contributors' in metadata:
            contributors = E.contributors()
            for c in metadata['contributors']:
                contributor = E.contributor(contributorType=c['contributor_type'])
                contributor.append(E.contributorName(c['contributor_name']))
                if 'given_name' in c:
                    contributor.append(E.givenName(c['given_name']))
                if 'family_name' in c:
                    contributor.append(E.familyName(c['family_name']))
                add_name_identifiers(c, contributor)
                add_affiliations(c, contributor)
                contributors.append(contributor)
            root.append(contributors)

    def dates(self, obj, root):
        from dateutil import parser
        metadata = obj['metadata']
        dates = E.dates()
        if 'dates' in metadata:
            for d in metadata['dates']:
                date = E.date(d['date'], dateType=d['date_type'])
                if (d.get('date_information')):
                    date.set('dateInformation', d['date_information'])
                dates.append(date)
        dates.append(E.date(obj['created'],dateType='Created', dateInformation='Creation'))
        d = parser.parse(obj['updated']) - parser.parse(obj['created'])
        if d.days > 0:
            dates.append(E.date(obj['updated'], dateType='Updated', dateInformation='Updated with latest properties'))
        root.append(dates)

    def resource_types(self, metadata, root):
        if 'resource_types' in metadata:
            resourceTypes = E.resourceTypes()
            for r in metadata['resource_types']:
                resourceType = E.resourceType(resourceTypeGeneral=r['resource_type_general'])
                if r.get('resource_type'):
                    resourceType.text = r['resource_type']
                if r.get('resource_type_description'):
                    resourceType.text = r['resource_type_description']
                resourceTypes.append(resourceType)
            root.append(resourceTypes)

    def alternate_identifiers(self, metadata, root):
        if 'alternate_identifiers' in metadata:
            alt = E.alternateIdentifiers()
            for a in metadata['alternate_identifiers']:
                alt.append(E.alternateIdentifier(a['alternate_identifier'],\
                    alternateIdentifierType=a['alternate_identifier_type']))
            root.append(alt)

    def related_identifiers(self, metadata, root):
        if 'related_identifiers' in metadata:
            rel = E.relatedIdentifiers()
            for r in metadata['related_identifiers']:
                related_identifier = E.relatedIdentifier(r['related_identifier'],\
                    relatedIdentifierType=r['related_identifier_type'], relationType=r['relation_type'])
                if r.get('scheme'):
                    related_identifier.set('relatedMetadataScheme', r['scheme'])
                if r.get('scheme_uri'):
                    related_identifier.set('schemeURI', r['scheme_uri'])
                if r.get('resouce_type_general'):
                    related_identifier.set('resourceTypeGeneral', r['resource_type_general'])
                rel.append(related_identifier)
            root.append(rel)

    def rights_list(self, metadata, root):
        if metadata.get('license'):
            rights = E.rightsList()
            l = metadata['license']
            right = E.rights(l['license'])
            if l.get('scheme_uri'):
                right.set('schemeURI', l['scheme_uri'])
            if l.get('scheme'):
                right.set('rightsIdentifierScheme', l['scheme'])
            if l.get('license_identifier'):
                right.set('rightsIdentifier', l['license_identifier'])
            if l.get('license_uri'):
                right.set('rightsURI', l['license_uri'])
            rights.append(right)
            root.append(rights)

    def descriptions(self, metadata, root):
        if 'descriptions' in metadata:
            descriptions = E.descriptions()
            for d in metadata['descriptions']:
                descriptions.append(E.description(d['description'], descriptionType=d['description_type']))
            root.append(descriptions)

    def contacts(self, metadata, root):
        if 'contact_email' in metadata:
            contacts = E.contacts()
            contacts.append(E.contact(metadata['contact_email'], contactType='email'))
            root.append(contacts)

    def funding_references(self, metadata, root):
        if 'funding_references' in metadata:
            fundrefs = E.fundingReferences()
            for f in metadata['funding_references']:
                fundref = E.fundingReference()
                fundref.append(E.funderName(f['funder_name']))
                if 'funder_identifier' in f:
                    fundref.append(E.funderIdentifier(f['funder_identifier'],\
                        funderIdentifierType=f.get('funder_identifier_type'),\
                        schemeURI=f.get('scheme_uri')))
                if 'award_number' in f:
                    fundref.append(E.awardNumber(f['award_number'],awardURI=f.get('award_uri')))
                if 'award_title' in f:
                    fundref.append(E.awardTitle(f['award_title']))
                fundrefs.append(fundref)
            root.append(fundrefs)


    def dump_etree(self, pid, obj):
        metadata = obj['metadata']
        root = etree.Element('resource', nsmap=self.ns, attrib=self.root_attribs)
        self.identifiers(metadata, root)
        self.community(metadata, root)
        self.creators(metadata, root)
        self.instruments(metadata, root)
        self.titles(metadata, root)
        self.publishers(metadata, root)
        self.publication_year(obj, root)
        self.keywords(metadata, root)
        self.disciplines(metadata, root)
        self.contributors(metadata, root)
        self.dates(obj, root)
        self.languages(metadata, root)
        self.resource_types(metadata, root)
        self.alternate_identifiers(metadata, root)
        self.related_identifiers(metadata, root)
        self.sizes(metadata, root)
        self.formats(metadata, root)
        self.rights_list(metadata, root)
        self.descriptions(metadata, root)
        self.contacts(metadata, root)
        self.spatial_coverages(metadata, root)
        self.temporal_coverages(metadata, root)
        self.funding_references(metadata, root)
        return root
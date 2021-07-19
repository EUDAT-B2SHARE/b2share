from marshmallow import Schema
from lxml import etree
from lxml.builder import E
from b2share.modules.communities.api import Community
from b2share.modules.communities.errors import CommunityDoesNotExistError
from invenio_files_rest.models import Bucket, ObjectVersion, FileInstance
from invenio_records_files.models import RecordsBuckets
from b2share.modules.records.minters import make_record_url

def get_buckets(record_id):
    res = Bucket.query.join(RecordsBuckets).\
        filter(RecordsBuckets.bucket_id == Bucket.id,
               RecordsBuckets.record_id == record_id).all()
    return res

def human_readable_size(size):
    for unit in ['B', 'kB', 'MB', 'GB']:
        if size < 1000.0 or unit == 'GB':
            break
        size /= 1000.0
    return "{:.1f} {}".format(size, unit)

def geo_location_point(point, element_name):
    p = E(element_name, E.pointLongitude(str(point['point_longitude'])),
        E.pointLatitude(str(point['point_latitude'])))
    if 'point_vertical' in point:
        p.append(E.pointVertical(str(point['point_vertical'])))
    return p

class EudatCoreSchema(object):
    def identifiers(self, metadata, root):
        ids = E.identifiers()
        for item in metadata['_pid']:
            if item['type']  == 'DOI':
                ids.append(E.identifier(item['value'], identifierType=item['type']))
            if item['type'] == 'b2rec':
                ids.append(E.identifier(make_record_url(item['value']), identifierType='URL'))
        root.append(ids)

    def titles(self, metadata, root):
        ret = E.titles()
        for t in metadata['titles']:
            ret.append(E.title(t['title']))
        root.append(ret)

    def community(self, metadata, root):
        try:
            c = Community.get(id=metadata['community'])
            root.append(E.community(c.name))
        except CommunityDoesNotExistError:
            root.append(E.community('unknown'))

    def publishers(self, metadata, root):
        ret = E.publishers()
        ret.append(E.publisher('EUDAT B2SHARE'))
        if 'publisher' in metadata:
            ret.append(E.publisher(metadata['publisher']))
        root.append(ret)

    def publication_year(self, obj, root):
        metadata = obj['metadata']
        if 'embargo_date' in metadata:
            root.append(E.publicationYear(metadata['embargo_date'][:4]))
        elif 'publication_date' in metadata:
            root.append(E.publicationYear(metadata['publication_date'][:4]))
        else:
            root.append(E.publicationYear(obj['created'][:4]))

    def creators(self, metadata, root):
        if 'creators' in metadata:
            creators = E.creators()
            for c in metadata['creators']:
                creators.append(E.creator(c['creator_name']))
            root.append(creators)

    def instruments(self, metadata, root):
        if 'instruments' in metadata:
            instruments = E.instruments()
            for i in metadata['instruments']:
                instrument = E.instrument(i['instrument_name'])
                if 'instrument_identifier_type' in i:
                    instrument.set('instrumentIdentifierType', i['instrument_identifier_type'])
                instruments.append(instrument)
                if 'instrument_identifier' in i:
                    instrument.set('instrumentIdentifier', i['instrument_identifier'])
            root.append(instruments)

    def descriptions(self, metadata, root):
        if 'descriptions' in metadata:
            descriptions = E.descriptions()
            for d in metadata['descriptions']:
                descriptions.append(E.description(d['description']))
            root.append(descriptions)

    def resource_types(self, metadata, root):
        if 'resource_types' in metadata:
            ret = E.resourceTypes()
            for r in metadata['resource_types']:
                if 'resource_type_general' in r:
                    ret.append(E.resourceType(r['resource_type_general']))
                else:
                    ret.append(E.resourceType(r['resource_type']))
            root.append(ret)

    def rights_list(self, metadata, root):
        rights = E.rightsList()
        if 'license' in metadata:
            rights = E.rightsList()
            rights.append(E.rights(metadata['license']['license']))
        rights.append(E.rights('info:eu-repo/semantics/openAccess' if metadata.get('open_access') else 'info:eu-repo/semantics/closedAccess'))
        root.append(rights)


    def languages(self, metadata, root):
        if 'language' in metadata:
            languages = E.languages()
            languages.append(E.language(metadata['language']))
            root.append(languages)
        if 'languages' in metadata:
            languages = E.languages()
            for l in metadata['languages']:
                languages.append(E.language(l['language_identifier']))
            root.append(languages)

    def formats(self, metadata, root):
        formats = set()
        ret = False
        for f in metadata.get('_files', []):
            split = f.get('key', '').split('.')
            if len(split) > 1:
                ret = True
                formats.add(split[len(split)-1])
        if ret:
            fs = E.formats()
            for f in formats:
                fs.append(E.format(f))
            root.append(fs)

    def disciplines(self, metadata, root):
        if 'disciplines' in metadata:
            disciplines = E.disciplines()
            for d in metadata['disciplines']:
                if isinstance(d, str):
                    disciplines.append(E.discipline(d))
                else:
                    discipline = E.discipline(d['discipline_name'])
                    if d.get('scheme'):
                        discipline.set('disciplineScheme', d['scheme'])
                    if d.get('scheme_uri'):
                        discipline.set('schemeURI', d['scheme_uri'])
                    if d.get('discipline_identifier'):
                        discipline.set('disciplineIdentifier', d['discipline_identifier'])
                    disciplines.append(discipline)
            root.append(disciplines)

    def keywords(self, metadata, root):
        if 'keywords' in metadata:
            keywords = E.keywords()
            for s in metadata['keywords']:
                if 'keyword' in s:
                    keywords.append(E.keyword(s['keyword']))
                else:
                    keywords.append(E.keyword(s))
            root.append(keywords)

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
                related_identifier = E.relatedIdentifier(r['related_identifier'], relatedIdentifierType=r['related_identifier_type'])
                rel.append(related_identifier)
            root.append(rel)

    def contributors(self, metadata, root):
        if 'contributors' in metadata:
            contributors = E.contributors()
            for c in metadata['contributors']:
                contributors.append(E.contributor(E.contributorName(c['contributor_name'])))
            root.append(contributors)

    def contacts(self, metadata, root):
        if 'contact_email' in metadata:
            contacts = E.contacts()
            contacts.append(E.contact(metadata['contact_email']))
            root.append(contacts)

    def sizes(self, metadata, root):
        sizes = E.sizes()
        n_files = 0
        total_size = 0
        for f in metadata['_files']:
            total_size += f['size']
            n_files += 1
        if n_files > 0:
            sizes.append(E.size(human_readable_size(total_size)))
            sizes.append(E.size('{} file{}'.format(n_files, 's' if n_files>1 else '')))
            root.append(sizes)

    def version(self, metadata, root):
        if 'version' in metadata:
            version = E.version(metadata['version'])
            root.append(version)

    def spatial_coverages(self, metadata, root):
        if 'spatial_coverages' in metadata:
            covs = metadata['spatial_coverages']
            spatialCoverages = E.spatialCoverages()
            for cov in covs:
                spatialCoverage = E.spatialCoverage()
                if 'place' in cov:
                    spatialCoverage.append(E.geoLocationPlace(cov['place']))

                if 'point' in cov:
                    spatialCoverage.append(geo_location_point(cov['point'], 'geoLocationPoint'))

                if 'box' in cov:
                    box = cov['box']
                    b = E.geoLocationBox(
                        E.westBoundLongitude(str(box['westbound_longitude'])),
                        E.eastBoundLongitude(str(box['eastbound_longitude'])),
                        E.northBoundLatitude(str(box['northbound_latitude'])),
                        E.southBoundLatitude(str(box['southbound_latitude'])),
                    )
                    spatialCoverage.append(b)

                if 'polygons' in cov:
                    for polygon in cov['polygons']:
                        p = E.geoLocationPolygon()
                        for point in polygon.get('polygon', []):
                            p.append(geo_location_point(point, 'polygonPoint'))
                        if 'inpoint' in polygon:
                            p.append(geo_location_point(polygon['inpoint'], 'inPolygonPoint'))
                        spatialCoverage.append(p)
                spatialCoverages.append(spatialCoverage)
            root.append(spatialCoverages)

    def temporal_coverages(self, metadata, root):
        if 'temporal_coverages' in metadata:
            temporalCoverages = E.temporalCoverages()
            covs = metadata['temporal_coverages']
            if 'ranges' in covs:
                for r in covs['ranges']:
                    tempCov = E.temporalCoverage()
                    tempCov.append(E.startDate(r['start_date'], format='ISO-8601'))
                    tempCov.append(E.endDate(r['end_date'], format='ISO-8601'))
                    temporalCoverages.append(tempCov)
            if 'spans' in covs:
                for s in covs['spans']:
                    temporalCoverages.append(E.temporalCoverage(E.span(s)))
            root.append(temporalCoverages)

    def funding_references(self, metadata, root):
        if 'funding_references' in metadata:
            fundrefs = E.fundingReferences()
            for f in metadata['funding_references']:
                fundref = E.fundingReference()
                fundref.append(E.funderName(f['funder_name']))
                if 'award_number' in f:
                    fundref.append(E.awardNumber(f['award_number']))
                fundrefs.append(fundref)
            root.append(fundrefs)

    ns = {
        None: 'http://schema.eudat.eu/schema/kernel-1',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xml': 'xml',
    }

    root_attribs = {
        '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation':
        'http://schema.eudat.eu/kernel-1 '
        'http://schema.eudat.eu/meta/kernel-core-1.0/schema.xsd',
    }

    def dump_etree(self, pid, obj):
        metadata = obj['metadata']
        record_id = [x for x in metadata['_pid'] if x['type'] == 'b2rec'][0]['value']
        root = etree.Element('resource', nsmap=self.ns, attrib=self.root_attribs)
        self.titles(metadata, root)
        self.community(metadata, root)
        self.identifiers(metadata, root)
        self.publishers(metadata, root)
        self.publication_year(obj, root)
        self.creators(metadata, root)
        self.instruments(metadata, root)
        self.descriptions(metadata, root)
        self.rights_list(metadata, root)
        self.languages(metadata, root)
        self.resource_types(metadata, root)
        self.disciplines(metadata, root)
        self.keywords(metadata, root)
        self.formats(metadata, root)
        self.alternate_identifiers(metadata, root)
        self.related_identifiers(metadata, root)
        self.contributors(metadata, root)
        self.contacts(metadata, root)

        self.spatial_coverages(metadata, root)
        self.temporal_coverages(metadata, root)

        self.version(metadata, root)
        self.sizes(metadata, root)
        self.funding_references(metadata, root)
        return root
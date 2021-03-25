from marshmallow import Schema
from lxml import etree
from lxml.builder import E
from b2share.modules.communities.api import Community
from invenio_files_rest.models import Bucket, ObjectVersion, FileInstance
from invenio_records_files.models import RecordsBuckets
from b2share.modules.records.minters import make_record_url
import mimetypes

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

def geo_location_point(point):
    p = E.geoLocationPoint(E.pointLongitude(str(point['point_longitude'])),
        E.pointLatitude(str(point['point_latitude'])))
    if 'point_vertical' in point:
        p.append(E.pointVertical(str(point['point_vertical'])))
    return p

class EudatCoreSchema(object):
    def identifiers(self, obj, root, record_id):
        ret = E.identifiers()
        for item in obj['_pid']:
            prefix = ''
            if item['type'] == 'ePIC_PID':
                prefix = 'pid'
            if item['type'] == 'DOI':
                prefix = 'doi'
            if prefix:
                ret.append(E.identifier('{}:{}'.format(prefix, item['value'])))
        ret.append(E.identifier('url:{}'.format(make_record_url(record_id))))
        root.append(ret)

    def titles(self, metadata, root):
        ret = E.titles()
        for t in metadata['titles']:
            ret.append(E.title(t['title']))
        root.append(ret)

    def community(self, metadata, root):
        c = Community.get(id=metadata['community'])
        root.append(E.community(c.name))

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
                instruments.append(E.instrument(i['instrument_name']))
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
        if 'license' in metadata:
            rights = E.rightsList()
            rights.append(E.rights(metadata['license']['license']))
            root.append(rights)

    def languages(self, metadata, root):
        if 'language' in metadata:
            languages = E.languages()
            languages.append(E.language(metadata['language']))
            root.append(languages)
        if 'languages' in metadata:
            languages = E.languages()
            for l in metadata['languages']:
                languages.append(E.language(l))
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
                if 'discipline_name' in d:
                    disciplines.append(E.discipline(d['discipline_name']))
                else:
                    disciplines.append(E.discipline(d))
            root.append(disciplines)

    def subjects(self, metadata, root):
        if 'keywords' in metadata:
            subjects = E.subjects()
            for s in metadata['keywords']:
                if 'keyword' in s:
                    subjects.append(E.subject(s['keyword']))
                else:
                    subjects.append(E.subject(s))
            root.append(subjects)

    def alternate_identifiers(self, metadata, root):
        if 'alternate_identifiers' in metadata:
            alt = E.alternateIdentifiers()
            for i in metadata['alternate_identifiers']:
                alt.append(E.alternateIdentifier("{}:{}".format(i['alternate_identifier_type'], i['alternate_identifier'])))
            root.append(alt)

    def related_identifiers(self, metadata, root):
        if 'related_identifiers' in metadata:
            rel = E.relatedIdentifiers()
            for i in metadata['related_identifiers']:
                rel.append(E.relatedIdentifier("{}:{}".format(i['related_identifier_type'], i['related_identifier'])))
            root.append(rel)

    def contributors(self, metadata, root):
        if 'contributors' in metadata:
            contributors = E.contributors()
            for c in metadata['contributors']:
                contributors.append(E.contributor(c['contributor_name']))
            root.append(contributors)

    def contacts(self, metadata, root):
        if 'contact_email' in metadata:
            contacts = E.contacts()
            contacts.append(E.contact((metadata['contact_email'])))
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
                if 'places' in cov:
                    for place in cov['places']:
                        spatialCoverage.append(E.geoLocationPlace(place))

                if 'point' in cov:
                    spatialCoverage.append(geo_location_point(cov['point']))

                if 'box' in cov:
                    box = cov['box']
                    b = E.geoLocationBox(
                        E.westBoundLongitude(str(box['westbound_longitude'])),
                        E.eastBoundLongitude(str(box['eastbound_longitude'])),
                        E.northBoundLatitude(str(box['northbound_latitude'])),
                        E.southBoundLatitude(str(box['southbound_latitude'])),
                    )
                    spatialCoverage.append(b)

                if 'polygon' in cov:
                    p = E.geoLocationPolygon()
                    for point in cov['polygon']:
                        p.append(geo_location_point(point))
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
                    tempCov.append(E.startDate(r['start_date']))
                    tempCov.append(E.endDate(r['end_date']))
                    temporalCoverages.append(tempCov)
            if 'spans' in covs:
                for s in covs['spans']:
                    temporalCoverages.append(E.temporalCoverage(E.span(s)))
            root.append(temporalCoverages)

    def funding_references(self, metadata, root):
        if 'funding_references' in metadata:
            fundref = E.fundingReferences()
            for f in metadata['funding_references']:
                fundref.append(E.fundingReference(f['funder_name']))
            root.append(fundref)

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
        self.identifiers(metadata, root, record_id)
        self.publishers(metadata, root)
        self.publication_year(obj, root)
        self.descriptions(metadata, root)
        self.rights_list(metadata, root)
        self.languages(metadata, root)
        self.resource_types(metadata, root)
        self.creators(metadata, root)
        self.instruments(metadata, root)
        self.subjects(metadata, root)
        self.disciplines(metadata, root)
        self.contributors(metadata, root)
        self.formats(metadata, root)
        self.alternate_identifiers(metadata, root)
        self.related_identifiers(metadata, root)

        self.spatial_coverages(metadata, root)
        self.temporal_coverages(metadata, root)

        self.contacts(metadata, root)
        self.version(metadata, root)
        self.sizes(metadata, root)
        return root
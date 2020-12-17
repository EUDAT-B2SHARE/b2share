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
    p = E.geoLocationPoint(E.pointLongitude(point['point_longitude']),
        E.pointLatitude(point['point_latitude']))
    if 'point_vertical' in point:
        p.append(E.pointVertical(point['point_vertical']))
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

    def titles(self, obj, root):
        ret = E.titles()
        for t in obj['titles']:
            ret.append(E.title(t['title']))
        root.append(ret)

    def community(self, obj, root):
        c = Community.get(id=obj['community'])
        root.append(E.community(c.name))

    def publishers(self, obj, root):
        ret = E.publishers()
        ret.append(E.publisher('EUDAT B2SHARE'))
        if 'publisher' in obj:
            ret.append(E.publisher(obj['publisher']))
        root.append(ret)

    def publication_year(self, obj, root):
        if 'embargo_date' in obj:
            root.append(E.publicationYear(obj['embargo_date'][:4]))
        elif 'publication_date' in obj:
            root.append(E.publicationYear(obj['publication_date'][:4]))
        else:
            root.append(E.publicationYear(obj['created'][:4]))

    def creators(self, obj, root):
        if 'creators' in obj:
            creators = E.creators()
            for c in obj['creators']:
                creators.append(E.creator(c['creator_name']))
            root.append(creators)

    def instruments(self, obj, root):
        if 'instruments' in obj:
            instruments = E.instruments()
            for i in obj['instruments']:
                instruments.append(E.instrument(i['instrument_name']))
            root.append(instruments)

    def descriptions(self, obj, root):
        if 'descriptions' in obj:
            descriptions = E.descriptions()
            for d in obj['descriptions']:
                descriptions.append(E.description(d['description']))
            root.append(descriptions)

    def resource_types(self, obj, root):
        if 'resource_types' in obj:
            ret = E.resourceTypes()
            for r in obj['resource_types']:
                if 'resource_type_general' in r:
                    ret.append(E.resourceType(r['resource_type_general']))
                else:
                    ret.append(E.resourceType(r['resource_type']))
            root.append(ret)

    def rights_list(self, obj, root):
        if 'license' in obj:
            rights = E.rightsList()
            rights.append(E.rights(obj['license']['license']))
            root.append(rights)

    def languages(self, obj, root):
        if 'language' in obj:
            languages = E.languages()
            languages.append(E.language(obj['language']))
            root.append(languages)
        if 'languages' in obj:
            languages = E.languages()
            for l in obj['languages']:
                languages.append(E.language(l))
            root.append(languages)

    def formats(self, buckets, root):
        formats = E.formats()
        ret = False
        for bucket in buckets:
            fres = ObjectVersion.get_by_bucket(bucket)
            for f in fres:
                split = f.basename.split('.')
                if len(split) > 1:
                    ret = True
                    formats.append(E.format(split[len(split)-1]))
        if ret:
            root.append(formats)

    def disciplines(self, obj, root):
        if 'disciplines' in obj:
            disciplines = E.disciplines()
            for d in obj['disciplines']:
                if 'discipline_name' in d:
                    disciplines.append(E.discipline(d['discipline_name']))
                else:
                    disciplines.append(E.discipline(d))
            root.append(disciplines)

    def subjects(self, obj, root):
        if 'keywords' in obj:
            subjects = E.subjects()
            for s in obj['keywords']:
                if 'keyword' in s:
                    subjects.append(E.subject(s['keyword']))
                else:
                    subjects.append(E.subject(s))
            root.append(subjects)

    def alternate_identifiers(self, obj, root):
        if 'alternate_identifiers' in obj:
            alt = E.alternateIdentifiers()
            for i in obj['alternate_identifiers']:
                alt.append(E.alternateIdentifier("{}:{}".format(i['alternate_identifier_type'], i['alternate_identifier'])))
            root.append(alt)

    def related_identifiers(self, obj, root):
        if 'related_identifiers' in obj:
            rel = E.relatedIdentifiers()
            for i in obj['related_identifiers']:
                rel.append(E.alternateIdentifier("{}:{}".format(i['related_identifier_type'], i['related_identifier'])))
            root.append(rel)

    def contributors(self, obj, root):
        if 'contributors' in obj:
            contributors = E.contributors()
            for c in obj['contributors']:
                contributors.append(E.contributor(c['contributor_name']))
            root.append(contributors)

    def contacts(self, obj, root):
        if 'contact_email' in obj:
            contacts = E.contacts()
            contacts.append(E.contact((obj['contact_email'])))
            root.append(contacts)

    def sizes(self, buckets, root):
        sizes = E.sizes()
        n_files = 0
        total_size = 0
        for bucket in buckets:
            total_size += bucket.size
            fres = ObjectVersion.get_by_bucket(bucket)
            for object_version in fres:
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
            spatialCoverage = E.spatialCoverage()

            if 'places' in covs:
                for place in covs['places']:
                    spatialCoverage.append(E.geoLocationPlace(place))

            if 'points' in covs:
                for point in covs['points']:
                    spatialCoverage.append(geo_location_point(point))

            if 'boxes' in covs:
                for box in covs['boxes']:
                    b = E.geoLocationBox(
                        E.westBoundLongitude(box['westbound_longitude']),
                        E.eastBoundLongitude(box['eastbound_longitude']),
                        E.northBoundLatitude(box['northbound_latitude']),
                        E.southBoundLatitude(box['southbound_latitude']),
                    )
                    spatialCoverage.append(b)

            if 'polygons' in covs:
                for polygon in covs['polygons']:
                    p = E.geoLocationPolygon()
                    for point in polygon:
                        p.append(geo_location_point(point))
                spatialCoverage.append(p)
            spatialCoverages.append(spatialCoverage)
            root.append(spatialCoverages)

    def temporal_coverages(self, metadata, root):
        if 'temporal_coverages' in metadata:
            temporalCoverages = E.temporalCoverages()
            covs = metadata['temporal_coverages']
            if 'start_end_dates' in covs:
                for date in covs['start_end_dates']:
                    tempCov = E.temporalCoverage()
                    tempCov.append(E.startDate(date['start_date']), E.endDate(date['end_date']))
                    temporalCoverages.append(tempCov)
            if 'ranges' in covs:
                for r in covs['ranges']:
                    tempCov = E.temporalCoverage(E.range(r['range']))
                    if 'resolution' in r:
                        tempCov.append(E.resolution(r['resolution']))
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
        record_id = pid.pid_value[27:]
        metadata = obj['metadata']
        buckets = get_buckets(record_id)
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
        self.formats(buckets, root)
        self.alternate_identifiers(metadata, root)

        self.spatial_coverages(metadata, root)
        self.temporal_coverages(metadata, root)

        self.contacts(metadata, root)
        self.version(metadata, root)
        self.sizes(buckets, root)
        return root
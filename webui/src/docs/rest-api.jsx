import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router'

const Example = React.createClass({
    render() {
        const stylePre = {
            background:'#fafafa',
            border:'1px solid #eee',
            padding: '0.5em',
            margin: '0.5em 1em 0.5em 0',
            fontSize:'1em',
            whiteSpace: 'pre-wrap',
        };
        return (
            <pre style={stylePre}>
                <span style={{color:'#888'}}>Example: </span>
                <span style={{color:'#111'}}>
                    { this.props.children }
                </span>
            </pre>
        );
    }
});

const Returns = React.createClass({
    getInitialState() {
        return {
            open: false,
        };
    },
    toggle(e) {
        e.preventDefault();
        this.setState({open:!this.state.open});
    },
    jsonize(x) {
        x = JSON.stringify(this.props.children, null, 2);
        return x.replace(new RegExp('"\\.\\.\\."', 'g'), "...");
    },
    render() {
        return (
            <span style={{display:'block'}}>
                <span style={{color:'#888'}}>Returns: </span>
                { this.state.open ?
                    <a href="#" onClick={this.toggle}>[hide]</a> :
                    <a href="#" onClick={this.toggle}>[show]</a>
                }

                <span style={{display:'block'}}>
                { this.state.open ? this.jsonize(this.props.children) : false }
                </span>
            </span>
        );
    },
});

module.exports = function() {
  return (
    <div className='rest_api'>
        <h1>The B2SHARE HTTP REST API</h1>
        <p>The B2HARE HTTP REST API can be used for interacting with B2SHARE via
            external services or applications, for example for integrating with
            other web-sites (research community portals) or for uploading or
            downloading large data sets that are not easily handled via a web
            browser. This API can also be used for metadata harvesting.
        </p>

        <h3>Basic concepts</h3>
        <p> A scientific <strong>community</strong> has
            the roles of creating and maintaining metadata schemas and curating
            the datasets which are part of a scientific domain or research project.
            B2SHARE users can be part of one or more communities. Some selected
            members of a community are also given the role of community
            administrators, which grants them the special rights needed for the
            schema definitions and record curation tasks.</p>
        <p> Any user can upload scientific datasets into B2SHARE and thus
            create data <strong>records</strong>. A record is comprised of data
            files and associated metadata. The record’s <strong>metadata </strong>
            consists of a set of common fixed metadata fields and a set of custom
            metadata blocks, each block containing related metadata fields. A
            record is always connected to one scientific community which has the
            role of curating and maintaining it.</p>
        <p> A data record can exist in several states. Immediately after creation a record
            enters the 'draft' state. In this state the record is only accessible
            by its owner and can be freely modified: its metadata can be changed
            and files can be uploaded into or removed from it. A draft can be
            published at any time, and through this action it changes its state
            from 'draft' to 'published', is assigned Persistent Identifiers,
            and becomes publicly accessible. <strong>Please note that the list
            of files in a <em>published record</em> cannot be changed</strong>.
            </p>
        <p> A record contains a set of common metadata fields and a set of
            custom metadata blocks. This metadata is not free form, however,
            but is governed by static schemas; the common metadata schema is
            set by B2SHARE and defines a superset of Dublin Core elements,
            while the schema for the custom metadata block is specific to each
            community and can be customized by the community administrators.
            The schemas are formally defined in the JSON Schema format. A
            special HTTP API call is available for retrieving the JSON Schema
            of a record in a specific community. In order to be accepted, the
            records submitted to a community must conform to the schema
            required by the community.
        </p>

        <h3>Authentication</h3>
        <p>Only authenticated users can use the API. Each HTTP request to the
            server must pass an <code>access_token</code> parameter that
            identifies the user. The <code>access_token</code> is an
            opaque string which can be created in the user profile when
            logged in to the B2SHARE web user interface. B2SHARE’s access
            tokens follow the OAuth 2.0 standard. </p>
        <p>To get an access token, login to the B2SHARE web interface and click
            on your username. On the User Profile page, go to the “API Tokens”
            section, enter a token identification name (e.g. 'api') and click
            “New Token”. This will create an access token, visible on the
            screen. Please note that this is the only time the access token is
            visible, so copy it to a safe place. </p>
        <p>The following shell commands will expect that the ACCESS_TOKEN
            environment variable is defined and contains the actual
            access_token. The command to define this variable is: </p>
        <Example>export ACCESS_TOKEN='...'</Example>


        <h3>HTTP Requests</h3>
        <p> The HTTP requests are made to a URL with parameters as described
            below. Each URL consists of a protocol part (always 'https://'), a
            hostname and a path. One of the following hostnames can be used
            to identify the B2SHARE instance:
        </p>
        <ul>
            <li><code>{window.location.hostname}</code> - the hostname of the
                current site.
            </li>
            <li><code>b2share.eudat.eu</code> - the hostname of the production
                site.
            </li>
            <li><code>trng-b2share.eudat.eu</code> - the base url of the
                training site. Use this URL for testing.
            </li>
        </ul>
        <p>The following shell commands will expect that the HOST environment
            variable is defined and contains the host part of the targeted
            B2SHARE site, e.g.:
        </p>
        <Example>export HOSTNAME='trng-b2share.eudat.eu'</Example>


        <p>Each allowed request is described below as follows:</p>
        <ul>
            <li><p>Description - A description of the function of the request.</p></li>
            <li><p>URL path - grammar for the allowed paths used together with one of the base URLs above.</p></li>
            <li><p>HTTP method - whether the HTTP protocols GET or POST method is used.</p></li>
            <li><p>Example - an example of usage using the program curl from the command line.</p></li>
        </ul>

        <p>Variables in the descriptions:</p>
        <ul>
            <li><p>COMMUNITY_ID - identifier of a user community in B2SHARE</p></li>
            <li><p>RECORD_ID - identifier for a specific record, which can be in draft or published state</p></li>
            <li><p>FILE_BUCKET_ID - identifier for a set of files. Each record has its own file set,
                usually found in the links -> files section </p></li>
        </ul>

        <h3>A publication workflow</h3>
        <p> The HTTP API does not impose a specific workflow for creating a record.
            The following example workflow only defines the most basic steps:
        </p>
        <ol>
            <li>Identify a target community for your data by using the HTTP API
                <a href={`#list-all-communities`}> List all communities </a> function
            </li>
            <li>Using the community's identifier, retrieve the JSON Schema of the
                record's metadata. The submitted metadata will have to conform to
                this schema. Use the
                <a href={`#get-community-schema`}> Get community schema </a> function </li>
            <li>Create a draft record: use the
                <a href={`#create-draft`}> Create draft record </a> function</li>
            <li>Upload the files into the draft record. You will have to use
                one HTTP request per file. Use the
                <a href={`#upload-file`}> Upload file </a> function</li>
            <li>Set the complete metadata and publish the record. Use the
                <a href={`#publish-draft`}> Publish draft </a> function</li>
        </ol>


        <h2>The HTTP API</h2>

        <h3 id="list-all-communities">List all communities</h3>
        <p>List all the communities, without any filtering.</p>
        <ul>
            <li><p>HTTP method: GET</p></li>
            <li><p>URL path: /api/communities</p></li>
            <li><p>Required parameters: access_token</p></li>
            <li><p>Returns: the list of communities (in JSON format) or an error message.</p></li>
        </ul>
        <Example>
            curl https://$HOSTNAME/api/communities/?access_token=$ACCESS_TOKEN
            <Returns>
            {{
              "hits": {
                "hits": [
                  {
                    "created": "Tue, 18 Oct 2016 08:30:47 GMT",
                    "description": "The big Eudat community. Use this community if no other is suited for you",
                    "id": "e9b9792e-79fb-4b07-b6b4-b9c2bd06d095",
                    "links": {
                      "self": "https://vm0045.kaj.pouta.csc.fi/api/communities/e9b9792e-79fb-4b07-b6b4-b9c2bd06d095"
                    },
                    "logo": "/img/communities/eudat.png",
                    "name": "EUDAT",
                    "updated": "Tue, 18 Oct 2016 08:30:47 GMT"
                  },
                  "...",
                ],
                "total": 11
              },
              "links": {
                "self": "https://vm0045.kaj.pouta.csc.fi/api/communities/"
              }
            }}
            </Returns>
        </Example>

        <h3 id="get-community-schema">Get community schema</h3>
        <p>Retrieves the JSON schema of records approved by a specific community.</p>
        <ul>
            <li><p>HTTP method: GET</p></li>
            <li><p>URL path: /api/communities/$COMMUNITY_ID/schemas/last</p></li>
            <li><p>Required parameters: access_token</p></li>
            <li><p>Returns: the JSON schema, embedded in a JSON object, or an error message.</p></li>
        </ul>
        <Example>
            curl https://$HOSTNAME/api/communities/$COMMUNITY_ID/schemas/last?access_token=$ACCESS_TOKEN
            <Returns>
            {{
              "community": "e9b9792e-79fb-4b07-b6b4-b9c2bd06d095",
              "draft_json_schema": {
                "$ref": "https://vm0045.kaj.pouta.csc.fi/api/communities/e9b9792e-79fb-4b07-b6b4-b9c2bd06d095/schemas/0#/json_schema",
                "$schema": "http://json-schema.org/draft-04/schema#"
              },
              "json_schema": {
                "allOf": [
                    "..."
                ]
              },
              "links": {
                "self": "https://vm0045.kaj.pouta.csc.fi/api/communities/e9b9792e-79fb-4b07-b6b4-b9c2bd06d095/schemas/0"
              },
              "version": 0
            }}
            </Returns>
        </Example>

        <h3>List all the records</h3>
        <p>List all the records, without any filtering.</p>
        <ul>
            <li><p>HTTP method: GET</p></li>
            <li><p>URL path: /api/records</p></li>
            <li><p>Required parameters: access_token</p></li>
            <li><p>Returns: the list of records (in JSON format) or an error message.</p></li>
        </ul>
        <Example>
            curl https://$HOSTNAME/api/records/?access_token=$ACCESS_TOKEN
            <Returns>
            {{
              "aggregations": {
                "type": {
                  "buckets": [],
                  "doc_count_error_upper_bound": 0,
                  "sum_other_doc_count": 0
                }
              },
              "hits": {
                "hits": [
                  {
                    "created": "2016-10-19T11:32:46.095143+00:00",
                    "files": [
                      {
                        "bucket": "473086fc-e125-4389-8483-b8a4f130e181",
                        "checksum": "md5:c8afdb36c52cf4727836669019e69222",
                        "key": "myfile",
                        "size": 9,
                        "version_id": "324fdf1d-0005-41b1-a9c5-26a8eabd05a2"
                      }
                    ],
                    "id": "a1c2ef96a1e446fa9bd7a2a46d2242d4",
                    "links": {
                      "files": "https://vm0045.kaj.pouta.csc.fi/api/files/473086fc-e125-4389-8483-b8a4f130e181",
                      "self": "https://vm0045.kaj.pouta.csc.fi/api/records/a1c2ef96a1e446fa9bd7a2a46d2242d4"
                    },
                    "metadata": {
                      "..." : "..."
                    },
                    "updated": "2016-10-19T11:32:46.095152+00:00"
                  },
                  "..."
                ],
                "total": 51
              },
              "links": {
                "next": "https://vm0045.kaj.pouta.csc.fi/api/records/?sort=mostrecent&q=&page=2",
                "self": "https://vm0045.kaj.pouta.csc.fi/api/records/?sort=mostrecent&q=&page=1"
              }
            }}
            </Returns>
        </Example>

        <h3 id="list-records-per-community">List records per community</h3>
        <p>List all records of a specific community.</p>
        <ul>
            <li><p>URL path: /api/records/?q=community:COMMUNITY_ID</p></li>
            <li><p>HTTP method: GET</p></li>
            <li><p>Required parameters: access_token</p></li>
            <li><p>Returns: the list of records (in JSON format) or an error message.</p></li>
        </ul>
        <Example>
            curl https://$HOSTNAME/api/records/?q=community:$COMMUNITY_ID?access_token=$ACCESS_TOKEN
            <Returns>
            {{
              "aggregations": {
                "type": {
                  "buckets": [],
                  "doc_count_error_upper_bound": 0,
                  "sum_other_doc_count": 0
                }
              },
              "hits": {
                "hits": [
                  {
                    "created": "2016-10-24T11:29:27.016892+00:00",
                    "id": "f7fddf6f111f4362a9e4661294e2b59e",
                    "links": {
                      "files": "https://vm0045.kaj.pouta.csc.fi/api/files/90ea3483-2792-4483-9392-7d624b610398",
                      "self": "https://vm0045.kaj.pouta.csc.fi/api/records/f7fddf6f111f4362a9e4661294e2b59e"
                    },
                    "updated": "2016-10-24T11:29:27.016900+00:00",
                    "..." : "..."
                  },
                  "..."
                ],
                "total": 32
              },
              "links": {
                "next": "https://vm0045.kaj.pouta.csc.fi/api/records/?sort=bestmatch&q=community%3Ae9b9792e-79fb-4b07-b6b4-b9c2bd06d095&size=10&page=2",
                "self": "https://vm0045.kaj.pouta.csc.fi/api/records/?sort=bestmatch&q=community%3Ae9b9792e-79fb-4b07-b6b4-b9c2bd06d095&size=10&page=1"
              }
            }}
            </Returns>
        </Example>

        <h3>Search records</h3>
        <p>Search all the published records for a query string.</p>
        <ul>
            <li><p>URL path: /api/records/?q=$QUERY_STRING</p></li>
            <li><p>HTTP method: GET</p></li>
            <li><p>Required parameters: access_token</p></li>
            <li><p>Returns: the list of matching records (in JSON format) or an error message.</p></li>
        </ul>
        <Example>
            curl https://$HOSTNAME/api/records/?q=$QUERY_STRING?access_token=$ACCESS_TOKEN
        </Example>

        <h3>Search drafts</h3>
        <p>Search for all drafts (unpublished records) that are accessible by the requestor. Usually this means own records only.</p>
        <ul>
            <li><p>URL path: /api/records/?drafts=1</p></li>
            <li><p>HTTP method: GET</p></li>
            <li><p>Required parameters: access_token, drafts</p></li>
            <li><p>Returns: the list of matching drafts (in JSON format) or an error message.</p></li>
        </ul>
        <Example>
            curl https://$HOSTNAME/api/records/?drafts=1?access_token=$ACCESS_TOKEN
        </Example>

        <h3>Get a specific record</h3>
        <p>List the metadata of the record specified by RECORD_ID</p>
        <ul>
            <li><p>URL path: /api/record/RECORD_ID</p></li>
            <li><p>HTTP method: GET</p></li>
            <li><p>Required parameters: access_token</p></li>
        </ul>
        <Example>
            curl https://$HOSTNAME/api/records/47077e3c4b9f4852a40709e338ad4620?access_token=$ACCESS_TOKEN
        </Example>


        <h3 id="create-draft">Create a draft record</h3>
        <p>Create a new record, in the draft state.</p>
        <ul>
            <li><p>URL path: /api/records</p></li>
            <li><p>HTTP method: POST</p></li>
            <li><p>Required URL parameter: access_token</p></li>
            <li><p>Required data payload: json object with basic information about the object </p></li>
            <li><p>Returns: the new draft record contents and location. Please note that
                the returned json object contains also the URL of the file bucket used for the record.
                Also note that the URL of the draft record, needed for setting record metadata,
                will end in '/drafts/'</p></li>
        </ul>
        <Example>
            {'curl -i -H "Content-Type:application/json" -d \'{"title":"TestRest", "community":"e9b9792e-79fb-4b07-b6b4-b9c2bd06d095", "open_access":true}\' -X POST https://$HOSTNAME/api/records/?access_token=$ACCESS_TOKEN'}
            <Returns>
            {{
              "created": "2016-10-24T12:21:21.697737+00:00",
              "id": "01826ff3e4974415afdb2574a7ea5a91",
              "links": {
                "files": "https://vm0045.kaj.pouta.csc.fi/api/files/5594a1bf-1484-4a01-b7d3-f1eb3d2e1dc6",
                "publication": "https://vm0045.kaj.pouta.csc.fi/api/records/01826ff3e4974415afdb2574a7ea5a91",
                "self": "https://vm0045.kaj.pouta.csc.fi/api/records/01826ff3e4974415afdb2574a7ea5a91/draft"
              },
              "metadata": {
                "$schema": "https://vm0045.kaj.pouta.csc.fi/api/communities/e9b9792e-79fb-4b07-b6b4-b9c2bd06d095/schemas/0#/draft_json_schema",
                "community": "e9b9792e-79fb-4b07-b6b4-b9c2bd06d095",
                "open_access": true,
                "owners": [
                  8
                ],
                "publication_state": "draft",
                "title": "TestRest"
              },
              "updated": "2016-10-24T12:21:21.697744+00:00"
            }}
            </Returns>
        </Example>

        <h3 id="upload-file">Upload file into draft record</h3>
        <p>To upload a new file into a draft record object, first you need to identify
            the file bucket URL. This URL can be found in the information returned when
            querying a draft record, in the 'links/files' section of the returned data. </p>
        <ul>
            <li><p>URL path: /api/files/FILE_BUCKET_ID/FILE_NAME</p></li>
            <li><p>HTTP Method: PUT</p></li>
            <li><p>Required input data: the file, sent as direct stream</p></li>
            <li><p>Required parameters: access_token</p></li>
            <li><p>Returns: informations about the newly uploaded file</p></li>
        </ul>
        <Example>
            curl -X PUT -d @TestFileToBeUploaded.txt https://$HOSTNAME/api/files/$FILE_BUCKET_ID/TestFileToBeUploaded.txt?access_token=$ACCESS_TOKEN
        </Example>

        <h3>List the files uploaded into a record object</h3>
        <p>List the files uploaded into a record object</p>
        <ul>
            <li><p>URL path: /api/files/FILE_BUCKET_ID</p></li>
            <li><p>Http Method: GET</p></li>
            <li><p>Required parameters: access_token</p></li>
            <li><p>Returns: information about all the files in the record object</p></li>
        </ul>
        <Example>
            curl https://$HOSTNAME/api/files/$FILE_BUCKET_ID?access_token=$ACCESS_TOKEN
        </Example>

        <h3 id="update-draft">Update draft record's metadata</h3>
        <p>This action updates the draft record with new information.</p>
        <ul>
            <li><p>URL path: /api/records/RECORD_ID/</p></li>
            <li><p>HTTP Method: PATCH</p></li>
            <li><p>Required input data: the metadata for the record object to be created,
                in the json patch format (see <a href="http://jsonpatch.com/">http://jsonpatch.com/</a>)
                </p> </li>
            <li><p>Notes: The patch format contains one or more JSONPath strings. The root of these paths
                are the <i>metadata</i> object, as this is the only mutable object. For instance, to
                update the <i>title</i> field of the record, use this JSONPath: <code>/title</code>
                </p> </li>
        </ul>
        <Example>
            {'curl -X PATCH -H \'Content-Type:application/json-patch+json\' -d \'[{"op": "add", "path":"/description", "value": "This record describes..."}]\' https://$HOSTNAME/api/records/$RECORD_ID/draft?access_token=$ACCESS_TOKEN'}
            <Returns>
            {{
              "created": "2016-10-24T12:21:21.697737+00:00",
              "id": "01826ff3e4974415afdb2574a7ea5a91",
              "links": {
                "files": "https://vm0045.kaj.pouta.csc.fi/api/files/5594a1bf-1484-4a01-b7d3-f1eb3d2e1dc6",
                "publication": "https://vm0045.kaj.pouta.csc.fi/api/records/01826ff3e4974415afdb2574a7ea5a91",
                "self": "https://vm0045.kaj.pouta.csc.fi/api/records/01826ff3e4974415afdb2574a7ea5a91/draft"
              },
              "metadata": {
                "$schema": "https://vm0045.kaj.pouta.csc.fi/api/communities/e9b9792e-79fb-4b07-b6b4-b9c2bd06d095/schemas/0#/draft_json_schema",
                "community": "e9b9792e-79fb-4b07-b6b4-b9c2bd06d095",
                "description": "This record describes...",
                "open_access": true,
                "owners": [
                  8
                ],
                "publication_state": "draft",
                "title": "TestRest"
              },
              "updated": "2016-10-24T12:23:59.454951+00:00"
            }}
            </Returns>
        </Example>

        <h3 id="publish-draft">Publishing a draft record</h3>
        <p> This action transforms a draft record into a published record, and
            <strong> will make its files immutable</strong>.</p>
        <p> A draft record becomes published if a special metadata field, called
            'publication_state' is set to 'published'. This field can be set
            using the PATCH call described above.</p>
        <p> Depending on the domain specification, other fields could be
            required in order to successfully publish a record. In case one of
            the required fields is missing the request fails and an error
            message is returned with further details.</p>

        <Example>
            {'curl -X PATCH -H \'Content-Type:application/json-patch+json\' -d \'[{"op": "add", "path":"/publication_state", "value": "published"}]\' https://$HOSTNAME/api/records/$RECORD_ID/draft?access_token=$ACCESS_TOKEN'}
            <Returns>
            {{
              "created": "2016-10-24T12:21:21.697737+00:00",
              "id": "01826ff3e4974415afdb2574a7ea5a91",
              "links": {
                "files": "https://vm0045.kaj.pouta.csc.fi/api/files/5594a1bf-1484-4a01-b7d3-f1eb3d2e1dc6",
                "publication": "https://vm0045.kaj.pouta.csc.fi/api/records/01826ff3e4974415afdb2574a7ea5a91",
                "self": "https://vm0045.kaj.pouta.csc.fi/api/records/01826ff3e4974415afdb2574a7ea5a91/draft"
              },
              "metadata": {
                "$schema": "https://vm0045.kaj.pouta.csc.fi/api/communities/e9b9792e-79fb-4b07-b6b4-b9c2bd06d095/schemas/0#/draft_json_schema",
                "DOI": "10.5072/b2share.cdb15c27-326e-4e95-b812-6b1c6b54c299",
                "community": "e9b9792e-79fb-4b07-b6b4-b9c2bd06d095",
                "description": "This record describes...",
                "ePIC_PID": "http://hdl.handle.net/11304/2c473f04-d997-47d9-9bdb-d3d71800f870",
                "open_access": true,
                "owners": [
                  8
                ],
                "publication_state": "published",
                "title": "TestRest"
              },
              "updated": "2016-10-24T12:26:51.538025+00:00"
            }}
            </Returns>
        </Example>

        <h3>Responses</h3>
        <p>All response bodies are JSON encoded (UTF-8 encoded).</p>
        <p>{'A record is represented as a JSON object: \u007B "field1": value, … \u007D '}</p>
        <p>A collection of records is represented as a JSON array of objects:</p>
        <p>{'[\u007B "field1": value, ... }, … ]\u007D'}</p>
        <p>Timestamps are in UTC and formatted according to ISO 8601:</p>
        <p>YYYY-MM-DDTHH:MM:SS+00:00</p>
    </div>
  );
};

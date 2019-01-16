import React from 'react/lib/ReactWithAddons';
import { Link } from 'react-router';

const Example = React.createClass({
    render() {
        const stylePre = {
            background:'#fafafa',
            border: '1px solid #eee',
            padding: '0.5em',
            margin: '0.5em 1em 2em 0.5em',
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

function VarValue(props) {
    if (props.fixed) {
        return ( <code>{props.value}</code> );
    } else {
        return ( <span dangerouslySetInnerHTML={ {__html: props.value} } /> );
    }
}

function VarRow(props) {
    if (Array.isArray(props.values)) {
        var listValues = props.values.map(key =>
            <VarValue key={key} value={key} fixed={props.fixed}/>
        );
    } else {
        var listValues = <VarValue key={props.values} value={props.values} fixed={props.fixed}/>
    }
    return ( <li><p>{props.title}: {listValues}</p></li> );
}

var Request = React.createClass({
    // specify the titles per variable, the order is implicit
    vars: {
        "method": ["HTTP method", true],
        "path": ["URL path", true],
        "params": ["Required parameters", true],
        "status": ["Expected status code", true],
        "returns": ["Returns", false],
        "notes": ["Notes", false]
    },
    defaults: {
        "method": "GET",
        "status": 200,
        "params": ["access_token"]
    },
    render() {
        const styleH4 = {
            color: '#944',
            fontSize: '1.4em'
        };
        // add default values if missing
        var self = this;
        Object.keys(this.defaults).forEach(function(key) {
            if (!(key in self.props.children)) {
                self.props.children[key] = self.defaults[key]
            }
        });
        return (
            <span>
                <h4 style={styleH4} id={"" + this.props.children.title.toLowerCase().replace(/ /g, '-')}>{this.props.children.title}</h4>
                <p> <span dangerouslySetInnerHTML={ {__html: this.props.children.description} } /></p>
                <ul>{
                    Object.keys(this.vars).filter(name => Object.keys(this.props.children).includes(name)).map(name => (
                        <VarRow key={name} values={this.props.children[name]} title={this.vars[name][0]} fixed={this.vars[name][1]} />
                    ))
                }</ul>
            </span>
        );
    },
});

const Json = React.createClass({
    jsonize(x) {
        x = JSON.stringify(this.props.children, null, 2);
        return x.replace(new RegExp('"\\.\\.\\."', 'g'), "...");
    },
    render() {
        const stylePre = {
            background:'#fafafa',
            border:'1px solid #eee',
            padding: '0.5em',
            margin: '0.5em 1em 0.5em 0',
            fontSize:'0.9em',
            whiteSpace: 'pre-wrap',
        };
        return (
            <pre style={stylePre}>
                <span style={{display:'block'}}>
                { this.jsonize(this.props.children) }
                </span>
            </pre>
        );
    },
});

module.exports = function() {
  return (
    <div className='rest_api'>
        <h1>B2SHARE HTTP REST API</h1>
        <p>The B2HARE HTTP REST API can be used for interaction with B2SHARE via
            external services or applications, for example for integration with
            other web-sites (research community portals) or for uploading or
            downloading large data sets that are not easily handled via a web
            browser. The API can also be used for metadata harvesting, although an
            OAI-PMH API endpoint is also provided for this purpose. This latter API will not
            be discussed here.
        </p>
        <p>This page will explain the basic concepts, authentication and all existing
            HTTP requests that can currently be used. The given examples are explained
            using curl commands. For usage of the API with Python, please follow the
            <a href="https://github.com/EUDAT-Training/B2SHARE-Training"> training material </a>
            provided by EUDAT.</p>

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
        <p> A record contains a set of common metadata fields and a set of
            custom metadata blocks. This metadata is not free form, however,
            but is governed by static schemas; the common metadata schema is
            set by B2SHARE and defines a superset of Dublin Core elements,
            while the schema for the custom metadata block is specific to each
            community and can be customized by the community administrators.
            The schemas are formally defined in the JSON Schema format. A
            special HTTP REST API call is available for retrieving the JSON Schema
            of a record in a specific community. In order to be accepted, the
            records submitted to a community must conform to the schema
            required by the community.
        </p>

        <h3>Editing and versioning records</h3>
        <p> A data record can exist in several states. Immediately after creation a record
            enters the 'draft' state. In this state the record is only accessible
            by its owner and can be freely modified: its metadata can be changed
            and files can be uploaded into or removed from it. A draft can be
            published at any time, and through this action it changes its state
            from 'draft' to 'published', is assigned Persistent Identifiers,
            and becomes publicly accessible. <strong>Please note that the list
            of files in a <em>published record</em> cannot be changed without
            versioning the record</strong>.
            </p>
        <p> Existing published records can be versioned by creating a derivative draft
            that initially is a clone of the original record. This draft record can be
            changed in metadata but also files. A link will be established to the
            original record so that anyone can find and compare the contents of the
            versioned and original record. There is no limit to the number of versions
            created per record. A new versioned record needs to be published before it
            becomes available to other users.</p>

        <h3>Authentication</h3>
        <p>Only authenticated users can use the API. Each HTTP request
            to the server that involves creation or modification of records or
            the retrieval of user-private data must pass an <code>access_token</code>
            parameter that identifies the user. The <code>access_token</code> is an
            opaque string which can be created in the user profile when
            logged in to the B2SHARE web user interface. B2SHARE’s access
            tokens follow the OAuth 2.0 standard. </p>
        <p>To get an access token, login to the B2SHARE web interface and click
            on your username. On the User Profile page, go to the “API Tokens”
            section, enter a token identification name (e.g. 'api') and click
            “New Token”. This will create an access token, visible on the
            screen. Please note that this is the only time the access token is
            visible, so copy it to a safe place. </p>
        <p>You can remove existing access tokens by clicking on the corresponding
            'Remove' button on the far right to the token you want to remove.</p>
        <p>The following shell commands will expect that the ACCESS_TOKEN
            environment variable is defined and contains the actual
            access_token. The command to define this variable looks like this: </p>
        <Example>export ACCESS_TOKEN='7O28DlvgCatQV0pkS6jLw947tbo123oztkU4dPw6fnqmJ8inOYAi7dYhF0d04'</Example>
        <p>Please remember to use your actual token instead of the one given
        	as an example above.</p>


        <h3>API Requests</h3>
        <p> The API requests are made to a URL with parameters as described
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
        <p>Please make sure that you are not using production instances for
            creating test records or testing the API in general.
        </p>
        <p>The following shell commands will expect that the HOST environment
            variable is defined and contains the host part of the targeted
            B2SHARE site, e.g.:
        </p>
        <Example>export B2SHARE_HOST='trng-b2share.eudat.eu'</Example>

        <h3>Responses</h3>
        <p>All request response bodies are JSON encoded (UTF-8 encoded).</p>
        <p>A record is represented as a JSON object:</p>
        <Json>{{ "field1": "value" }}</Json>
        <p>A collection of records is represented as a JSON array of objects:</p>
        <Json>{{ "collection": [{ "field1": "value", "field2": "value" }, { "field1": "value", "field2": "value" }] }}</Json>
        <p>Timestamps are in UTC and formatted according to ISO 8601:</p>
        <Json>{{ "updated": "YYYY-MM-DDTHH:MM:SS.ssssss+00:00" }}</Json>

        <p>In case a request fails, the body of the response body contains details about the error, for example:</p>
        <Json>{{ "message": "The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.", "status": 404 }}</Json>
        <p>Herein the message field provides a detailed description of what went wrong, while the code indicates the HTTP status code (equivalent to the request response status code).</p>

        <h4>Status codes</h4>
        <p> The request status codes indicate whether the request was successfully received, processed and/or
            executed. B2SHARE follows the HTTP status codes where possible, a complete list can be found
            <a href="https://en.wikipedia.org/wiki/List_of_HTTP_status_codes"> here</a>.</p>
        <p> One of the following status codes is returned in case the request was successful:</p>
        <ul>
            <li><p><code>200</code> - Request was successfully received and executed, see body for results</p></li>
            <li><p><code>201</code> - Object created, see body for results</p></li>
            <li><p><code>204</code> - No contents, this occurs when for example an object is successfully deleted</p></li>
        </ul>

        <p> In case the request failed, the body of the response usually contains details, and one of the following
            status codes is returned:</p>
        <ul>
            <li><p><code>400</code> - Request was not understood</p></li>
            <li><p><code>401</code> - User must authenticate first, usually because no access token was provided with the request</p></li>
            <li><p><code>403</code> - User is not authorized to perform request, missing permission to do so</p></li>
            <li><p><code>404</code> - Requested object not found or API endpoint does not exist</p></li>
        </ul>

        <p> Any status code greater then or equal to 500 indicates that internally something went wrong in the server. If in this case
            the problem persists, kindly report this to <a href="https://eudat.eu/contact-support-request"> EUDAT</a>.</p>

        <h3>A publication workflow</h3>
        <p> The HTTP REST API does not impose a specific workflow for creating a record.
            The following example workflow only defines the most basic steps:
        </p>
        <ol>
            <li>Identify a target community for your data by using the HTTP REST API
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
                <a href={`#submit-draft`}> Submit draft for publication </a> function</li>
        </ol>

        <h3 id="migration">Migrating to the B2SHARE v2 HTTP REST API</h3>
        <p> The following changes are needed for a B2SHARE version 1 client using
            the old HTTP REST API in order to make it work with B2SHARE version 2
            for creating and publishing a record: </p>
        <ol>
            <li>Identify the unique ID of your target community or communities: see
                <a href={`#list-all-communities`}> List all communities </a> function
            </li>
            <li>Update the URL for creating a new record, from
                <code>/api/deposition/</code> to <code>/api/records/</code>; see
                <a href={`#create-draft`}> Create draft record </a> function</li>
            <li>Update the JSON structure of the newly created records to match the
                required JSON schema structure, see the
                <a href={`#get-community-schema`}> Get community schema </a> function </li>
            <li>Update the file upload calls, making sure that the file bucket url is used
                instead of the old record URL, see the
                <a href={`#upload-file`}> Upload file </a> function</li>
            <li>Update the old 'commit' action as described in the
                <a href={`#submit-draft`}> Submit draft for publication </a> function</li>
        </ol>

        <h2>Available HTTP REST API requests</h2>

        <p>Each allowed request is described as follows:</p>
        <ul>
            <li><p>Description - A description of the function of the request.</p></li>
            <li><p>HTTP method - which HTTP protocol such as GET or POST method is used.</p></li>
            <li><p>URL path - grammar for the allowed paths used together with one of the base URLs above.</p></li>
            <li><p>Status code - the returned status code upon a successful request.</p></li>
            <li><p>Returns - the returned data in the body of the response upon a successful request.</p></li>
            <li><p>Example - an example of usage using the program curl from the command line.</p></li>
        </ul>

        <p>Some of the requests additionally might have the following information:</p>
        <ul>
            <li><p>Required parameters - the parameters that need to be added to the URL.</p></li>
            <li><p>Required data - the data that needs to be sent with the request, the expected structure is shown in the example.</p></li>
        </ul>

        <p>Variables in the descriptions:</p>
        <ul>
            <li><p><code>COMMUNITY_ID</code> - identifier of a user community in B2SHARE</p></li>
            <li><p><code>RECORD_ID</code> - identifier for a specific record, which can be in draft or published state</p></li>
            <li><p><code>FILE_BUCKET_ID</code> - identifier for a set of files. Each record has its own file set,
                usually found in the links -> files section </p></li>
            <li><p><code>FILE_NAME</code> - name of a file in a specific file bucket</p></li>
        </ul>

        <h3>Object retrieval</h3>

        <Request>{{
            "title": "List all communities",
            "description": "List all the communities, without any filtering.",
            "path": "/api/communities/",
            "returns": "the list of communities (in JSON format) or an error message."
        }}</Request>
        <Example>
            curl https://$B2SHARE_HOST/api/communities/?access_token=$ACCESS_TOKEN
            <Returns>
            {{
              "hits": {
                "hits": [
                  {
                    "created": "Tue, 18 Oct 2016 08:30:47 GMT",
                    "description": "The big Eudat community. Use this community if no other is suited for you",
                    "id": "e9b9792e-79fb-4b07-b6b4-b9c2bd06d095",
                    "links": {
                      "self": "https://trng-b2share.eudat.eu/api/communities/e9b9792e-79fb-4b07-b6b4-b9c2bd06d095"
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
                "self": "https://trng-b2share.eudat.eu/api/communities/"
              }
            }}
            </Returns>
        </Example>

         <Request>{{
            "title": "Get community schema",
            "description": "Retrieves the JSON schema of records approved by a specific community.",
            "path": "/api/communities/$COMMUNITY_ID/schemas/last",
            "returns": "the community metadata schema, embedded in a JSON object, or an error message."
        }}</Request>
        <Example>
            curl https://$B2SHARE_HOST/api/communities/$COMMUNITY_ID/schemas/last?access_token=$ACCESS_TOKEN
            <Returns>
            {{
              "community": "e9b9792e-79fb-4b07-b6b4-b9c2bd06d095",
              "draft_json_schema": {
                "$ref": "https://trng-b2share.eudat.eu/api/communities/e9b9792e-79fb-4b07-b6b4-b9c2bd06d095/schemas/0#/json_schema",
                "$schema": "http://json-schema.org/draft-04/schema#"
              },
              "json_schema": {
                "allOf": [
                    "..."
                ]
              },
              "links": {
                "self": "https://trng-b2share.eudat.eu/api/communities/e9b9792e-79fb-4b07-b6b4-b9c2bd06d095/schemas/0"
              },
              "version": 0
            }}
            </Returns>
        </Example>

        <Request>{{
            "title": "List all records",
            "description": "List all the records, without any filtering.",
            "path": "/api/records",
            "returns": "the list of records (in JSON format) or an error message."
        }}</Request>
        <Example>
            curl https://$B2SHARE_HOST/api/records/?access_token=$ACCESS_TOKEN
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
                      "files": "https://trng-b2share.eudat.eu/api/files/473086fc-e125-4389-8483-b8a4f130e181",
                      "self": "https://trng-b2share.eudat.eu/api/records/a1c2ef96a1e446fa9bd7a2a46d2242d4"
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
                "next": "https://trng-b2share.eudat.eu/api/records/?sort=mostrecent&q=&page=2",
                "self": "https://trng-b2share.eudat.eu/api/records/?sort=mostrecent&q=&page=1"
              }
            }}
            </Returns>
        </Example>

        <Request>{{
            "title": "List records per community",
            "description": "List all records of a specific community.",
            "path": "/api/records/?q=community:COMMUNITY_ID",
            "returns": "the list of records (in JSON format) or an error message."
        }}</Request>
        <Example>
            curl https://$B2SHARE_HOST/api/records/?q=community:$COMMUNITY_ID?access_token=$ACCESS_TOKEN
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
                      "files": "https://trng-b2share.eudat.eu/api/files/90ea3483-2792-4483-9392-7d624b610398",
                      "self": "https://trng-b2share.eudat.eu/api/records/f7fddf6f111f4362a9e4661294e2b59e"
                    },
                    "updated": "2016-10-24T11:29:27.016900+00:00",
                    "..." : "..."
                  },
                  "..."
                ],
                "total": 32
              },
              "links": {
                "next": "https://trng-b2share.eudat.eu/api/records/?sort=bestmatch&q=community%3Ae9b9792e-79fb-4b07-b6b4-b9c2bd06d095&size=10&page=2",
                "self": "https://trng-b2share.eudat.eu/api/records/?sort=bestmatch&q=community%3Ae9b9792e-79fb-4b07-b6b4-b9c2bd06d095&size=10&page=1"
              }
            }}
            </Returns>
        </Example>

        <Request>{{
            "title": "Search records",
            "description": "Search all the published records for a query string.",
            "path": "/api/records/?q=$QUERY_STRING",
            "returns": "the list of matching records (in JSON format) or an error message."
        }}</Request>
        <Example>
            curl https://$B2SHARE_HOST/api/records/?q=$QUERY_STRING?access_token=$ACCESS_TOKEN
        </Example>

        <Request>{{
            "title": "Search drafts",
            "decription": "Search for all drafts (unpublished records) that are accessible by the requestor. Usually this means own records only.",
            "path": "/api/records/?drafts",
            "returns": "the list of matching drafts (in JSON format) or an error message."
        }}</Request>
        <Example>
            curl https://$B2SHARE_HOST/api/records/?drafts&access_token=$ACCESS_TOKEN
        </Example>

        <Request>{{
            "title": "Get specific record",
            "path": "/api/records/RECORD_ID",
            "description": "List the metadata of the record specified by RECORD_ID",
            "notes": "the access token is only required when a record is not publicly available."
        }}</Request>
        <Example>
            curl https://$B2SHARE_HOST/api/records/47077e3c4b9f4852a40709e338ad4620?access_token=$ACCESS_TOKEN
        </Example>

        <h3>Record creation</h3>

        <Request>{{
            "title": "Create draft record",
            "description": "Create a new record, in the draft state.",
            "path": "/api/records",
            "method": "POST",
            "status": 201,
            "data": "JSON object with basic metadata of the object",
            "returns": "the new draft record metadata including new URL location. \
                Please note that the returned JSON object contains also the URL of the file bucket used for the record. \
                Also note that the URL of the draft record, needed for setting record metadata, will end in '/draft/'"
        }}</Request>
        <Example>
            {'curl -i -H "Content-Type:application/json" -d \'{"titles":[{"title":"TestRest"}], "community":"e9b9792e-79fb-4b07-b6b4-b9c2bd06d095", "open_access":true, "community_specific": {}}\' -X POST https://$B2SHARE_HOST/api/records/?access_token=$ACCESS_TOKEN'}
            <Returns>
            {{
              "created": "2016-10-24T12:21:21.697737+00:00",
              "id": "01826ff3e4974415afdb2574a7ea5a91",
              "links": {
                "files": "https://trng-b2share.eudat.eu/api/files/5594a1bf-1484-4a01-b7d3-f1eb3d2e1dc6",
                "publication": "https://trng-b2share.eudat.eu/api/records/01826ff3e4974415afdb2574a7ea5a91",
                "self": "https://trng-b2share.eudat.eu/api/records/01826ff3e4974415afdb2574a7ea5a91/draft"
              },
              "metadata": {
                "$schema": "https://trng-b2share.eudat.eu/api/communities/e9b9792e-79fb-4b07-b6b4-b9c2bd06d095/schemas/0#/draft_json_schema",
                "community": "e9b9792e-79fb-4b07-b6b4-b9c2bd06d095",
                "community_specific": {},
                "open_access": true,
                "owners": [
                  8
                ],
                "publication_state": "draft",
                "titles":[
                  {
                    "title":"TestRest"
                  }
                ]
              },
              "updated": "2016-10-24T12:21:21.697744+00:00"
            }}
            </Returns>
        </Example>

        <Request>{{
            "title": "Upload file into draft record",
            "description": "To upload a new file into a draft record object, first you need to identify \
            the file bucket URL. This URL can be found in the information returned when \
            querying a draft record, in the 'links/files' section of the returned data.",
            "path": "/api/files/FILE_BUCKET_ID/FILE_NAME",
            "method": "PUT",
            "data": "the file, sent as direct stream",
            "returns": "informations about the newly uploaded file"
        }}</Request>
        <Example>
            curl -X PUT -H 'Accept:application/json' -H 'Content-Type:application/octet-stream' --data-binary @TestFileToBeUploaded.txt https://$B2SHARE_HOST/api/files/$FILE_BUCKET_ID/TestFileToBeUploaded.txt?access_token=$ACCESS_TOKEN
        </Example>

        <Request>{{
            "title": "Delete file from draft record",
            "description": "Send a DELETE request to the file's URL, which is the same URL used for uploading.",
            "path": "/api/files/FILE_BUCKET_ID/FILE_NAME",
            "method": "DELETE",
            "status": 204,
            "returns": "no content"
        }}</Request>
        <Example>
            curl -X DELETE -H 'Accept:application/json' https://$B2SHARE_HOST/api/files/$FILE_BUCKET_ID/FileToBeRemoved.txt?access_token=$ACCESS_TOKEN
        </Example>

        <Request>{{
            "title": "List files of record",
            "description": "List the files uploaded into a record object. For this request you need the <code>FILE_BUCKET_ID</code> which can be found in the metadata of the record.",
            "path": "/api/files/FILE_BUCKET_ID",
            "returns": "information about all the files in the record object"
        }}</Request>
        <Example>
            curl https://$B2SHARE_HOST/api/files/$FILE_BUCKET_ID?access_token=$ACCESS_TOKEN
        </Example>

        <Request>{{
            "title": "Update draft record metadata",
            "description": "This action updates the draft record with new information.",
            "path": "/api/records/RECORD_ID/draft",
            "method": "PATCH",
            "data": "the metadata for the record object to be created, \
                in the JSON patch format (see <a href='http://jsonpatch.com/'>http://jsonpatch.com/</a>)",
            "notes": "The patch format contains one or more JSONPath strings. The root of these paths \
                are the <i>metadata</i> object, as this is the only mutable object. For instance, to \
                update the <i>title</i> field of the record, use this JSONPath: <code>/title</code>"
        }}</Request>
        <Example>
            {'curl -X PATCH -H \'Content-Type:application/json-patch+json\' -d \'[{"op": "add", "path":"/keywords", "value": ["keyword1", "keyword2"]}]\' https://$B2SHARE_HOST/api/records/$RECORD_ID/draft?access_token=$ACCESS_TOKEN'}
            <Returns>
            {{
              "created": "2016-10-24T12:21:21.697737+00:00",
              "id": "01826ff3e4974415afdb2574a7ea5a91",
              "links": {
                "files": "https://trng-b2share.eudat.eu/api/files/5594a1bf-1484-4a01-b7d3-f1eb3d2e1dc6",
                "publication": "https://trng-b2share.eudat.eu/api/records/01826ff3e4974415afdb2574a7ea5a91",
                "self": "https://trng-b2share.eudat.eu/api/records/01826ff3e4974415afdb2574a7ea5a91/draft"
              },
              "metadata": {
                "$schema": "https://trng-b2share.eudat.eu/api/communities/e9b9792e-79fb-4b07-b6b4-b9c2bd06d095/schemas/0#/draft_json_schema",
                "community": "e9b9792e-79fb-4b07-b6b4-b9c2bd06d095",
                "community_specific": {},
                "keywords": [
                  "keyword1",
                  "keyword2"
                ],
                "open_access": true,
                "owners": [
                  8
                ],
                "publication_state": "draft",
                "titles": [
                  {
                    "title": "TestRest"
                  }
                ]
              },
              "updated": "2016-10-24T12:23:59.454951+00:00"
            }}
            </Returns>
        </Example>

        <Request>{{
            "title": "Submit a draft record for publication",
            "description": "This action marks the draft record as complete and submits it for \
                    publication. Currently B2SHARE automatically publishes all the \
                    submitted drafts. Please be advised that publishing the draft \
                    <strong> will make its files immutable</strong>.</p> \
                <p> A draft record is submitted for publication if a special metadata \
                    field, called 'publication_state' is set to 'submitted'. This field \
                    can be set using the PATCH call described above.</p> \
                <p> Depending on the domain specification, other fields could be \
                    required in order to successfully publish a record. In case one of \
                    the required fields is missing the request fails and an error \
                    message is returned with further details.",
            "path": "/api/records/$RECORD_ID/draft",
            "data": "JSON-Patch operation that alters the <code>publication_state</code> metadata field of the record metadata, see example below."
        }}</Request>
        <Example>
            {'curl -X PATCH -H \'Content-Type:application/json-patch+json\' -d \'[{"op": "add", "path":"/publication_state", "value": "submitted"}]\' https://$B2SHARE_HOST/api/records/$RECORD_ID/draft?access_token=$ACCESS_TOKEN'}
            <Returns>
            {{
              "created": "2016-10-24T12:21:21.697737+00:00",
              "id": "01826ff3e4974415afdb2574a7ea5a91",
              "links": {
                "files": "https://trng-b2share.eudat.eu/api/files/5594a1bf-1484-4a01-b7d3-f1eb3d2e1dc6",
                "publication": "https://trng-b2share.eudat.eu/api/records/01826ff3e4974415afdb2574a7ea5a91",
                "self": "https://trng-b2share.eudat.eu/api/records/01826ff3e4974415afdb2574a7ea5a91/draft"
              },
              "metadata": {
                "$schema": "https://trng-b2share.eudat.eu/api/communities/e9b9792e-79fb-4b07-b6b4-b9c2bd06d095/schemas/0#/draft_json_schema",
                "DOI": "10.5072/b2share.cdb15c27-326e-4e95-b812-6b1c6b54c299",
                "community": "e9b9792e-79fb-4b07-b6b4-b9c2bd06d095",
                "community_specific": {},
                "keywords": [
                  "keyword1",
                  "keyword2"
                ],
                "ePIC_PID": "http://hdl.handle.net/11304/2c473f04-d997-47d9-9bdb-d3d71800f870",
                "open_access": true,
                "owners": [
                  8
                ],
                "publication_state": "published",
                "titles": [
                  {
                    "title": "TestRest"
                  }
                ]
              },
              "updated": "2016-10-24T12:26:51.538025+00:00"
            }}
            </Returns>
        </Example>

        <h3>Other requests</h3>

        <Request>{{
            "title": "Report a record as an abuse record",
            "description": "If there is anything wrong with the record users can report it as an abuse record. \
                An email will be send to the related admin and it will be followed up. There are 4 different \
                reasons listed on the report abuse form and the reporter should choose one of:</p> \
                <ol> \
                    <li><p>Abuse or Inappropriate content</p></li> \
                    <li><p>Copyrighted material</p></li> \
                    <li><p>Not research data</p></li> \
                    <li><p>Illegal content</p></li> \
                </ol> \
                <p>The reporter can also send a message to explain more about the problem. It is possible for an anonymous \
                   user to send the report and authentication is not required. </p> \
                <p>Report an abuse record.",
            "method": "POST",
            "path": "/api/records/$RECORD_ID/abuse",
            "data": "JSON object with information about reporter and the reason",
            "returns": "a message that an email was sent and the record is reported"
        }}</Request>
        <Example>
            {'curl -X POST -H \'Content-Type:application/json\' -d \'{"noresearch":true, "abusecontent":false, "copyright":false, "illegalcontent":false,"message":"It is s not research data...", "name":"John Smith", "affiliation":"example University", "email":"j.smith@example.com", "address":"example street", "city":"exampleCity", "country":"exampleCountry", "zipcode":"12345", "phone":"7364017452"}\' https://$B2SHARE_HOST/api/records/$RECORD_ID/abuse?access_token=$ACCESS_TOKEN'}
            <Returns>
                {{
                  "message": "The record is reported."
                }}
            </Returns>
        </Example>

        <Request>{{
            "title": "Send record access request",
            "description": "For the records with restricted access to data, a user (either authenticated or anonymous) can \
                send a request to the record owner and ask for it. Send request to access closed data.",
            "method": "POST",
            "path": "/api/records/$RECORD_ID/accessrequests",
            "data": "JSON object with information about who is sending the request",
            "returns": "a message that an email was sent"
        }}</Request>
        <Example>
            {'curl -X POST -H \'Content-Type:application/json\' -d \'{"message":"explain the request...", "name":"John Smith", "affiliation":"example University", "email":"j.smith@example.com", "address":"example street", "city":"exampleCity", "country":"exampleCountry", "zipcode":"12345", "phone":"7364017452"}\' https://$B2SHARE_HOST/api/records/$RECORD_ID/abuse?access_token=$ACCESS_TOKEN'}
            <Returns>
                {{
                    "message": "An email was sent to the record owner."
                }}
            </Returns>
        </Example>
    </div>
  );
};

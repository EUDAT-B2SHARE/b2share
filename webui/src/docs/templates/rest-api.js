var React = require('react');

module.exports = function(props) {
  return (
    <div className='rest_api'>

<h1>The B2SHARE HTTP REST API</h1>
<p>The B2HARE HTTP REST API can be used for interacting with B2SHARE via external programs, for example for integrating with other web-sites, like e.g. research community portals, or for up- or downloading of large data sets that are not easily handled via a web browser. The REST API can also be used for metadata harvesting.</p>
<h2 id="using-the-api">Using the API</h2>
<p>The REST API is used by letting a program make requests by calling a URL via the standard HTTP protocol’s GET or POST methods.</p>
<h2 id="authentication">Authentication</h2>
<p>Only authenticated users can use the API. Authentication is made by passing an access token in the request. The access token is an encrypted string which can be created in the user profile when logged in to the B2SHARE web user        interface. B2SHARE’s access tokens follow the OAuth 2.0 standard.</p>
<p>To get an access token, login to B2SHARE and click your username, then choose “Account” and then click “Applications” in the menu to the left.</p>
<div>
    <img src="/img/help/rest-api/image00.png" alt="Screenshot 1"/>
</div>
<p>Click on “New token”, enter a name and click “Create”:</p>
<div>
	<img src="/img/help/rest-api/image02.png" alt="Screenshot 2" />
</div>
<p>This will create an access token, your access token is visible under “Access token” on the screen:</p>
<div>
	<img src="/img/help/rest-api/image01.png" alt="Screenshot 3" />
</div>
<p>Please note that this is the only time the access token is visible, so copy it to a safe place. Then click “Save”. The access token is now ready for use. Access tokens can be deleted with the delete button for the particular token,    which is found by clicking the token’s name in the menu “Applications”.</p>
<h2 id="making-requests">Making Requests</h2>
<p>Requests are made by calling an URL with parameters as described below. Each URL consists of a base url and a path. One of the following base urls can be used for the current B2SHARE instance:</p>
<p>https://b2share.eudat.eu - the base url for the production site.</p>
<p>https://trng-b2share.eudat.eu - the base url for the training site. Use this base URL for testing.</p>
<p>Each allowed request is described below as follows:</p>
<p>Description - A description of the function of the request.</p>
<p>URL path - grammar for the allowed paths used together with one of the base URLs above.</p>
<p>HTTP method - whether the HTTP protocols GET or POST method is used.</p>
<p>Example - an example of usage using the program curl from the command line. “example.org” is used as a fictive base URL for the examples. Substitute “example.org” with a base URL from the list above.</p>
<p>Variables in the descriptions:</p>
<p>ACCESS_TOKEN - represents an access token created as described above (mandatory)</p>
<p>COMMUNITY_NAME - name of a user community in B2SHARE (optional)</p>
<p>PAGE_SIZE - size of page for pagination of output data (optional)</p>
<p>PAGE_OFFSET - page offset (page number) for paginated output data (optional)</p>
<p>RECORD_ID - identifier for a specific record</p>
<p>DEPOSITION_ID - identifier for a specific deposition</p>
<p><strong><em>Note</em></strong>: A <strong><em>record</em></strong> is unchangeable and has a PID assigned to it. A user can create a record by first creating a <strong><em>deposition</em></strong>, which is modifiable. Files and       metadata can be placed into a deposition, but not into a record.</p>
<h3 id="list-all-the-records">List all the records</h3>
<p>List all the records, without any filtering.</p>
<ul>
<li><p>HTTP method: GET</p></li>
<li><p>URL path: /api/records</p></li>
<li><p>Required parameters: access_token</p></li>
<li><p>Optional parameters: page_size, page_offset</p></li>
</ul>
<p>Example: curl -i http://example.org/api/records?access_token=LKR35GP7TF&amp;page_size=5&amp;page_offset=2</p>
<h3 id="list-records-per-community">List records per community</h3>
<p>List all records of a specific community.</p>
<ul>
<li><p>URL path: /api/records/COMMUNITY_NAME</p></li>
<li><p>HTTP method: GET</p></li>
<li><p>Required parameters: access_token</p></li>
<li><p>Optional parameters: page_size, page_offset</p></li>
<li><p>Returns: the list of records (in JSON format) or an error message with the list of valid community identifiers if the COMMUNITY_ID is invalid.</p></li>
</ul>
<p>Example: curl -i http://example.org/api/records/BBMRI?access_token=LKR35GP7TF&amp;page_size=10&amp;page_offset=3</p>
<h3 id="list-a-specific-record">List a specific record</h3>
<p>List the metadata of the record specified by RECORD_ID</p>
<ul>
<li><p>URL path: /api/record/RECORD_ID</p></li>
<li><p>HTTP method: GET</p></li>
<li><p>Required parameters: access_token</p></li>
</ul>
<p>Example: curl -i http://example.org/api/record/1?access_token=LKR35GP7TF</p>
<h3 id="create-a-new-deposition">Create a new deposition</h3>
<p>Create a new deposition</p>
<ul>
<li><p>URL path: /api/depositions</p></li>
<li><p>HTTP method: POST</p></li>
<li><p>Required parameters: access_token</p></li>
<li><p>Returns: the URL of the deposition (both as JSON and in the field 'Location' in the http header)</p></li>
</ul>
<p>Example: curl -i -X POST http://example.org/api/depositions?access_token=LKR35GP7TF</p>
<h3 id="upload-a-new-file-into-a-deposition-object">Upload a new file into a deposition object</h3>
<p>Upload a new file into a deposition object</p>
<ul>
<li><p>URL path: /api/deposition/DEPOSITION_ID/files</p></li>
<li><p>HTTP Method: POST</p></li>
<li><p>Required input data: the file, sent as multipart/form-data</p></li>
<li><p>Required parameters: access_token</p></li>
<li><p>Returns: the name and size of the newly uploaded file</p></li>
</ul>
<p>Example: curl -i -X POST -F file=<span >@TestFileToBeUploaded.txt</span> http://example.org/api/deposition/23k85hjfiu2y346/files?access_token=LKR35GP7TF</p>
<h3 id="list-the-files-uploaded-into-a-deposition-object">List the files uploaded into a deposition object</h3>
<p>List the files uploaded into a deposition object</p>
<ul>
<li><p>URL path: /api/deposition/DEPOSITION_ID/files</p></li>
<li><p>Http Method: GET</p></li>
<li><p>Required parameters: access_token</p></li>
<li><p>Returns: the name and size of all the files in the deposition object</p></li>
</ul>
<p>Example: curl -i http://example.org/api/deposition/23k85hjfiu2y346/files?access_token=LKR35GP7TF</p>
<h3 id="commit-deposition">Commit deposition</h3>
<p>This action transforms a deposition into an immutable record.</p>
<ul>
<li><p>URL path: /api/deposition/DEPOSITION_ID/commit</p></li>
<li><p>HTTP Method: POST</p></li>
<li><p>Required input data: the metadata for the record object to be created. This metadata must be sent as a list of fields (key:value pairs). The required fields are:</p>
<ul>
<li><p>domain [string]: the id of the community to which the record belongs</p></li>
<li><p>open_access [boolean]: the access restriction of the new record</p></li>
<li><p>title [string]: the title of the new record</p></li>
<li><p>description [string]: the description of the new record</p></li>
</ul></li>
</ul>
<p>Depending on the domain specification, other fields could be required in order to make a successful commit. The list of all the fields, with their description, multiplicity and controlled vocabulary, is automatically returned to the   user in case one of the required fields is missing.</p>
<ul>
<li><p>Required parameters: access_token</p></li>
<li><p>Returns: the location URL of the new record if the submitted metadata is valid; otherwise, the list of all the metadata fields that can be filled in and details on each one.</p></li>
</ul>
<p>{'Example: curl -i -X POST -H "Content-Type: application/json" -d \u0027{"domain":"generic", "title":"REST Test Title", "description":"REST Test Description", "open_access":"true"}\u0027 http://.../api/deposition/DEPOSITION_ID/commit\u005C?access_token=LKR35GP7TF '}</p>
<h3 id="responses">Responses</h3>
<p>All response bodies are JSON encoded (UTF-8 encoded).</p>
<p>{'A deposition is represented as a JSON object: \u007B "field1": value, … \u007D '}</p>
<p>A collection of depositions is represented as a JSON array of objects:</p>
<p>{'[\u007B "field1": value, ... }, … ]\u007D'}</p>
<p>Timestamps are in UTC and formatted according to ISO 8601:</p>
<p>YYYY-MM-DDTHH:MM:SS+00:00</p>
<h3 id="response-fields">Response Fields</h3>
<div>
	<img src="/img/help/rest-api/response-fields.png" alt="Response fields" />
    </div>
    </div>

  );
};

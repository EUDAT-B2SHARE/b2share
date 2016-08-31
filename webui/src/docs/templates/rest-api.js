var React = require('react');

module.exports = function(props) {
  return (
    <div className='rest_api'>
    	<h1>The B2SHARE HTTP REST API</h1>
    	<p>The B2HARE HTTP REST API can be used for interacting with B2SHARE via
    		external programs, for example for integrating with other web-sites,
    		like e.g. research community portals, or for up- or downloading of
    		large data sets that are not easily handled via a web browser.
    		The REST API can also be used for metadata harvesting.
    	</p>

		<h2>Using the API</h2>
		<p>The REST API is used by letting a program make requests by calling a URL
			via the standard HTTP protocol’s GET or POST methods.
		</p>

		<h2>Authentication</h2>
		<p>Only authenticated users can use the API. Authentication is made by
			passing an access token in the request. The access token is an
			encrypted string which can be created in the user profile when
			logged in to the B2SHARE web user interface. B2SHARE’s access
			tokens follow the OAuth 2.0 standard.</p>
		<p>To get an access token, login to B2SHARE and click your username.
			On the User Profile page, go to the “API Tokens” section, enter
			a name and click “New Token”.</p>
		<p>This will create an access token, visible on the screen.</p>
		<p>Please note that this is the only time the access token is visible,
			so copy it to a safe place.
		</p>


		<h2>Making Requests</h2>
		<p>Requests are made by calling an URL with parameters as described
			below. Each URL consists of a base url and a path. One of the
			following base urls can be used for the current B2SHARE instance:</p>
		<ul>
		<li><code>{window.location.origin}</code> - the base url for the current site.</li>
		<li><code>https://b2share.eudat.eu</code> - the base url for the production site.</li>
		<li><code>https://trng-b2share.eudat.eu</code> - the base url for the training site.
			Use this base URL for testing.</li>
		</ul>

		<p>Each allowed request is described below as follows:</p>
		<ul>
		<li><p>Description - A description of the function of the request.</p></li>
		<li><p>URL path - grammar for the allowed paths used together with one of the base URLs above.</p></li>
		<li><p>HTTP method - whether the HTTP protocols GET or POST method is used.</p></li>
		<li><p>Example - an example of usage using the program curl from the command line.
			“example.org” is used as a fictive base URL for the examples.
			Substitute “example.org” with a base URL from the list above.</p></li>
		<li><p>Variables in the descriptions:</p></li>
		<li><p>ACCESS_TOKEN - represents an access token created as described above (mandatory)</p></li>
		<li><p>COMMUNITY_ID - identifier of a user community in B2SHARE (optional)</p></li>
		<li><p>RECORD_ID - identifier for a specific record, which can be in draft or published state</p></li>
		<li><p>FILE_BUCKET_ID - identifier for a set of files. Each record has its own file set,
			usually found in the links -> files section </p></li>
		</ul>
		<p><strong><em>Note</em></strong>:
			Files in a <strong><em>published record</em></strong> cannot be
			changed. A user can create a record by first creating a
			<strong><em>draft record</em></strong>, which is modifiable.
			Files and metadata can be placed into a draft record, but not into
			a published record.</p>

		<h3>List all the communities</h3>
		<p>List all the communities, without any filtering.</p>
		<ul>
			<li><p>HTTP method: GET</p></li>
			<li><p>URL path: /api/communities</p></li>
			<li><p>Required parameters: access_token</p></li>
			<li><p>Returns: the list of communities (in JSON format) or an error message.</p></li>
		</ul>
		<p>Example: <code>curl -i http://example.org/api/communities/?access_token=LKR35GP7TF</code></p>

		<h3>List all the records</h3>
		<p>List all the records, without any filtering.</p>
		<ul>
			<li><p>HTTP method: GET</p></li>
			<li><p>URL path: /api/records</p></li>
			<li><p>Required parameters: access_token</p></li>
			<li><p>Returns: the list of records (in JSON format) or an error message.</p></li>
		</ul>
		<p>Example: <code>curl -i http://example.org/api/records?access_token=LKR35GP7TF</code></p>

		<h3 id="list-records-per-community">List records per community</h3>
		<p>List all records of a specific community.</p>
		<ul>
			<li><p>URL path: /api/records/?q=community:COMMUNITY_ID</p></li>
			<li><p>HTTP method: GET</p></li>
			<li><p>Required parameters: access_token</p></li>
			<li><p>Returns: the list of records (in JSON format) or an error message.</p></li>
		</ul>
		<p>Example: <code>curl -i http://example.org/api/records/?q=community:e9b9792e-79fb-4b07-b6b4-b9c2bd06d095?access_token=LKR35GP7TF</code></p>

		<h3>List a specific record</h3>
		<p>List the metadata of the record specified by RECORD_ID</p>
		<ul>
			<li><p>URL path: /api/record/RECORD_ID</p></li>
			<li><p>HTTP method: GET</p></li>
			<li><p>Required parameters: access_token</p></li>
		</ul>
		<p>Example: <code>curl -i http://example.org/api/records/47077e3c4b9f4852a40709e338ad4620?access_token=LKR35GP7TF</code></p>

		<h3>Create a new draft record</h3>
		<p>Create a new record, in the draft state.</p>
		<ul>
			<li><p>URL path: /api/records</p></li>
			<li><p>HTTP method: POST</p></li>
			<li><p>Required URL parameter: access_token</p></li>
			<li><p>Required data payload: json object with basic information about the object </p></li>
			<li><p>Returns: the new draft record contents and location. Please note that
				the returned json object contains also the URL of the file bucked used for the record.
				Also note that the URL of the draft record, needed for setting record metadata,
				will end in '/drafts/'</p></li>
		</ul>
		<p>Example: <code>{'curl -i -H "Content-Type:application/json" \
			-d \'{"title":"TestRest", "community":"e9b9792e-79fb-4b07-b6b4-b9c2bd06d095", "open_access":true}\' \
			-X POST http://example.org/api/records/?access_token=LKR35GP7TF'}</code></p>

		<h3>Upload a new file into a draft record</h3>
		<p>To upload a new file into a draft record object, first you need to identify
			the file bucket URL. This URL can be found in the information returned when
			querying a record, in the 'links/files' section of the returned data. </p>
		<ul>
			<li><p>URL path: /api/files/FILE_BUCKET_ID</p></li>
			<li><p>HTTP Method: POST</p></li>
			<li><p>Required input data: the file, sent as direct stream</p></li>
			<li><p>Required parameters: access_token</p></li>
			<li><p>Returns: informations about the newly uploaded file</p></li>
		</ul>
		<p>Example: <code>curl -i -X POST -d @TestFileToBeUploaded.txt http://example.org/api/files/4f947e84-4bf7-4087-86ea-442938b9c2b4/?access_token=LKR35GP7TF</code></p>

		<h3>List the files uploaded into a record object</h3>
		<p>List the files uploaded into a record object</p>
		<ul>
			<li><p>URL path: /api/files/FILE_BUCKET_ID/</p></li>
			<li><p>Http Method: GET</p></li>
			<li><p>Required parameters: access_token</p></li>
			<li><p>Returns: information about all the files in the record object</p></li>
		</ul>
		<p>Example: <code>curl -i http://example.org/api/files/4f947e84-4bf7-4087-86ea-442938b9c2b4/?access_token=LKR35GP7TF</code></p>

		<h3>Updating a draft record</h3>
		<p>This action updates the draft record with new information.</p>
		<ul>
			<li><p>URL path: /api/records/RECORD_ID/</p></li>
			<li><p>HTTP Method: PATCH</p></li>
			<li><p>Required input data: the metadata for the record object to be created,
				in the json patch format (see <a href="http://jsonpatch.com/">http://jsonpatch.com/</a>)
				</p> </li>
		</ul>
		<p>Example: <code>{'curl -v -X PATCH -H \'Content-Type:application/json-patch+json\' \
			-d \'[{"op": "replace", "path":"/description", "value": "This record describes..."}\' \
			http://localhost:5000/api/records/968661eb-c071-4e2b-814a-b5aa5ecd1628'}</code></p>


		<h3>Publishing a draft record</h3>
		<p>This action transforms a draft record into a published record, and will make its files immutable.</p>
		<p>A draft record becomes published if a special metadata field, called 'publication_state' is set to 'published'.
			This field can be set using the PATCH call described above.</p>
		<p>Depending on the domain specification, other fields could be required in order to successfully publish a record.
			The list of all the fields, with their description, multiplicity and controlled vocabulary,
			is automatically returned to the user in case one of the required fields is missing.</p>

		<p>Example: <code>{'curl -v -X PATCH -H \'Content-Type:application/json-patch+json\' \
			-d \'[{"op": "add", "path":"/publication_state", "value": "published"}\' \
			http://localhost:5000/api/records/968661eb-c071-4e2b-814a-b5aa5ecd1628'}</code></p>

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

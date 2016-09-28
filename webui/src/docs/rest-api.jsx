var React = require('react');

const Example = React.createClass({
    render() {
    	const stylePara = {
    		background:'#fafafa',
    		border:'1px solid #eee',
    		padding: '0.5em',
    		margin: '0.5em 1em 0.5em 0',
    	};
    	const styleCode = {
    		background:'none',
    		border: 'none',
    		fontSize:'1em',
    		padding: 0,
    		margin: 0,
    	};
        return (
        	<p style={stylePara}>
        		<code style={styleCode}>
        			<span style={{color:'#888'}}>Example: </span>
        			{ this.props.children }
        		</code>
        	</p>
        );
    }
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

		<h3>Authentication</h3>
		<p>Only authenticated users can use the API. Each HTTP request to the
			server must pass an <code>access_token</code> parameter that
			identifies the user. The <code>access_token</code> is an
			opaque string which can be created in the user profile when
			logged in to the B2SHARE web user interface. B2SHARE’s access
			tokens follow the OAuth 2.0 standard.
		</p>
		<p>To get an access token, login to B2SHARE and click your username.
			On the User Profile page, go to the “API Tokens” section, enter
			a token identification name (e.g. 'api') and click “New Token”.
			This will create an access token, visible on the screen. Please
			note that this is the only time the access token is visible, so
			copy it to a safe place.
		</p>
		<p>The following shell commands will expect that the ACCESS_TOKEN
			environment variable is defined and contains the actual
			access_token. The command to define this variable is:
		</p>
		<Example> export ACCESS_TOKEN='...'</Example>


		<h3>Making Requests</h3>
		<p>Requests are made by calling an URL with parameters as described
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
		<Example> export HOSTNAME='trng-b2share.eudat.eu'</Example>


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

		<h3>Records and drafts</h3>
		<p> Please note that files in a <strong><em>published record</em></strong> cannot be
			changed. A user can create a record by first creating a
			<strong> <em>draft record</em></strong>, which is modifiable.
			Files and metadata can be placed into a draft record, but not into
			a published record.
		</p>

		<h2>The API</h2>

		<h3>List all the communities</h3>
		<p>List all the communities, without any filtering.</p>
		<ul>
			<li><p>HTTP method: GET</p></li>
			<li><p>URL path: /api/communities</p></li>
			<li><p>Required parameters: access_token</p></li>
			<li><p>Returns: the list of communities (in JSON format) or an error message.</p></li>
		</ul>
		<Example>
			curl -i https://$HOSTNAME/api/communities/?access_token=$ACCESS_TOKEN
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
			curl -i https://$HOSTNAME/api/records?access_token=$ACCESS_TOKEN
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
			curl -i https://$HOSTNAME/api/records/?q=community:e9b9792e-79fb-4b07-b6b4-b9c2bd06d095?access_token=$ACCESS_TOKEN
		</Example>

		<h3>List a specific record</h3>
		<p>List the metadata of the record specified by RECORD_ID</p>
		<ul>
			<li><p>URL path: /api/record/RECORD_ID</p></li>
			<li><p>HTTP method: GET</p></li>
			<li><p>Required parameters: access_token</p></li>
		</ul>
		<Example>
			curl -i https://$HOSTNAME/api/records/47077e3c4b9f4852a40709e338ad4620?access_token=$ACCESS_TOKEN
		</Example>

		<h3>Create a new draft record</h3>
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
			{'curl -i -H "Content-Type:application/json" \
			-d \'{"title":"TestRest", "community":"e9b9792e-79fb-4b07-b6b4-b9c2bd06d095", "open_access":true}\' \
			-X POST https://$HOSTNAME/api/records/?access_token=$ACCESS_TOKEN'}
		</Example>

		<h3>Upload a new file into a draft record</h3>
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
			curl -i -X PUT -d @TestFileToBeUploaded.txt https://$HOSTNAME/api/files/$FILE_BUCKET_ID/TestFileToBeUploaded.txt?access_token=$ACCESS_TOKEN
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
			curl -i https://$HOSTNAME/api/files/$FILE_BUCKET_ID?access_token=$ACCESS_TOKEN
		</Example>

		<h3>Updating a draft record</h3>
		<p>This action updates the draft record with new information.</p>
		<ul>
			<li><p>URL path: /api/records/RECORD_ID/</p></li>
			<li><p>HTTP Method: PATCH</p></li>
			<li><p>Required input data: the metadata for the record object to be created,
				in the json patch format (see <a href="http://jsonpatch.com/">http://jsonpatch.com/</a>)
				</p> </li>
		</ul>
		<Example>
			{'curl -v -X PATCH -H \'Content-Type:application/json-patch+json\' \
			-d \'[{"op": "replace", "path":"/description", "value": "This record describes..."}\' \
			https://$HOSTNAME/api/records/$RECORD_ID/draft?access_token=$ACCESS_TOKEN'}
		</Example>


		<h3>Publishing a draft record</h3>
		<p>This action transforms a draft record into a published record, and will make its files immutable.</p>
		<p>A draft record becomes published if a special metadata field, called 'publication_state' is set to 'published'.
			This field can be set using the PATCH call described above.</p>
		<p>Depending on the domain specification, other fields could be required in order to successfully publish a record.
			The list of all the fields, with their description, multiplicity and controlled vocabulary,
			is automatically returned to the user in case one of the required fields is missing.</p>

		<Example>
			{'curl -v -X PATCH -H \'Content-Type:application/json-patch+json\' \
			-d \'[{"op": "add", "path":"/publication_state", "value": "published"}\' \
			https://$HOSTNAME/api/records/$RECORD_ID/draft?access_token=$ACCESS_TOKEN'}
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

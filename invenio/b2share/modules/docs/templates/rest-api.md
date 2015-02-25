[](#)[](#)

The B2SHARE HTTP REST API
=========================

The B2HARE HTTP REST API can be used for interacting with B2SHARE via external programs, for example for integrating with other web-sites, like e.g. research community portals, or for up- or downloading of large
data sets that are not easily handled via a web browser. The REST API can also be used for metadata harvesting.

Using the API
-------------

The REST API is used by letting a program make requests by calling a URL via the standard HTTP protocol’s GET or POST methods.

Authentication
--------------

Only authenticated users can use the API. Authentication is made by passing an access token in the request. The access token is an encrypted string which can be created in the user profile when logged in to the
B2SHARE web user interface. B2SHARE’s access tokens follow the OAuth 2.0 standard.

To get an access token, login to B2SHARE and click your username, then choose “Account” and then click “Applications” in the menu to the left.

![Screenshot 1](img/rest-api/image00.png)

Click on “New token”, enter a name and click “Create”:

![Screenshot 2](img/rest-api/image02.png)

This will create an access token, your access token is visible under “Access token” on the screen:

![Screenshot 3](img/rest-api/image01.png)

Please note that this is the only time the access token is visible, so copy it to a safe place. Then click “Save”. The access token is now ready for use. Access tokens can be deleted with the delete button for
the particular token, which is found by clicking the token’s name in the menu “Applications”.

Making Requests
---------------

Requests are made by calling an URL with parameters as described below. Each URL consists of a base url and a path. One of the following base urls can be used for the current B2SHARE instance:

https://b2share.eudat.eu \- the base url for the production site.

https://trng-b2share.eudat.eu \- the base url for the training site. Use this base URL for testing.

Each allowed request is described below as follows:

Description - A description of the function of the request.

URL path - grammar for the allowed paths used together with one of the
base URLs above.

HTTP method - whether the HTTP protocols GET or POST method is used.

Example - an example of usage using the program curl from the command
line. “example.org” is used as a fictive base URL for the examples.
Substitute “example.org” with a base URL from the list above.

Variables in the descriptions:

ACCESS\_TOKEN - represents an access token created as described above (mandatory)

COMMUNITY\_NAME - name of a user community in B2SHARE (optional)

PAGE\_SIZE - size of page for pagination of output data (optional)

PAGE\_OFFSET - page offset (page number) for paginated output data (optional)

RECORD\_ID - identifier for a specific record

DEPOSITION\_ID - identifier for a specific deposition

***Note***: A ***record*** is unchangeable and has a PID assigned to it. A user can create a record by first creating a ***deposition***, which is modifiable. Files and metadata can be placed into a deposition, but not into a record.

### List all the records

List all the records, without any filtering.

* HTTP method: GET

* URL path: /api/records

* Required parameters: access\_token

* Optional parameters: page_size, page_offset

Example: curl -i http://example.org/api/records?access\_token=LKR35GP7TF&page_size=5&page_offset=2

### List records per community

List all records of a specific community.

* URL path: /api/records/COMMUNITY\_NAME

* HTTP method: GET

* Required parameters: access\_token

* Optional parameters: page_size, page_offset

* Returns: the list of records (in JSON format) or an error message with the list of valid community identifiers if the COMMUNITY_ID is invalid.

Example: curl -i http://example.org/api/records/BBMRI?access\_token=LKR35GP7TF&page_size=10&page_offset=3

### List a specific record

List the metadata of the record specified by RECORD_ID

* URL path: /api/record/RECORD_ID

* HTTP method: GET

* Required parameters: access\_token

Example: curl -i http://example.org/api/record/1?access\_token=LKR35GP7TF

### Create a new deposition

Create a new deposition

* URL path: /api/depositions

* HTTP method: POST

* Required parameters: access\_token

* Returns: the URL of the deposition (both as JSON and in the field 'Location' in the http header)

Example: curl -i -X POST http://example.org/api/depositions?access\_token=LKR35GP7TF

### Upload a new file into a deposition object

Upload a new file into a deposition object

* URL path: /api/deposition/DEPOSITION_ID/files

* HTTP Method: POST

* Required input data: the file, sent as multipart/form-data

* Required parameters: access\_token

* Returns: the name and size of the newly uploaded file

Example: curl -i -X POST -F file=@TestFileToBeUploaded.txt http://example.org/api/deposition/23k85hjfiu2y346/files?access\_token=LKR35GP7TF

### List the files uploaded into a deposition object

List the files uploaded into a deposition object

* URL path: /api/deposition/DEPOSITION_ID/files

* Http Method: GET

* Required parameters: access\_token

* Returns: the name and size of all the files in the deposition object

Example: curl -i http://example.org/api/deposition/23k85hjfiu2y346/files?access\_token=LKR35GP7TF

### Commit deposition

This action transforms a deposition into an immutable record.

* URL path: /api/deposition/DEPOSITION_ID/commit

* HTTP Method: POST

* Required input data: the metadata for the record object to be created. This metadata must be sent as a list of fields (key:value pairs). The required fields are:

    - domain [string]: the id of the community to which the record belongs

    - open_access [boolean]: the access restriction of the new record

    - title [string]: the title of the new record

    - description [string]: the description of the new record

Depending on the domain specification, other fields could be required in order to make a successful commit. The list of all the fields, with their description, multiplicity and controlled vocabulary, is automatically returned to the user in case one of the required fields is missing.

* Required parameters: access\_token

* Returns: the location URL of the new record if the submitted metadata is valid; otherwise, the list of all the metadata fields that can be filled in and details on each one.

Example: curl -i -X POST -H "Content-Type: application/json" -d '{"domain":"generic", "title":"REST Test Title", "description":"REST Test Description", "open_access":"true"}' http://.../api/deposition/DEPOSITION_ID/commit\?access\_token=LKR35GP7TF

### Responses

All response bodies are JSON encoded (UTF-8 encoded).

A deposition is represented as a JSON object: { "field1": value, … }

A collection of depositions is represented as a JSON array of objects:

[{ "field1": value, ... }, … ]

Timestamps are in UTC and formatted according to ISO 8601:

YYYY-MM-DDTHH:MM:SS+00:00

### Response Fields

![Response fields](img/rest-api/response-fields.png)

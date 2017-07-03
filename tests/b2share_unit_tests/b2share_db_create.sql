

-----------------------------------------------
--- Create an empty B2SHARE 2.0.1 database ----
-----------------------------------------------

--- NOTES: This script was created with B2SHARE 2.0.1 database dump

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.2
-- Dumped by pg_dump version 9.6.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: access_actionsroles; Type: TABLE; Schema: public;
--

CREATE TABLE access_actionsroles (
    id integer NOT NULL,
    action character varying(80),
    exclude boolean DEFAULT false NOT NULL,
    argument character varying(255),
    role_id integer NOT NULL
);



--
-- Name: access_actionsroles_id_seq; Type: SEQUENCE; Schema: public;
--

CREATE SEQUENCE access_actionsroles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: access_actionsroles_id_seq; Type: SEQUENCE OWNED BY; Schema: public;
--

ALTER SEQUENCE access_actionsroles_id_seq OWNED BY access_actionsroles.id;


--
-- Name: access_actionsusers; Type: TABLE; Schema: public;
--

CREATE TABLE access_actionsusers (
    id integer NOT NULL,
    action character varying(80),
    exclude boolean DEFAULT false NOT NULL,
    argument character varying(255),
    user_id integer
);



--
-- Name: access_actionsusers_id_seq; Type: SEQUENCE; Schema: public;
--

CREATE SEQUENCE access_actionsusers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: access_actionsusers_id_seq; Type: SEQUENCE OWNED BY; Schema: public;
--

ALTER SEQUENCE access_actionsusers_id_seq OWNED BY access_actionsusers.id;


--
-- Name: accounts_role; Type: TABLE; Schema: public;
--

CREATE TABLE accounts_role (
    id integer NOT NULL,
    name character varying(80),
    description character varying(255)
);



--
-- Name: accounts_role_id_seq; Type: SEQUENCE; Schema: public;
--

CREATE SEQUENCE accounts_role_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: accounts_role_id_seq; Type: SEQUENCE OWNED BY; Schema: public;
--

ALTER SEQUENCE accounts_role_id_seq OWNED BY accounts_role.id;


--
-- Name: accounts_user; Type: TABLE; Schema: public;
--

CREATE TABLE accounts_user (
    id integer NOT NULL,
    email character varying(255),
    password character varying(255),
    active boolean,
    confirmed_at timestamp without time zone,
    last_login_at timestamp without time zone,
    current_login_at timestamp without time zone,
    last_login_ip character varying(50),
    current_login_ip character varying(50),
    login_count integer
);



--
-- Name: accounts_user_id_seq; Type: SEQUENCE; Schema: public;
--

CREATE SEQUENCE accounts_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: accounts_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public;
--

ALTER SEQUENCE accounts_user_id_seq OWNED BY accounts_user.id;


--
-- Name: accounts_user_session_activity; Type: TABLE; Schema: public;
--

CREATE TABLE accounts_user_session_activity (
    created timestamp without time zone NOT NULL,
    updated timestamp without time zone NOT NULL,
    sid_s character varying(255) NOT NULL,
    user_id integer
);



--
-- Name: accounts_userrole; Type: TABLE; Schema: public;
--

CREATE TABLE accounts_userrole (
    user_id integer,
    role_id integer
);



--
-- Name: b2share_block_schema; Type: TABLE; Schema: public;
--

CREATE TABLE b2share_block_schema (
    created timestamp without time zone NOT NULL,
    updated timestamp without time zone NOT NULL,
    id uuid NOT NULL,
    name character varying(200) NOT NULL,
    deprecated boolean NOT NULL,
    community uuid NOT NULL,
    CONSTRAINT b2share_block_schema_name_check CHECK (((length((name)::text) > 2) AND (length((name)::text) <= 200)))
);



--
-- Name: b2share_block_schema_version; Type: TABLE; Schema: public;
--

CREATE TABLE b2share_block_schema_version (
    block_schema uuid NOT NULL,
    version integer NOT NULL,
    released timestamp without time zone NOT NULL,
    json_schema text
);



--
-- Name: b2share_community; Type: TABLE; Schema: public;
--

CREATE TABLE b2share_community (
    created timestamp without time zone NOT NULL,
    updated timestamp without time zone NOT NULL,
    id uuid NOT NULL,
    name character varying(80) NOT NULL,
    description character varying(2000) NOT NULL,
    logo character varying(300),
    deleted boolean DEFAULT false NOT NULL,
    publication_workflow character varying(80) NOT NULL,
    restricted_submission boolean DEFAULT false NOT NULL
);



--
-- Name: b2share_community_schema_version; Type: TABLE; Schema: public;
--

CREATE TABLE b2share_community_schema_version (
    community uuid NOT NULL,
    version integer NOT NULL,
    released timestamp without time zone NOT NULL,
    root_schema integer NOT NULL,
    community_schema character varying NOT NULL
);



--
-- Name: b2share_root_schema_version; Type: TABLE; Schema: public;
--

CREATE TABLE b2share_root_schema_version (
    version integer NOT NULL,
    json_schema text NOT NULL
);



--
-- Name: files_bucket; Type: TABLE; Schema: public;
--

CREATE TABLE files_bucket (
    created timestamp without time zone NOT NULL,
    updated timestamp without time zone NOT NULL,
    id uuid NOT NULL,
    default_location integer NOT NULL,
    default_storage_class character varying(1) NOT NULL,
    size bigint NOT NULL,
    quota_size bigint,
    max_file_size bigint,
    locked boolean NOT NULL,
    deleted boolean NOT NULL
);



--
-- Name: files_buckettags; Type: TABLE; Schema: public;
--

CREATE TABLE files_buckettags (
    bucket_id uuid NOT NULL,
    key character varying(255) NOT NULL,
    value text NOT NULL
);



--
-- Name: files_files; Type: TABLE; Schema: public;
--

CREATE TABLE files_files (
    created timestamp without time zone NOT NULL,
    updated timestamp without time zone NOT NULL,
    id uuid NOT NULL,
    uri text,
    storage_class character varying(1),
    size bigint,
    checksum character varying(255),
    readable boolean NOT NULL,
    writable boolean NOT NULL,
    last_check_at timestamp without time zone,
    last_check boolean NOT NULL
);



--
-- Name: files_location; Type: TABLE; Schema: public;
--

CREATE TABLE files_location (
    created timestamp without time zone NOT NULL,
    updated timestamp without time zone NOT NULL,
    id integer NOT NULL,
    name character varying(20) NOT NULL,
    uri character varying(255) NOT NULL,
    "default" boolean NOT NULL
);



--
-- Name: files_location_id_seq; Type: SEQUENCE; Schema: public;
--

CREATE SEQUENCE files_location_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: files_location_id_seq; Type: SEQUENCE OWNED BY; Schema: public;
--

ALTER SEQUENCE files_location_id_seq OWNED BY files_location.id;


--
-- Name: files_multipartobject; Type: TABLE; Schema: public;
--

CREATE TABLE files_multipartobject (
    created timestamp without time zone NOT NULL,
    updated timestamp without time zone NOT NULL,
    upload_id uuid NOT NULL,
    bucket_id uuid,
    key text,
    file_id uuid NOT NULL,
    chunk_size integer,
    size bigint,
    completed boolean NOT NULL
);



--
-- Name: files_multipartobject_part; Type: TABLE; Schema: public;
--

CREATE TABLE files_multipartobject_part (
    created timestamp without time zone NOT NULL,
    updated timestamp without time zone NOT NULL,
    upload_id uuid NOT NULL,
    part_number integer NOT NULL,
    checksum character varying(255)
);



--
-- Name: files_object; Type: TABLE; Schema: public;
--

CREATE TABLE files_object (
    created timestamp without time zone NOT NULL,
    updated timestamp without time zone NOT NULL,
    bucket_id uuid NOT NULL,
    key text NOT NULL,
    version_id uuid NOT NULL,
    file_id uuid,
    _mimetype character varying(255),
    is_head boolean NOT NULL
);



--
-- Name: oaiserver_set; Type: TABLE; Schema: public;
--

CREATE TABLE oaiserver_set (
    created timestamp without time zone NOT NULL,
    updated timestamp without time zone NOT NULL,
    id integer NOT NULL,
    spec character varying(255) NOT NULL,
    name character varying(255),
    description text,
    search_pattern text
);



--
-- Name: oaiserver_set_id_seq; Type: SEQUENCE; Schema: public;
--

CREATE SEQUENCE oaiserver_set_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: oaiserver_set_id_seq; Type: SEQUENCE OWNED BY; Schema: public;
--

ALTER SEQUENCE oaiserver_set_id_seq OWNED BY oaiserver_set.id;


--
-- Name: oauth2server_client; Type: TABLE; Schema: public;
--

CREATE TABLE oauth2server_client (
    name character varying(40),
    description text,
    website text,
    user_id integer,
    client_id character varying(255) NOT NULL,
    client_secret character varying(255) NOT NULL,
    is_confidential boolean,
    is_internal boolean,
    _redirect_uris text,
    _default_scopes text
);



--
-- Name: oauth2server_token; Type: TABLE; Schema: public;
--

CREATE TABLE oauth2server_token (
    id integer NOT NULL,
    client_id character varying(255) NOT NULL,
    user_id integer,
    token_type character varying(255),
    access_token bytea,
    refresh_token bytea,
    expires timestamp without time zone,
    _scopes text,
    is_personal boolean,
    is_internal boolean
);



--
-- Name: oauth2server_token_id_seq; Type: SEQUENCE; Schema: public;
--

CREATE SEQUENCE oauth2server_token_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: oauth2server_token_id_seq; Type: SEQUENCE OWNED BY; Schema: public;
--

ALTER SEQUENCE oauth2server_token_id_seq OWNED BY oauth2server_token.id;


--
-- Name: oauthclient_remoteaccount; Type: TABLE; Schema: public;
--

CREATE TABLE oauthclient_remoteaccount (
    id integer NOT NULL,
    user_id integer NOT NULL,
    client_id character varying(255) NOT NULL,
    extra_data json NOT NULL
);



--
-- Name: oauthclient_remoteaccount_id_seq; Type: SEQUENCE; Schema: public;
--

CREATE SEQUENCE oauthclient_remoteaccount_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: oauthclient_remoteaccount_id_seq; Type: SEQUENCE OWNED BY; Schema: public;
--

ALTER SEQUENCE oauthclient_remoteaccount_id_seq OWNED BY oauthclient_remoteaccount.id;


--
-- Name: oauthclient_remotetoken; Type: TABLE; Schema: public;
--

CREATE TABLE oauthclient_remotetoken (
    id_remote_account integer NOT NULL,
    token_type character varying(40) NOT NULL,
    access_token bytea NOT NULL,
    secret text NOT NULL
);



--
-- Name: oauthclient_useridentity; Type: TABLE; Schema: public;
--

CREATE TABLE oauthclient_useridentity (
    id character varying(255) NOT NULL,
    method character varying(255) NOT NULL,
    id_user integer NOT NULL
);



--
-- Name: pidstore_pid; Type: TABLE; Schema: public;
--

CREATE TABLE pidstore_pid (
    created timestamp without time zone NOT NULL,
    updated timestamp without time zone NOT NULL,
    id integer NOT NULL,
    pid_type character varying(6) NOT NULL,
    pid_value character varying(255) NOT NULL,
    pid_provider character varying(8),
    status character(1) NOT NULL,
    object_type character varying(3),
    object_uuid uuid
);



--
-- Name: pidstore_pid_id_seq; Type: SEQUENCE; Schema: public;
--

CREATE SEQUENCE pidstore_pid_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: pidstore_pid_id_seq; Type: SEQUENCE OWNED BY; Schema: public;
--

ALTER SEQUENCE pidstore_pid_id_seq OWNED BY pidstore_pid.id;


--
-- Name: pidstore_recid; Type: TABLE; Schema: public;
--

CREATE TABLE pidstore_recid (
    recid bigint NOT NULL
);



--
-- Name: pidstore_recid_recid_seq; Type: SEQUENCE; Schema: public;
--

CREATE SEQUENCE pidstore_recid_recid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: pidstore_recid_recid_seq; Type: SEQUENCE OWNED BY; Schema: public;
--

ALTER SEQUENCE pidstore_recid_recid_seq OWNED BY pidstore_recid.recid;


--
-- Name: pidstore_redirect; Type: TABLE; Schema: public;
--

CREATE TABLE pidstore_redirect (
    created timestamp without time zone NOT NULL,
    updated timestamp without time zone NOT NULL,
    id uuid NOT NULL,
    pid_id integer NOT NULL
);



--
-- Name: records_buckets; Type: TABLE; Schema: public;
--

CREATE TABLE records_buckets (
    record_id uuid NOT NULL,
    bucket_id uuid NOT NULL
);



--
-- Name: records_metadata; Type: TABLE; Schema: public;
--

CREATE TABLE records_metadata (
    created timestamp without time zone NOT NULL,
    updated timestamp without time zone NOT NULL,
    id uuid NOT NULL,
    json json,
    version_id integer NOT NULL
);



--
-- Name: records_metadata_version; Type: TABLE; Schema: public;
--

CREATE TABLE records_metadata_version (
    created timestamp without time zone,
    updated timestamp without time zone,
    id uuid NOT NULL,
    json json,
    version_id integer,
    transaction_id bigint NOT NULL,
    end_transaction_id bigint,
    operation_type smallint NOT NULL
);



--
-- Name: transaction; Type: TABLE; Schema: public;
--

CREATE TABLE transaction (
    issued_at timestamp without time zone,
    id bigint NOT NULL,
    remote_addr character varying(50),
    user_id integer
);



--
-- Name: transaction_id_seq; Type: SEQUENCE; Schema: public;
--

CREATE SEQUENCE transaction_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: access_actionsroles id; Type: DEFAULT; Schema: public;
--

ALTER TABLE ONLY access_actionsroles ALTER COLUMN id SET DEFAULT nextval('access_actionsroles_id_seq'::regclass);


--
-- Name: access_actionsusers id; Type: DEFAULT; Schema: public;
--

ALTER TABLE ONLY access_actionsusers ALTER COLUMN id SET DEFAULT nextval('access_actionsusers_id_seq'::regclass);


--
-- Name: accounts_role id; Type: DEFAULT; Schema: public;
--

ALTER TABLE ONLY accounts_role ALTER COLUMN id SET DEFAULT nextval('accounts_role_id_seq'::regclass);


--
-- Name: accounts_user id; Type: DEFAULT; Schema: public;
--

ALTER TABLE ONLY accounts_user ALTER COLUMN id SET DEFAULT nextval('accounts_user_id_seq'::regclass);


--
-- Name: files_location id; Type: DEFAULT; Schema: public;
--

ALTER TABLE ONLY files_location ALTER COLUMN id SET DEFAULT nextval('files_location_id_seq'::regclass);


--
-- Name: oaiserver_set id; Type: DEFAULT; Schema: public;
--

ALTER TABLE ONLY oaiserver_set ALTER COLUMN id SET DEFAULT nextval('oaiserver_set_id_seq'::regclass);


--
-- Name: oauth2server_token id; Type: DEFAULT; Schema: public;
--

ALTER TABLE ONLY oauth2server_token ALTER COLUMN id SET DEFAULT nextval('oauth2server_token_id_seq'::regclass);


--
-- Name: oauthclient_remoteaccount id; Type: DEFAULT; Schema: public;
--

ALTER TABLE ONLY oauthclient_remoteaccount ALTER COLUMN id SET DEFAULT nextval('oauthclient_remoteaccount_id_seq'::regclass);


--
-- Name: pidstore_pid id; Type: DEFAULT; Schema: public;
--

ALTER TABLE ONLY pidstore_pid ALTER COLUMN id SET DEFAULT nextval('pidstore_pid_id_seq'::regclass);


--
-- Name: pidstore_recid recid; Type: DEFAULT; Schema: public;
--

ALTER TABLE ONLY pidstore_recid ALTER COLUMN recid SET DEFAULT nextval('pidstore_recid_recid_seq'::regclass);


--
-- Data for Name: access_actionsroles; Type: TABLE DATA; Schema: public;
--



--
-- Name: access_actionsroles_id_seq; Type: SEQUENCE SET; Schema: public;
--

SELECT pg_catalog.setval('access_actionsroles_id_seq', 1, false);


--
-- Data for Name: access_actionsusers; Type: TABLE DATA; Schema: public;
--



--
-- Name: access_actionsusers_id_seq; Type: SEQUENCE SET; Schema: public;
--

SELECT pg_catalog.setval('access_actionsusers_id_seq', 1, false);


--
-- Data for Name: accounts_role; Type: TABLE DATA; Schema: public;
--



--
-- Name: accounts_role_id_seq; Type: SEQUENCE SET; Schema: public;
--

SELECT pg_catalog.setval('accounts_role_id_seq', 1, false);


--
-- Data for Name: accounts_user; Type: TABLE DATA; Schema: public;
--



--
-- Name: accounts_user_id_seq; Type: SEQUENCE SET; Schema: public;
--

SELECT pg_catalog.setval('accounts_user_id_seq', 1, false);


--
-- Data for Name: accounts_user_session_activity; Type: TABLE DATA; Schema: public;
--



--
-- Data for Name: accounts_userrole; Type: TABLE DATA; Schema: public;
--



--
-- Data for Name: b2share_block_schema; Type: TABLE DATA; Schema: public;
--



--
-- Data for Name: b2share_block_schema_version; Type: TABLE DATA; Schema: public;
--



--
-- Data for Name: b2share_community; Type: TABLE DATA; Schema: public;
--



--
-- Data for Name: b2share_community_schema_version; Type: TABLE DATA; Schema: public;
--



--
-- Data for Name: b2share_root_schema_version; Type: TABLE DATA; Schema: public;
--



--
-- Data for Name: files_bucket; Type: TABLE DATA; Schema: public;
--



--
-- Data for Name: files_buckettags; Type: TABLE DATA; Schema: public;
--



--
-- Data for Name: files_files; Type: TABLE DATA; Schema: public;
--



--
-- Data for Name: files_location; Type: TABLE DATA; Schema: public;
--



--
-- Name: files_location_id_seq; Type: SEQUENCE SET; Schema: public;
--

SELECT pg_catalog.setval('files_location_id_seq', 1, false);


--
-- Data for Name: files_multipartobject; Type: TABLE DATA; Schema: public;
--



--
-- Data for Name: files_multipartobject_part; Type: TABLE DATA; Schema: public;
--



--
-- Data for Name: files_object; Type: TABLE DATA; Schema: public;
--



--
-- Data for Name: oaiserver_set; Type: TABLE DATA; Schema: public;
--



--
-- Name: oaiserver_set_id_seq; Type: SEQUENCE SET; Schema: public;
--

SELECT pg_catalog.setval('oaiserver_set_id_seq', 1, false);


--
-- Data for Name: oauth2server_client; Type: TABLE DATA; Schema: public;
--



--
-- Data for Name: oauth2server_token; Type: TABLE DATA; Schema: public;
--



--
-- Name: oauth2server_token_id_seq; Type: SEQUENCE SET; Schema: public;
--

SELECT pg_catalog.setval('oauth2server_token_id_seq', 1, false);


--
-- Data for Name: oauthclient_remoteaccount; Type: TABLE DATA; Schema: public;
--



--
-- Name: oauthclient_remoteaccount_id_seq; Type: SEQUENCE SET; Schema: public;
--

SELECT pg_catalog.setval('oauthclient_remoteaccount_id_seq', 1, false);


--
-- Data for Name: oauthclient_remotetoken; Type: TABLE DATA; Schema: public;
--



--
-- Data for Name: oauthclient_useridentity; Type: TABLE DATA; Schema: public;
--



--
-- Data for Name: pidstore_pid; Type: TABLE DATA; Schema: public;
--



--
-- Name: pidstore_pid_id_seq; Type: SEQUENCE SET; Schema: public;
--

SELECT pg_catalog.setval('pidstore_pid_id_seq', 1, false);


--
-- Data for Name: pidstore_recid; Type: TABLE DATA; Schema: public;
--



--
-- Name: pidstore_recid_recid_seq; Type: SEQUENCE SET; Schema: public;
--

SELECT pg_catalog.setval('pidstore_recid_recid_seq', 1, false);


--
-- Data for Name: pidstore_redirect; Type: TABLE DATA; Schema: public;
--



--
-- Data for Name: records_buckets; Type: TABLE DATA; Schema: public;
--



--
-- Data for Name: records_metadata; Type: TABLE DATA; Schema: public;
--



--
-- Data for Name: records_metadata_version; Type: TABLE DATA; Schema: public;
--



--
-- Data for Name: transaction; Type: TABLE DATA; Schema: public;
--



--
-- Name: transaction_id_seq; Type: SEQUENCE SET; Schema: public;
--

SELECT pg_catalog.setval('transaction_id_seq', 1, false);


--
-- Name: access_actionsroles access_actionsroles_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY access_actionsroles
    ADD CONSTRAINT access_actionsroles_pkey PRIMARY KEY (id);


--
-- Name: access_actionsroles access_actionsroles_unique; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY access_actionsroles
    ADD CONSTRAINT access_actionsroles_unique UNIQUE (action, exclude, argument, role_id);


--
-- Name: access_actionsusers access_actionsusers_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY access_actionsusers
    ADD CONSTRAINT access_actionsusers_pkey PRIMARY KEY (id);


--
-- Name: access_actionsusers access_actionsusers_unique; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY access_actionsusers
    ADD CONSTRAINT access_actionsusers_unique UNIQUE (action, exclude, argument, user_id);


--
-- Name: accounts_role accounts_role_name_key; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY accounts_role
    ADD CONSTRAINT accounts_role_name_key UNIQUE (name);


--
-- Name: accounts_role accounts_role_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY accounts_role
    ADD CONSTRAINT accounts_role_pkey PRIMARY KEY (id);


--
-- Name: accounts_user accounts_user_email_key; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY accounts_user
    ADD CONSTRAINT accounts_user_email_key UNIQUE (email);


--
-- Name: accounts_user accounts_user_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY accounts_user
    ADD CONSTRAINT accounts_user_pkey PRIMARY KEY (id);


--
-- Name: accounts_user_session_activity accounts_user_session_activity_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY accounts_user_session_activity
    ADD CONSTRAINT accounts_user_session_activity_pkey PRIMARY KEY (sid_s);


--
-- Name: b2share_block_schema b2share_block_schema_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY b2share_block_schema
    ADD CONSTRAINT b2share_block_schema_pkey PRIMARY KEY (id);


--
-- Name: b2share_block_schema_version b2share_block_schema_version_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY b2share_block_schema_version
    ADD CONSTRAINT b2share_block_schema_version_pkey PRIMARY KEY (block_schema, version);


--
-- Name: b2share_community b2share_community_name_key; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY b2share_community
    ADD CONSTRAINT b2share_community_name_key UNIQUE (name);


--
-- Name: b2share_community b2share_community_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY b2share_community
    ADD CONSTRAINT b2share_community_pkey PRIMARY KEY (id);


--
-- Name: b2share_community_schema_version b2share_community_schema_version_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY b2share_community_schema_version
    ADD CONSTRAINT b2share_community_schema_version_pkey PRIMARY KEY (community, version);


--
-- Name: b2share_root_schema_version b2share_root_schema_version_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY b2share_root_schema_version
    ADD CONSTRAINT b2share_root_schema_version_pkey PRIMARY KEY (version);


--
-- Name: files_bucket files_bucket_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY files_bucket
    ADD CONSTRAINT files_bucket_pkey PRIMARY KEY (id);


--
-- Name: files_buckettags files_buckettags_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY files_buckettags
    ADD CONSTRAINT files_buckettags_pkey PRIMARY KEY (bucket_id, key);


--
-- Name: files_files files_files_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY files_files
    ADD CONSTRAINT files_files_pkey PRIMARY KEY (id);


--
-- Name: files_files files_files_uri_key; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY files_files
    ADD CONSTRAINT files_files_uri_key UNIQUE (uri);


--
-- Name: files_location files_location_name_key; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY files_location
    ADD CONSTRAINT files_location_name_key UNIQUE (name);


--
-- Name: files_location files_location_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY files_location
    ADD CONSTRAINT files_location_pkey PRIMARY KEY (id);


--
-- Name: files_multipartobject_part files_multipartobject_part_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY files_multipartobject_part
    ADD CONSTRAINT files_multipartobject_part_pkey PRIMARY KEY (upload_id, part_number);


--
-- Name: files_multipartobject files_multipartobject_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY files_multipartobject
    ADD CONSTRAINT files_multipartobject_pkey PRIMARY KEY (upload_id);


--
-- Name: files_object files_object_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY files_object
    ADD CONSTRAINT files_object_pkey PRIMARY KEY (bucket_id, key, version_id);


--
-- Name: oaiserver_set oaiserver_set_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY oaiserver_set
    ADD CONSTRAINT oaiserver_set_pkey PRIMARY KEY (id);


--
-- Name: oaiserver_set oaiserver_set_spec_key; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY oaiserver_set
    ADD CONSTRAINT oaiserver_set_spec_key UNIQUE (spec);


--
-- Name: oauth2server_client oauth2server_client_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY oauth2server_client
    ADD CONSTRAINT oauth2server_client_pkey PRIMARY KEY (client_id);


--
-- Name: oauth2server_token oauth2server_token_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY oauth2server_token
    ADD CONSTRAINT oauth2server_token_pkey PRIMARY KEY (id);


--
-- Name: oauthclient_remoteaccount oauthclient_remoteaccount_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY oauthclient_remoteaccount
    ADD CONSTRAINT oauthclient_remoteaccount_pkey PRIMARY KEY (id);


--
-- Name: oauthclient_remoteaccount oauthclient_remoteaccount_user_id_client_id_key; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY oauthclient_remoteaccount
    ADD CONSTRAINT oauthclient_remoteaccount_user_id_client_id_key UNIQUE (user_id, client_id);


--
-- Name: oauthclient_remotetoken oauthclient_remotetoken_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY oauthclient_remotetoken
    ADD CONSTRAINT oauthclient_remotetoken_pkey PRIMARY KEY (id_remote_account, token_type);


--
-- Name: oauthclient_useridentity oauthclient_useridentity_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY oauthclient_useridentity
    ADD CONSTRAINT oauthclient_useridentity_pkey PRIMARY KEY (id, method);


--
-- Name: pidstore_pid pidstore_pid_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY pidstore_pid
    ADD CONSTRAINT pidstore_pid_pkey PRIMARY KEY (id);


--
-- Name: pidstore_recid pidstore_recid_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY pidstore_recid
    ADD CONSTRAINT pidstore_recid_pkey PRIMARY KEY (recid);


--
-- Name: pidstore_redirect pidstore_redirect_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY pidstore_redirect
    ADD CONSTRAINT pidstore_redirect_pkey PRIMARY KEY (id);


--
-- Name: records_buckets records_buckets_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY records_buckets
    ADD CONSTRAINT records_buckets_pkey PRIMARY KEY (record_id, bucket_id);


--
-- Name: records_metadata records_metadata_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY records_metadata
    ADD CONSTRAINT records_metadata_pkey PRIMARY KEY (id);


--
-- Name: records_metadata_version records_metadata_version_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY records_metadata_version
    ADD CONSTRAINT records_metadata_version_pkey PRIMARY KEY (id, transaction_id);


--
-- Name: transaction transaction_pkey; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY transaction
    ADD CONSTRAINT transaction_pkey PRIMARY KEY (id);


--
-- Name: files_multipartobject uix_item; Type: CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY files_multipartobject
    ADD CONSTRAINT uix_item UNIQUE (upload_id, bucket_id, key);


--
-- Name: idx_object; Type: INDEX; Schema: public;
--

CREATE INDEX idx_object ON pidstore_pid USING btree (object_type, object_uuid);


--
-- Name: idx_status; Type: INDEX; Schema: public;
--

CREATE INDEX idx_status ON pidstore_pid USING btree (status);


--
-- Name: ix_access_actionsroles_action; Type: INDEX; Schema: public;
--

CREATE INDEX ix_access_actionsroles_action ON access_actionsroles USING btree (action);


--
-- Name: ix_access_actionsroles_argument; Type: INDEX; Schema: public;
--

CREATE INDEX ix_access_actionsroles_argument ON access_actionsroles USING btree (argument);


--
-- Name: ix_access_actionsusers_action; Type: INDEX; Schema: public;
--

CREATE INDEX ix_access_actionsusers_action ON access_actionsusers USING btree (action);


--
-- Name: ix_access_actionsusers_argument; Type: INDEX; Schema: public;
--

CREATE INDEX ix_access_actionsusers_argument ON access_actionsusers USING btree (argument);


--
-- Name: ix_files_object__mimetype; Type: INDEX; Schema: public;
--

CREATE INDEX ix_files_object__mimetype ON files_object USING btree (_mimetype);


--
-- Name: ix_oaiserver_set_name; Type: INDEX; Schema: public;
--

CREATE INDEX ix_oaiserver_set_name ON oaiserver_set USING btree (name);


--
-- Name: ix_oauth2server_client_client_secret; Type: INDEX; Schema: public;
--

CREATE UNIQUE INDEX ix_oauth2server_client_client_secret ON oauth2server_client USING btree (client_secret);


--
-- Name: ix_oauth2server_token_access_token; Type: INDEX; Schema: public;
--

CREATE UNIQUE INDEX ix_oauth2server_token_access_token ON oauth2server_token USING btree (access_token);


--
-- Name: ix_oauth2server_token_refresh_token; Type: INDEX; Schema: public;
--

CREATE UNIQUE INDEX ix_oauth2server_token_refresh_token ON oauth2server_token USING btree (refresh_token);


--
-- Name: ix_records_metadata_version_end_transaction_id; Type: INDEX; Schema: public;
--

CREATE INDEX ix_records_metadata_version_end_transaction_id ON records_metadata_version USING btree (end_transaction_id);


--
-- Name: ix_records_metadata_version_operation_type; Type: INDEX; Schema: public;
--

CREATE INDEX ix_records_metadata_version_operation_type ON records_metadata_version USING btree (operation_type);


--
-- Name: ix_records_metadata_version_transaction_id; Type: INDEX; Schema: public;
--

CREATE INDEX ix_records_metadata_version_transaction_id ON records_metadata_version USING btree (transaction_id);


--
-- Name: ix_transaction_user_id; Type: INDEX; Schema: public;
--

CREATE INDEX ix_transaction_user_id ON transaction USING btree (user_id);


--
-- Name: uidx_type_pid; Type: INDEX; Schema: public;
--

CREATE UNIQUE INDEX uidx_type_pid ON pidstore_pid USING btree (pid_type, pid_value);


--
-- Name: useridentity_id_user_method; Type: INDEX; Schema: public;
--

CREATE UNIQUE INDEX useridentity_id_user_method ON oauthclient_useridentity USING btree (id_user, method);


--
-- Name: access_actionsroles access_actionsroles_role_id_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY access_actionsroles
    ADD CONSTRAINT access_actionsroles_role_id_fkey FOREIGN KEY (role_id) REFERENCES accounts_role(id);


--
-- Name: access_actionsusers access_actionsusers_user_id_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY access_actionsusers
    ADD CONSTRAINT access_actionsusers_user_id_fkey FOREIGN KEY (user_id) REFERENCES accounts_user(id);


--
-- Name: accounts_user_session_activity accounts_user_session_activity_user_id_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY accounts_user_session_activity
    ADD CONSTRAINT accounts_user_session_activity_user_id_fkey FOREIGN KEY (user_id) REFERENCES accounts_user(id);


--
-- Name: accounts_userrole accounts_userrole_role_id_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY accounts_userrole
    ADD CONSTRAINT accounts_userrole_role_id_fkey FOREIGN KEY (role_id) REFERENCES accounts_role(id);


--
-- Name: accounts_userrole accounts_userrole_user_id_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY accounts_userrole
    ADD CONSTRAINT accounts_userrole_user_id_fkey FOREIGN KEY (user_id) REFERENCES accounts_user(id);


--
-- Name: b2share_block_schema b2share_block_schema_community_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY b2share_block_schema
    ADD CONSTRAINT b2share_block_schema_community_fkey FOREIGN KEY (community) REFERENCES b2share_community(id);


--
-- Name: b2share_block_schema_version b2share_block_schema_version_block_schema_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY b2share_block_schema_version
    ADD CONSTRAINT b2share_block_schema_version_block_schema_fkey FOREIGN KEY (block_schema) REFERENCES b2share_block_schema(id);


--
-- Name: b2share_community_schema_version b2share_community_schema_version_community_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY b2share_community_schema_version
    ADD CONSTRAINT b2share_community_schema_version_community_fkey FOREIGN KEY (community) REFERENCES b2share_community(id);


--
-- Name: b2share_community_schema_version b2share_community_schema_version_root_schema_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY b2share_community_schema_version
    ADD CONSTRAINT b2share_community_schema_version_root_schema_fkey FOREIGN KEY (root_schema) REFERENCES b2share_root_schema_version(version);


--
-- Name: files_bucket files_bucket_default_location_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY files_bucket
    ADD CONSTRAINT files_bucket_default_location_fkey FOREIGN KEY (default_location) REFERENCES files_location(id) ON DELETE RESTRICT;


--
-- Name: files_buckettags files_buckettags_bucket_id_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY files_buckettags
    ADD CONSTRAINT files_buckettags_bucket_id_fkey FOREIGN KEY (bucket_id) REFERENCES files_bucket(id) ON DELETE CASCADE;


--
-- Name: files_multipartobject files_multipartobject_bucket_id_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY files_multipartobject
    ADD CONSTRAINT files_multipartobject_bucket_id_fkey FOREIGN KEY (bucket_id) REFERENCES files_bucket(id) ON DELETE RESTRICT;


--
-- Name: files_multipartobject files_multipartobject_file_id_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY files_multipartobject
    ADD CONSTRAINT files_multipartobject_file_id_fkey FOREIGN KEY (file_id) REFERENCES files_files(id) ON DELETE RESTRICT;


--
-- Name: files_multipartobject_part files_multipartobject_part_upload_id_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY files_multipartobject_part
    ADD CONSTRAINT files_multipartobject_part_upload_id_fkey FOREIGN KEY (upload_id) REFERENCES files_multipartobject(upload_id) ON DELETE RESTRICT;


--
-- Name: files_object files_object_bucket_id_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY files_object
    ADD CONSTRAINT files_object_bucket_id_fkey FOREIGN KEY (bucket_id) REFERENCES files_bucket(id) ON DELETE RESTRICT;


--
-- Name: files_object files_object_file_id_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY files_object
    ADD CONSTRAINT files_object_file_id_fkey FOREIGN KEY (file_id) REFERENCES files_files(id) ON DELETE RESTRICT;


--
-- Name: oauth2server_client oauth2server_client_user_id_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY oauth2server_client
    ADD CONSTRAINT oauth2server_client_user_id_fkey FOREIGN KEY (user_id) REFERENCES accounts_user(id);


--
-- Name: oauth2server_token oauth2server_token_client_id_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY oauth2server_token
    ADD CONSTRAINT oauth2server_token_client_id_fkey FOREIGN KEY (client_id) REFERENCES oauth2server_client(client_id);


--
-- Name: oauth2server_token oauth2server_token_user_id_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY oauth2server_token
    ADD CONSTRAINT oauth2server_token_user_id_fkey FOREIGN KEY (user_id) REFERENCES accounts_user(id);


--
-- Name: oauthclient_remoteaccount oauthclient_remoteaccount_user_id_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY oauthclient_remoteaccount
    ADD CONSTRAINT oauthclient_remoteaccount_user_id_fkey FOREIGN KEY (user_id) REFERENCES accounts_user(id);


--
-- Name: oauthclient_remotetoken oauthclient_remotetoken_id_remote_account_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY oauthclient_remotetoken
    ADD CONSTRAINT oauthclient_remotetoken_id_remote_account_fkey FOREIGN KEY (id_remote_account) REFERENCES oauthclient_remoteaccount(id);


--
-- Name: oauthclient_useridentity oauthclient_useridentity_id_user_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY oauthclient_useridentity
    ADD CONSTRAINT oauthclient_useridentity_id_user_fkey FOREIGN KEY (id_user) REFERENCES accounts_user(id);


--
-- Name: pidstore_redirect pidstore_redirect_pid_id_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY pidstore_redirect
    ADD CONSTRAINT pidstore_redirect_pid_id_fkey FOREIGN KEY (pid_id) REFERENCES pidstore_pid(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: records_buckets records_buckets_bucket_id_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY records_buckets
    ADD CONSTRAINT records_buckets_bucket_id_fkey FOREIGN KEY (bucket_id) REFERENCES files_bucket(id);


--
-- Name: records_buckets records_buckets_record_id_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY records_buckets
    ADD CONSTRAINT records_buckets_record_id_fkey FOREIGN KEY (record_id) REFERENCES records_metadata(id);


--
-- Name: transaction transaction_user_id_fkey; Type: FK CONSTRAINT; Schema: public;
--

ALTER TABLE ONLY transaction
    ADD CONSTRAINT transaction_user_id_fkey FOREIGN KEY (user_id) REFERENCES accounts_user(id);


--
-- PostgreSQL database dump complete
--


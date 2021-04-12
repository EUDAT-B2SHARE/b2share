
-------------------------------------------------------------
--- Adds data to the db created by b2share_db_create.sql ----
-------------------------------------------------------------

--- NOTES: This script was created with B2SHARE 2.0.1 demonstration
--- database dump. The JSON Schemas URLs have been modified in order
--- to work with tests (http://.../api/... => http://.../... because
--- there is no UI app as the one created by the b2share factory.py)

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

SET search_path = public, pg_catalog;

--
-- Data for Name: accounts_role; Type: TABLE DATA; Schema: public; Owner: b2share
--

INSERT INTO accounts_role (id, name, description) VALUES (1, 'com:c4234f93da964d2fa2c8fa83d0775212:admin', 'Admin role of the community "Aalto"');
INSERT INTO accounts_role (id, name, description) VALUES (2, 'com:c4234f93da964d2fa2c8fa83d0775212:member', 'Member role of the community "Aalto"');
INSERT INTO accounts_role (id, name, description) VALUES (3, 'com:99916f6f9a2c4feba3426552ac7f1529:admin', 'Admin role of the community "BBMRI"');
-- This is commented on purpose so that we can check that the permissions are correctly fixed if they are missing
-- INSERT INTO accounts_role (id, name, description) VALUES (4, 'com:99916f6f9a2c4feba3426552ac7f1529:member', 'Member role of the community "BBMRI"');
INSERT INTO accounts_role (id, name, description) VALUES (5, 'com:0afede872bf24d89867ed2ee57251c62:admin', 'Admin role of the community "CLARIN"');
INSERT INTO accounts_role (id, name, description) VALUES (6, 'com:0afede872bf24d89867ed2ee57251c62:member', 'Member role of the community "CLARIN"');
INSERT INTO accounts_role (id, name, description) VALUES (7, 'com:94a9567e2fba46778fdea8b68bdb63e8:admin', 'Admin role of the community "DRIHM"');
INSERT INTO accounts_role (id, name, description) VALUES (8, 'com:94a9567e2fba46778fdea8b68bdb63e8:member', 'Member role of the community "DRIHM"');
INSERT INTO accounts_role (id, name, description) VALUES (9, 'com:b344f92acd0e4e4caa0928b5f95f7e41:admin', 'Admin role of the community "EISCAT"');
INSERT INTO accounts_role (id, name, description) VALUES (10, 'com:b344f92acd0e4e4caa0928b5f95f7e41:member', 'Member role of the community "EISCAT"');
INSERT INTO accounts_role (id, name, description) VALUES (11, 'com:e9b9792e79fb4b07b6b4b9c2bd06d095:admin', 'Admin role of the community "EUDAT"');
INSERT INTO accounts_role (id, name, description) VALUES (12, 'com:e9b9792e79fb4b07b6b4b9c2bd06d095:member', 'Member role of the community "EUDAT"');
INSERT INTO accounts_role (id, name, description) VALUES (13, 'com:893fad89dc4a4f1ba9ba4240aa18e12b:admin', 'Admin role of the community "EUON"');
INSERT INTO accounts_role (id, name, description) VALUES (14, 'com:893fad89dc4a4f1ba9ba4240aa18e12b:member', 'Member role of the community "EUON"');
INSERT INTO accounts_role (id, name, description) VALUES (15, 'com:867c4e6792274b6f8595c97d37e9de61:admin', 'Admin role of the community "GBIF"');
INSERT INTO accounts_role (id, name, description) VALUES (16, 'com:867c4e6792274b6f8595c97d37e9de61:member', 'Member role of the community "GBIF"');
INSERT INTO accounts_role (id, name, description) VALUES (17, 'com:d952913c451e4b5c817ed578dc8a4469:admin', 'Admin role of the community "LTER"');
INSERT INTO accounts_role (id, name, description) VALUES (18, 'com:d952913c451e4b5c817ed578dc8a4469:member', 'Member role of the community "LTER"');
INSERT INTO accounts_role (id, name, description) VALUES (19, 'com:4ba7c0fd143543139c134d888d60321a:admin', 'Admin role of the community "NRM"');
INSERT INTO accounts_role (id, name, description) VALUES (20, 'com:4ba7c0fd143543139c134d888d60321a:member', 'Member role of the community "NRM"');
INSERT INTO accounts_role (id, name, description) VALUES (21, 'com:8d963a295e19492b8cfe97da4f54fad2:admin', 'Admin role of the community "RDA"');
INSERT INTO accounts_role (id, name, description) VALUES (22, 'com:8d963a295e19492b8cfe97da4f54fad2:member', 'Member role of the community "RDA"');


--
-- Data for Name: access_actionsroles; Type: TABLE DATA; Schema: public; Owner: b2share
-- --

-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (1, 'create-deposit', false, '{"community":"c4234f93-da96-4d2f-a2c8-fa83d0775212","publication_state":"draft"}', 2);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (2, 'create-deposit', false, '{"community":"c4234f93-da96-4d2f-a2c8-fa83d0775212","publication_state":"draft"}', 1);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (3, 'read-deposit', false, '{"community":"c4234f93-da96-4d2f-a2c8-fa83d0775212","publication_state":"submitted"}', 1);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (4, 'read-deposit', false, '{"community":"c4234f93-da96-4d2f-a2c8-fa83d0775212","publication_state":"published"}', 1);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (5, 'update-deposit-metadata', false, '{"community":"c4234f93-da96-4d2f-a2c8-fa83d0775212","publication_state":"submitted"}', 1);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (6, 'update-deposit-publication-state', false, '{"community":"c4234f93-da96-4d2f-a2c8-fa83d0775212","new_state":"published","old_state":"submitted"}', 1);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (7, 'update-deposit-publication-state', false, '{"community":"c4234f93-da96-4d2f-a2c8-fa83d0775212","new_state":"draft","old_state":"submitted"}', 1);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (8, 'update-record-metadata', false, '{"community":"c4234f93-da96-4d2f-a2c8-fa83d0775212"}', 1);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (9, 'assign_role', false, '{"community":"c4234f93-da96-4d2f-a2c8-fa83d0775212","role":"None"}', 1);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (10, 'accounts-search', false, NULL, 1);
-- -- This is commented on purpose so that we can check that the permissions are correctly fixed if they are missing
-- -- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (11, 'create-deposit', false, '{"community":"99916f6f-9a2c-4feb-a342-6552ac7f1529","publication_state":"draft"}', 4);
-- -- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (12, 'create-deposit', false, '{"community":"99916f6f-9a2c-4feb-a342-6552ac7f1529","publication_state":"draft"}', 3);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (13, 'read-deposit', false, '{"community":"99916f6f-9a2c-4feb-a342-6552ac7f1529","publication_state":"submitted"}', 3);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (14, 'read-deposit', false, '{"community":"99916f6f-9a2c-4feb-a342-6552ac7f1529","publication_state":"published"}', 3);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (15, 'update-deposit-metadata', false, '{"community":"99916f6f-9a2c-4feb-a342-6552ac7f1529","publication_state":"submitted"}', 3);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (16, 'update-deposit-publication-state', false, '{"community":"99916f6f-9a2c-4feb-a342-6552ac7f1529","new_state":"published","old_state":"submitted"}', 3);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (17, 'update-deposit-publication-state', false, '{"community":"99916f6f-9a2c-4feb-a342-6552ac7f1529","new_state":"draft","old_state":"submitted"}', 3);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (18, 'update-record-metadata', false, '{"community":"99916f6f-9a2c-4feb-a342-6552ac7f1529"}', 3);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (19, 'assign_role', false, '{"community":"99916f6f-9a2c-4feb-a342-6552ac7f1529","role":"None"}', 3);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (20, 'accounts-search', false, NULL, 3);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (21, 'create-deposit', false, '{"community":"0afede87-2bf2-4d89-867e-d2ee57251c62","publication_state":"draft"}', 6);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (22, 'create-deposit', false, '{"community":"0afede87-2bf2-4d89-867e-d2ee57251c62","publication_state":"draft"}', 5);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (23, 'read-deposit', false, '{"community":"0afede87-2bf2-4d89-867e-d2ee57251c62","publication_state":"submitted"}', 5);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (24, 'read-deposit', false, '{"community":"0afede87-2bf2-4d89-867e-d2ee57251c62","publication_state":"published"}', 5);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (25, 'update-deposit-metadata', false, '{"community":"0afede87-2bf2-4d89-867e-d2ee57251c62","publication_state":"submitted"}', 5);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (26, 'update-deposit-publication-state', false, '{"community":"0afede87-2bf2-4d89-867e-d2ee57251c62","new_state":"published","old_state":"submitted"}', 5);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (27, 'update-deposit-publication-state', false, '{"community":"0afede87-2bf2-4d89-867e-d2ee57251c62","new_state":"draft","old_state":"submitted"}', 5);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (28, 'update-record-metadata', false, '{"community":"0afede87-2bf2-4d89-867e-d2ee57251c62"}', 5);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (29, 'assign_role', false, '{"community":"0afede87-2bf2-4d89-867e-d2ee57251c62","role":"None"}', 5);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (30, 'accounts-search', false, NULL, 5);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (31, 'create-deposit', false, '{"community":"94a9567e-2fba-4677-8fde-a8b68bdb63e8","publication_state":"draft"}', 8);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (32, 'create-deposit', false, '{"community":"94a9567e-2fba-4677-8fde-a8b68bdb63e8","publication_state":"draft"}', 7);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (33, 'read-deposit', false, '{"community":"94a9567e-2fba-4677-8fde-a8b68bdb63e8","publication_state":"submitted"}', 7);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (34, 'read-deposit', false, '{"community":"94a9567e-2fba-4677-8fde-a8b68bdb63e8","publication_state":"published"}', 7);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (35, 'update-deposit-metadata', false, '{"community":"94a9567e-2fba-4677-8fde-a8b68bdb63e8","publication_state":"submitted"}', 7);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (36, 'update-deposit-publication-state', false, '{"community":"94a9567e-2fba-4677-8fde-a8b68bdb63e8","new_state":"published","old_state":"submitted"}', 7);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (37, 'update-deposit-publication-state', false, '{"community":"94a9567e-2fba-4677-8fde-a8b68bdb63e8","new_state":"draft","old_state":"submitted"}', 7);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (38, 'update-record-metadata', false, '{"community":"94a9567e-2fba-4677-8fde-a8b68bdb63e8"}', 7);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (39, 'assign_role', false, '{"community":"94a9567e-2fba-4677-8fde-a8b68bdb63e8","role":"None"}', 7);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (40, 'accounts-search', false, NULL, 7);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (41, 'create-deposit', false, '{"community":"b344f92a-cd0e-4e4c-aa09-28b5f95f7e41","publication_state":"draft"}', 10);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (42, 'create-deposit', false, '{"community":"b344f92a-cd0e-4e4c-aa09-28b5f95f7e41","publication_state":"draft"}', 9);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (43, 'read-deposit', false, '{"community":"b344f92a-cd0e-4e4c-aa09-28b5f95f7e41","publication_state":"submitted"}', 9);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (44, 'read-deposit', false, '{"community":"b344f92a-cd0e-4e4c-aa09-28b5f95f7e41","publication_state":"published"}', 9);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (45, 'update-deposit-metadata', false, '{"community":"b344f92a-cd0e-4e4c-aa09-28b5f95f7e41","publication_state":"submitted"}', 9);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (46, 'update-deposit-publication-state', false, '{"community":"b344f92a-cd0e-4e4c-aa09-28b5f95f7e41","new_state":"published","old_state":"submitted"}', 9);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (47, 'update-deposit-publication-state', false, '{"community":"b344f92a-cd0e-4e4c-aa09-28b5f95f7e41","new_state":"draft","old_state":"submitted"}', 9);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (48, 'update-record-metadata', false, '{"community":"b344f92a-cd0e-4e4c-aa09-28b5f95f7e41"}', 9);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (49, 'assign_role', false, '{"community":"b344f92a-cd0e-4e4c-aa09-28b5f95f7e41","role":"None"}', 9);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (50, 'accounts-search', false, NULL, 9);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (51, 'create-deposit', false, '{"community":"e9b9792e-79fb-4b07-b6b4-b9c2bd06d095","publication_state":"draft"}', 12);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (52, 'create-deposit', false, '{"community":"e9b9792e-79fb-4b07-b6b4-b9c2bd06d095","publication_state":"draft"}', 11);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (53, 'read-deposit', false, '{"community":"e9b9792e-79fb-4b07-b6b4-b9c2bd06d095","publication_state":"submitted"}', 11);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (54, 'read-deposit', false, '{"community":"e9b9792e-79fb-4b07-b6b4-b9c2bd06d095","publication_state":"published"}', 11);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (55, 'update-deposit-metadata', false, '{"community":"e9b9792e-79fb-4b07-b6b4-b9c2bd06d095","publication_state":"submitted"}', 11);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (56, 'update-deposit-publication-state', false, '{"community":"e9b9792e-79fb-4b07-b6b4-b9c2bd06d095","new_state":"published","old_state":"submitted"}', 11);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (57, 'update-deposit-publication-state', false, '{"community":"e9b9792e-79fb-4b07-b6b4-b9c2bd06d095","new_state":"draft","old_state":"submitted"}', 11);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (58, 'update-record-metadata', false, '{"community":"e9b9792e-79fb-4b07-b6b4-b9c2bd06d095"}', 11);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (59, 'assign_role', false, '{"community":"e9b9792e-79fb-4b07-b6b4-b9c2bd06d095","role":"None"}', 11);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (60, 'accounts-search', false, NULL, 11);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (61, 'create-deposit', false, '{"community":"893fad89-dc4a-4f1b-a9ba-4240aa18e12b","publication_state":"draft"}', 14);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (62, 'create-deposit', false, '{"community":"893fad89-dc4a-4f1b-a9ba-4240aa18e12b","publication_state":"draft"}', 13);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (63, 'read-deposit', false, '{"community":"893fad89-dc4a-4f1b-a9ba-4240aa18e12b","publication_state":"submitted"}', 13);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (64, 'read-deposit', false, '{"community":"893fad89-dc4a-4f1b-a9ba-4240aa18e12b","publication_state":"published"}', 13);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (65, 'update-deposit-metadata', false, '{"community":"893fad89-dc4a-4f1b-a9ba-4240aa18e12b","publication_state":"submitted"}', 13);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (66, 'update-deposit-publication-state', false, '{"community":"893fad89-dc4a-4f1b-a9ba-4240aa18e12b","new_state":"published","old_state":"submitted"}', 13);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (67, 'update-deposit-publication-state', false, '{"community":"893fad89-dc4a-4f1b-a9ba-4240aa18e12b","new_state":"draft","old_state":"submitted"}', 13);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (68, 'update-record-metadata', false, '{"community":"893fad89-dc4a-4f1b-a9ba-4240aa18e12b"}', 13);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (69, 'assign_role', false, '{"community":"893fad89-dc4a-4f1b-a9ba-4240aa18e12b","role":"None"}', 13);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (70, 'accounts-search', false, NULL, 13);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (71, 'create-deposit', false, '{"community":"867c4e67-9227-4b6f-8595-c97d37e9de61","publication_state":"draft"}', 16);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (72, 'create-deposit', false, '{"community":"867c4e67-9227-4b6f-8595-c97d37e9de61","publication_state":"draft"}', 15);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (73, 'read-deposit', false, '{"community":"867c4e67-9227-4b6f-8595-c97d37e9de61","publication_state":"submitted"}', 15);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (74, 'read-deposit', false, '{"community":"867c4e67-9227-4b6f-8595-c97d37e9de61","publication_state":"published"}', 15);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (75, 'update-deposit-metadata', false, '{"community":"867c4e67-9227-4b6f-8595-c97d37e9de61","publication_state":"submitted"}', 15);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (76, 'update-deposit-publication-state', false, '{"community":"867c4e67-9227-4b6f-8595-c97d37e9de61","new_state":"published","old_state":"submitted"}', 15);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (77, 'update-deposit-publication-state', false, '{"community":"867c4e67-9227-4b6f-8595-c97d37e9de61","new_state":"draft","old_state":"submitted"}', 15);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (78, 'update-record-metadata', false, '{"community":"867c4e67-9227-4b6f-8595-c97d37e9de61"}', 15);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (79, 'assign_role', false, '{"community":"867c4e67-9227-4b6f-8595-c97d37e9de61","role":"None"}', 15);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (80, 'accounts-search', false, NULL, 15);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (81, 'create-deposit', false, '{"community":"d952913c-451e-4b5c-817e-d578dc8a4469","publication_state":"draft"}', 18);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (82, 'create-deposit', false, '{"community":"d952913c-451e-4b5c-817e-d578dc8a4469","publication_state":"draft"}', 17);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (83, 'read-deposit', false, '{"community":"d952913c-451e-4b5c-817e-d578dc8a4469","publication_state":"submitted"}', 17);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (84, 'read-deposit', false, '{"community":"d952913c-451e-4b5c-817e-d578dc8a4469","publication_state":"published"}', 17);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (85, 'update-deposit-metadata', false, '{"community":"d952913c-451e-4b5c-817e-d578dc8a4469","publication_state":"submitted"}', 17);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (86, 'update-deposit-publication-state', false, '{"community":"d952913c-451e-4b5c-817e-d578dc8a4469","new_state":"published","old_state":"submitted"}', 17);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (87, 'update-deposit-publication-state', false, '{"community":"d952913c-451e-4b5c-817e-d578dc8a4469","new_state":"draft","old_state":"submitted"}', 17);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (88, 'update-record-metadata', false, '{"community":"d952913c-451e-4b5c-817e-d578dc8a4469"}', 17);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (89, 'assign_role', false, '{"community":"d952913c-451e-4b5c-817e-d578dc8a4469","role":"None"}', 17);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (90, 'accounts-search', false, NULL, 17);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (91, 'create-deposit', false, '{"community":"4ba7c0fd-1435-4313-9c13-4d888d60321a","publication_state":"draft"}', 20);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (92, 'create-deposit', false, '{"community":"4ba7c0fd-1435-4313-9c13-4d888d60321a","publication_state":"draft"}', 19);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (93, 'read-deposit', false, '{"community":"4ba7c0fd-1435-4313-9c13-4d888d60321a","publication_state":"submitted"}', 19);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (94, 'read-deposit', false, '{"community":"4ba7c0fd-1435-4313-9c13-4d888d60321a","publication_state":"published"}', 19);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (95, 'update-deposit-metadata', false, '{"community":"4ba7c0fd-1435-4313-9c13-4d888d60321a","publication_state":"submitted"}', 19);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (96, 'update-deposit-publication-state', false, '{"community":"4ba7c0fd-1435-4313-9c13-4d888d60321a","new_state":"published","old_state":"submitted"}', 19);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (97, 'update-deposit-publication-state', false, '{"community":"4ba7c0fd-1435-4313-9c13-4d888d60321a","new_state":"draft","old_state":"submitted"}', 19);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (98, 'update-record-metadata', false, '{"community":"4ba7c0fd-1435-4313-9c13-4d888d60321a"}', 19);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (99, 'assign_role', false, '{"community":"4ba7c0fd-1435-4313-9c13-4d888d60321a","role":"None"}', 19);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (100, 'accounts-search', false, NULL, 19);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (101, 'create-deposit', false, '{"community":"8d963a29-5e19-492b-8cfe-97da4f54fad2","publication_state":"draft"}', 22);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (102, 'create-deposit', false, '{"community":"8d963a29-5e19-492b-8cfe-97da4f54fad2","publication_state":"draft"}', 21);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (103, 'read-deposit', false, '{"community":"8d963a29-5e19-492b-8cfe-97da4f54fad2","publication_state":"submitted"}', 21);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (104, 'read-deposit', false, '{"community":"8d963a29-5e19-492b-8cfe-97da4f54fad2","publication_state":"published"}', 21);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (105, 'update-deposit-metadata', false, '{"community":"8d963a29-5e19-492b-8cfe-97da4f54fad2","publication_state":"submitted"}', 21);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (106, 'update-deposit-publication-state', false, '{"community":"8d963a29-5e19-492b-8cfe-97da4f54fad2","new_state":"published","old_state":"submitted"}', 21);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (107, 'update-deposit-publication-state', false, '{"community":"8d963a29-5e19-492b-8cfe-97da4f54fad2","new_state":"draft","old_state":"submitted"}', 21);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (108, 'update-record-metadata', false, '{"community":"8d963a29-5e19-492b-8cfe-97da4f54fad2"}', 21);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (109, 'assign_role', false, '{"community":"8d963a29-5e19-492b-8cfe-97da4f54fad2","role":"None"}', 21);
-- INSERT INTO access_actionsroles (id, action, exclude, argument, role_id) VALUES (110, 'accounts-search', false, NULL, 21);


--
-- Name: access_actionsroles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: b2share
--

SELECT pg_catalog.setval('access_actionsroles_id_seq', 110, true);


--
-- Data for Name: accounts_user; Type: TABLE DATA; Schema: public; Owner: b2share
--

INSERT INTO accounts_user (id, email, password, active, confirmed_at, last_login_at, current_login_at, last_login_ip, current_login_ip, login_count) VALUES (1, 'firstuser@example.com', NULL, true, NULL, NULL, NULL, NULL, NULL, NULL);


--
-- Data for Name: access_actionsusers; Type: TABLE DATA; Schema: public; Owner: b2share
--



--
-- Name: access_actionsusers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: b2share
--

SELECT pg_catalog.setval('access_actionsusers_id_seq', 1, false);


--
-- Name: accounts_role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: b2share
--

SELECT pg_catalog.setval('accounts_role_id_seq', 22, true);


--
-- Name: accounts_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: b2share
--

SELECT pg_catalog.setval('accounts_user_id_seq', 1, true);


--
-- Data for Name: accounts_user_session_activity; Type: TABLE DATA; Schema: public; Owner: b2share
--



--
-- Data for Name: accounts_userrole; Type: TABLE DATA; Schema: public; Owner: b2share
--



--
-- Data for Name: b2share_community; Type: TABLE DATA; Schema: public; Owner: b2share
--

INSERT INTO b2share_community (created, updated, id, name, description, logo, deleted, publication_workflow, restricted_submission) VALUES ('2017-11-03 09:04:44.064654', '2017-11-03 09:04:44.064684', 'c4234f93-da96-4d2f-a2c8-fa83d0775212', 'Aalto', 'Aalto University', '/img/communities/aalto.jpg', false, 'direct_publish', true);
INSERT INTO b2share_community (created, updated, id, name, description, logo, deleted, publication_workflow, restricted_submission) VALUES ('2017-11-03 09:04:44.163812', '2017-11-03 09:04:44.16384', '99916f6f-9a2c-4feb-a342-6552ac7f1529', 'BBMRI', 'Biomedical Research.', '/img/communities/bbmri.png', false, 'direct_publish', false);
INSERT INTO b2share_community (created, updated, id, name, description, logo, deleted, publication_workflow, restricted_submission) VALUES ('2017-11-03 09:04:44.181132', '2017-11-03 09:04:44.181146', '0afede87-2bf2-4d89-867e-d2ee57251c62', 'CLARIN', 'Linguistic data', '/img/communities/clarin.png', false, 'direct_publish', false);
INSERT INTO b2share_community (created, updated, id, name, description, logo, deleted, publication_workflow, restricted_submission) VALUES ('2017-11-03 09:04:44.198448', '2017-11-03 09:04:44.198463', '94a9567e-2fba-4677-8fde-a8b68bdb63e8', 'DRIHM', 'Meteorology and climate data.', '/img/communities/drihm.png', false, 'direct_publish', false);
INSERT INTO b2share_community (created, updated, id, name, description, logo, deleted, publication_workflow, restricted_submission) VALUES ('2017-11-03 09:04:44.21667', '2017-11-03 09:04:44.216685', 'b344f92a-cd0e-4e4c-aa09-28b5f95f7e41', 'EISCAT', 'Incoherent scatter radar data', '/img/communities/eiscat.png', false, 'direct_publish', true);
INSERT INTO b2share_community (created, updated, id, name, description, logo, deleted, publication_workflow, restricted_submission) VALUES ('2017-11-03 09:04:44.235286', '2017-11-03 09:04:44.2353', 'e9b9792e-79fb-4b07-b6b4-b9c2bd06d095', 'EUDAT', 'The big Eudat community. Use this community if no other is suited for you', '/img/communities/eudat.png', false, 'direct_publish', false);
INSERT INTO b2share_community (created, updated, id, name, description, logo, deleted, publication_workflow, restricted_submission) VALUES ('2017-11-03 09:04:44.253439', '2017-11-03 09:04:44.253456', '893fad89-dc4a-4f1b-a9ba-4240aa18e12b', 'EUON', 'Ontological data.', '/img/communities/euon.png', false, 'direct_publish', false);
INSERT INTO b2share_community (created, updated, id, name, description, logo, deleted, publication_workflow, restricted_submission) VALUES ('2017-11-03 09:04:44.275145', '2017-11-03 09:04:44.275162', '867c4e67-9227-4b6f-8595-c97d37e9de61', 'GBIF', 'Biodiversity data.', '/img/communities/gbif.png', false, 'direct_publish', false);
INSERT INTO b2share_community (created, updated, id, name, description, logo, deleted, publication_workflow, restricted_submission) VALUES ('2017-11-03 09:04:44.294538', '2017-11-03 09:04:44.294553', 'd952913c-451e-4b5c-817e-d578dc8a4469', 'LTER', 'Long-Term Ecosystem Research in Europe', '/img/communities/lter.jpg', false, 'direct_publish', false);
INSERT INTO b2share_community (created, updated, id, name, description, logo, deleted, publication_workflow, restricted_submission) VALUES ('2017-11-03 09:04:44.312213', '2017-11-03 09:04:44.312227', '4ba7c0fd-1435-4313-9c13-4d888d60321a', 'NRM', 'Herbarium data.', '/img/communities/nrm.png', false, 'direct_publish', false);
INSERT INTO b2share_community (created, updated, id, name, description, logo, deleted, publication_workflow, restricted_submission) VALUES ('2017-11-03 09:04:44.332138', '2017-11-03 09:04:44.332152', '8d963a29-5e19-492b-8cfe-97da4f54fad2', 'RDA', 'Research Data Alliance', '/img/communities/rda.png', false, 'direct_publish', true);


--
-- Data for Name: b2share_block_schema; Type: TABLE DATA; Schema: public; Owner: b2share
--

INSERT INTO b2share_block_schema (created, updated, id, name, deprecated, community) VALUES ('2017-11-03 09:04:44.352499', '2017-11-03 09:04:44.352513', '27193e5b-97e6-4f6f-8e87-3694589bcebe', 'lter', false, 'd952913c-451e-4b5c-817e-d578dc8a4469');
INSERT INTO b2share_block_schema (created, updated, id, name, deprecated, community) VALUES ('2017-11-03 09:04:44.642801', '2017-11-03 09:04:44.642817', '419e94c9-9c8b-4527-b12c-51fdd1f27947', 'aalto', false, 'c4234f93-da96-4d2f-a2c8-fa83d0775212');
INSERT INTO b2share_block_schema (created, updated, id, name, deprecated, community) VALUES ('2017-11-03 09:04:44.661474', '2017-11-03 09:04:44.661488', '2a01ee91-36fe-4edb-9734-73d22ac78821', 'clarin', false, '0afede87-2bf2-4d89-867e-d2ee57251c62');
INSERT INTO b2share_block_schema (created, updated, id, name, deprecated, community) VALUES ('2017-11-03 09:04:44.68064', '2017-11-03 09:04:44.680656', 'c46a2f19-58fc-4487-9176-5c538e028e55', 'euon', false, '893fad89-dc4a-4f1b-a9ba-4240aa18e12b');
INSERT INTO b2share_block_schema (created, updated, id, name, deprecated, community) VALUES ('2017-11-03 09:04:44.699006', '2017-11-03 09:04:44.699022', 'fa52bec3-a847-4602-8af5-b8d41a5215bc', 'nrm', false, '4ba7c0fd-1435-4313-9c13-4d888d60321a');
INSERT INTO b2share_block_schema (created, updated, id, name, deprecated, community) VALUES ('2017-11-03 09:04:44.718762', '2017-11-03 09:04:44.718776', 'e06cafbc-0598-4dd8-9029-9bf1f74d8b2e', 'gbif', false, '867c4e67-9227-4b6f-8595-c97d37e9de61');
INSERT INTO b2share_block_schema (created, updated, id, name, deprecated, community) VALUES ('2017-11-03 09:04:44.738686', '2017-11-03 09:04:44.738701', '668b996d-9e0e-4fff-be58-53d33316c5c6', 'rda', false, '8d963a29-5e19-492b-8cfe-97da4f54fad2');
INSERT INTO b2share_block_schema (created, updated, id, name, deprecated, community) VALUES ('2017-11-03 09:04:44.755419', '2017-11-03 09:04:44.755434', '362e6f81-68fb-4d71-9496-34ca00e59769', 'bbmri', false, '99916f6f-9a2c-4feb-a342-6552ac7f1529');
INSERT INTO b2share_block_schema (created, updated, id, name, deprecated, community) VALUES ('2017-11-03 09:04:44.778465', '2017-11-03 09:04:44.778481', '5108aff5-be5b-4d92-968a-22930ee65e94', 'drihm', false, '94a9567e-2fba-4677-8fde-a8b68bdb63e8');
INSERT INTO b2share_block_schema (created, updated, id, name, deprecated, community) VALUES ('2017-11-03 09:04:44.798022', '2017-11-03 09:04:44.798038', 'cee77dd0-9149-4a7b-9c28-85a8f7052bd9', 'eiscat', false, 'b344f92a-cd0e-4e4c-aa09-28b5f95f7e41');


--
-- Data for Name: b2share_block_schema_version; Type: TABLE DATA; Schema: public; Owner: b2share
--

INSERT INTO b2share_block_schema_version (block_schema, version, released, json_schema) VALUES ('27193e5b-97e6-4f6f-8e87-3694589bcebe', 0, '2017-11-03 09:04:44.635714', '{"additionalProperties":false,"title":"LTER Metadata","description":"This is the blueprint of the metadata block specific for the LTER community","type":"object","properties":{"metadata_url":{"type":"string","title":"Metadata URL","description":"Metadata URL"}},"$schema":"http://json-schema.org/draft-04/schema#"}');
INSERT INTO b2share_block_schema_version (block_schema, version, released, json_schema) VALUES ('419e94c9-9c8b-4527-b12c-51fdd1f27947', 0, '2017-11-03 09:04:44.657535', '{"additionalProperties":false,"required":["language_code"],"title":"Aalto Metadata","b2share":{"overwrites":{"language_code":{"ROOT_SCHEMA":["language"]}},"presentation":{"plugins":{"language_code":"language_chooser"},"major":["project_name","project_url","language_code","funding_id","owner_org","funder","owner"]}},"description":"This is the blueprint of the metadata block specific for the Aalto community","type":"object","properties":{"funder":{"type":"string","title":"Funder","description":"Funder"},"owner_org":{"type":"string","title":"Owner Organisation","description":"Owner Organisation"},"funding_id":{"type":"string","title":"Funding ID","description":"Funding ID"},"project_name":{"type":"string","title":"Project Name","description":"Project Name"},"language_code":{"type":"string","title":"Language Code","description":"This element can be used to add an ISO language code from ISO-639-3 to uniquely identify the language a document is written in","default":"eng"},"project_url":{"type":"string","title":"Project URL","description":"Project URL"},"owner":{"type":"string","title":"Owner","description":"Owner"}},"$schema":"http://json-schema.org/draft-04/schema#"}');
INSERT INTO b2share_block_schema_version (block_schema, version, released, json_schema) VALUES ('2a01ee91-36fe-4edb-9734-73d22ac78821', 0, '2017-11-03 09:04:44.677305', '{"additionalProperties":false,"required":["language_code","ling_resource_type"],"title":"CLARIN Metadata","b2share":{"overwrites":{"language_code":{"ROOT_SCHEMA":["language"]},"resource_type":{"ROOT_SCHEMA":["resource_type"]}},"presentation":{"plugins":{"language_code":"language_chooser"},"major":["language_code","region","ling_resource_type","project_name","quality"]}},"description":"This is the blueprint of the metadata block specific for the clarin community","type":"object","properties":{"region":{"type":"string","title":"Country/Region","description":"This element allows users to specify a country and/or a region to allow depositors to specify where the language the document is in is spoken"},"ling_resource_type":{"items":{"type":"string","enum":["Text","Image","Video","Audio","Time-Series","Other","treebank"]},"type":"array","title":"Resource Type","uniqueItems":true,"description":"This element allows the depositor to specify the type of the resource (Text, Audio, Video, Time-Series, Photo, etc.)"},"language_code":{"type":"string","title":"Language Code","default":"eng","description":"This element can be used to add an ISO language code from ISO-639-3 to uniquely identify the language a document is written in"},"quality":{"type":"string","title":"Quality","description":"This element allows depositors to indicate the quality of the resource allowing potential users to immediately see whether the resource is of use for them."},"project_name":{"type":"string","title":"Project Name","description":"This element allows the depositor to specify the projects which were at the source of the creation of the resource"}},"$schema":"http://json-schema.org/draft-04/schema#"}');
INSERT INTO b2share_block_schema_version (block_schema, version, released, json_schema) VALUES ('c46a2f19-58fc-4487-9176-5c538e028e55', 0, '2017-11-03 09:04:44.695469', '{"additionalProperties":false,"required":["hasDomain","hasOntologyLanguage"],"title":"EUON Metadata","description":"This is the blueprint of the metadata block specific for the EUON community","type":"object","properties":{"usedOntologyEngineeringTool":{"uniqueItems":true,"title":"Ontology Engineering Tool","description":"The tool that was used to develop the ontology","items":{"type":"string","enum":["Prot\u00e9g\u00e9","Prot\u00e9g\u00e9 3.x","Swoop","TopBraid Composer","OBO-Edit","OntoStudio","KAON","PoolParty Thesaurus Server","poolParty","XPATH2","Protege 4.3","Other...",""]},"type":"array","default":"Prot\u00e9g\u00e9"},"hasDomain":{"type":"string","title":"Ontology Domain","description":"A category that describes the ontology, from a pre-defined list of categories"},"hasOntologyLanguage":{"uniqueItems":true,"title":"Ontology Language","description":"The language in which the ontology was developed","items":{"type":"string","enum":["english","F-Logic","KIF","LexGrid-XML","OCML","OBO","OMV:DAML-OIL","OMV:OWL","OMV:OWL-DL","OMV:OWL-Full","OMV:OWL-Lite","OMV:RDF-S","OWL","Prot\u00e9g\u00e9-Frames","Prot\u00e9g\u00e9 3.x","Prot\u00e9g\u00e9 4.3","RRF","TRIX","W3C:OWL_2","W3C:SKOS","Other..."]},"type":"array","default":"F-Logic"},"modificationDate":{"format":"date-time","title":"Modification Date","type":"string","description":"Modification Date"},"creationDate":{"format":"date-time","title":"Creation Date","type":"string","description":"Creation Date"}},"$schema":"http://json-schema.org/draft-04/schema#"}');
INSERT INTO b2share_block_schema_version (block_schema, version, released, json_schema) VALUES ('fa52bec3-a847-4602-8af5-b8d41a5215bc', 0, '2017-11-03 09:04:44.715302', '{"additionalProperties":false,"required":["uuid","species_name","collector_name","collection_date","locality"],"title":"NRM Metadata","description":"This is the blueprint of the metadata block specific for the NRM community","type":"object","properties":{"species_name":{"type":"string","title":"Species name","description":"Species name displayed on the herbarium sheet label."},"locality":{"type":"string","title":"Locality","description":"Location at which the item shown in the image was collected. This may range from a country name to specific place names and descriptions."},"uuid":{"type":"string","title":"UUID","description":"The unique identifier for the herbarium sheet shown in this image, typically corresponds to the herbarium sheet''s catalogue number shown on the label."},"collection_date":{"type":"string","title":"Collection date","description":"Collection date shown on the label. This may be incomplete and/or show only year or year/month.","format":"date-time"},"latitude":{"type":"string","title":"Latitude","description":"Only modern labels will typically carry coordinates."},"collector_name":{"type":"string","title":"Collector name","description":"Name of the collector shown on the label."},"longitude":{"type":"string","title":"Longitude","description":"Only modern labels will typically carry coordinates."}},"$schema":"http://json-schema.org/draft-04/schema#"}');
INSERT INTO b2share_block_schema_version (block_schema, version, released, json_schema) VALUES ('e06cafbc-0598-4dd8-9029-9bf1f74d8b2e', 0, '2017-11-03 09:04:44.734365', '{"additionalProperties":false,"required":["version_number","gbif_id","country","status"],"title":"GBIF Metadata","description":"This is the blueprint of the metadata block specific for the GBIF community","type":"object","properties":{"country":{"type":"string","title":"Country","description":"Country"},"status":{"type":"string","title":"Status","description":"Endorsement status"},"gbif_id":{"type":"string","title":"GBIF ID","description":"Refers to GBIF metadataset"},"version_number":{"type":"string","title":"Version number","description":"Version number"}},"$schema":"http://json-schema.org/draft-04/schema#"}');
INSERT INTO b2share_block_schema_version (block_schema, version, released, json_schema) VALUES ('668b996d-9e0e-4fff-be58-53d33316c5c6', 0, '2017-11-03 09:04:44.752866', '{"additionalProperties":false,"title":"RDA Metadata","b2share":{"presentation":{"major":["date","coverage","format","relation","source"]}},"description":"This is the blueprint of the metadata block specific for the RDA community","type":"object","properties":{"coverage":{"type":"string","title":"Coverage","description":"Coverage"},"format":{"type":"string","title":"Format","description":"Format"},"date":{"type":"string","format":"date-time","title":"Date","description":"Date"},"source":{"type":"string","title":"Source","description":"Source"},"relation":{"type":"string","title":"Relation","description":"Relation"}},"$schema":"http://json-schema.org/draft-04/schema#"}');
INSERT INTO b2share_block_schema_version (block_schema, version, released, json_schema) VALUES ('362e6f81-68fb-4d71-9496-34ca00e59769', 0, '2017-11-03 09:04:44.769774', '{"additionalProperties":false,"title":"BBMRI Metadata","description":"This is the blueprint of the metadata block specific for the BBMRI community","type":"object","properties":{"age_interval":{"type":"string","title":"Age interval","description":"Age interval of youngest to oldest study participant, for example 40-80"},"categories_of_data_collected":{"items":{"type":"string","enum":["Biological samples","Register data","Survey data","Physiological measurements","Imaging data","Medical records","Other"]},"type":"array","title":"Categories of data collected","description":"The type of data collected in the study, and if biological samples are part of the study. Can be one or several of the following values: Biological samples, Register data, Survey data, Physiological measurements, Imaging data, Medical records, Other"},"planned_sampled_individuals":{"type":"integer","title":"Planned sampled individuals","description":"Number of individuals with biological samples planned for the study"},"study_name":{"type":"string","title":"Study name","description":"The name of the study in English"},"disease":{"type":"string","title":"Disease","description":"The disease of main interest in the sample collection, if any. Can be several values MIABIS-21"},"study_id":{"type":"string","title":"Study ID","description":"The unique ID or acronym for the study"},"sex":{"items":{"type":"string","enum":["Female","Male","Other"]},"type":"array","title":"Sex","description":"The sex of the study participants."},"principal_investigator":{"type":"string","title":"Principal Investigator","description":"The name of the person responsible for the study or the principal investigator"},"study_description":{"type":"string","title":"Study Description","description":"A description of the study aim"},"planned_total_individuals":{"type":"integer","title":"Planned total individuals","description":"Total number of individuals planned for the study with or without biological samples"},"study_design":{"items":{"type":"string","enum":["Case-control","Cohort","Cross-sectional","Longitudinal","Twin-study","Quality control","Population-based","Other"]},"type":"array","title":"Study design","description":"The type of study. Can be one or several of the following values."},"material_type":{"items":{"type":"string","enum":["Whole blood","Plasma","Serum","Urine","Saliva","CSF","DNA","RNA","Tissue","Faeces","Other","cell line"]},"type":"array","title":"Material type","description":"The nature of the biological samples that are included in the study, if any. Can be one or several of the following values: Whole blood, Plasma, Serum, Urine, Saliva, CSF, DNA, RNA, Tissue, Faeces, Other"}},"$schema":"http://json-schema.org/draft-04/schema#"}');
INSERT INTO b2share_block_schema_version (block_schema, version, released, json_schema) VALUES ('5108aff5-be5b-4d92-968a-22930ee65e94', 0, '2017-11-03 09:04:44.795058', '{"required":["ref_date","reference_system","topic","responsible_party","geo_location","spatial_resolution","vertical_extent","lineage"],"title":"DRIHM Metadata","description":"This is the blueprint of the metadata block specific for the DRIHM community","type":"object","properties":{"spatial_resolution":{"type":"string","title":"Spatial Resolution","description":"Spatial Resolution"},"ref_date":{"type":"string","title":"Reference date","description":"Reference date"},"lineage":{"type":"string","title":"Lineage","description":"Lineage"},"responsible_party":{"type":"string","title":"Responsible Party","description":"Responsible Party"},"vertical_extent":{"type":"string","title":"Vertical Extent","description":"Vertical Extent"},"topic":{"type":"string","title":"Topic Category","description":"Topic Category"},"reference_system":{"type":"string","title":"Reference System","description":"Reference System"},"geo_location":{"type":"string","title":"Geographic Location","description":"Geographic Location"}},"$schema":"http://json-schema.org/draft-04/schema#","additionalProperties":false}');
INSERT INTO b2share_block_schema_version (block_schema, version, released, json_schema) VALUES ('cee77dd0-9149-4a7b-9c28-85a8f7052bd9', 0, '2017-11-03 09:04:44.815949', '{"additionalProperties":false,"title":"EISCAT Metadata","description":"This is the blueprint of the metadata block specific for the EISCAT community","type":"object","properties":{"altitude":{"type":"string","title":"Instrument altitude","description":"Instrument altitude"},"kindat":{"type":"string","title":"kindat","description":"kindat"},"kind_of_data_file":{"type":"string","title":"Kind of data file","description":"Kind of data file"},"end_time":{"type":"string","title":"End time","description":"Timeserie end time"},"latitude":{"type":"string","title":"Instrument latitude","description":"Instrument latitude"},"status":{"type":"string","title":"Status description","description":"Status description"},"start_time":{"type":"string","title":"Start time","description":"Timeserie start time"},"longitude":{"type":"string","title":"Instrument longitude","description":"Instrument longitude"},"instrument":{"type":"string","title":"Instrument name","description":"Instrument name"}},"$schema":"http://json-schema.org/draft-04/schema#"}');


--
-- Data for Name: b2share_root_schema_version; Type: TABLE DATA; Schema: public; Owner: b2share
--

INSERT INTO b2share_root_schema_version (version, json_schema) VALUES (0, '{"b2share": {"presentation": {"minor": ["contributors", "resource_types", "alternate_identifiers", "version", "publisher", "language"], "major": ["community", "titles", "descriptions", "creators", "open_access", "embargo_date", "license", "disciplines", "keywords", "contact_email"]}}, "required": ["community", "titles", "open_access", "publication_state", "community_specific"], "properties": {"descriptions": {"uniqueItems": true, "description": "A more elaborate description of the resource. Focus on a content description that makes it easy for others to find, and to interpret its relevance.", "type": "array", "title": "Descriptions", "items": {"required": ["description", "description_type"], "additionalProperties": false, "type": "object", "properties": {"description": {"type": "string"}, "description_type": {"enum": ["Abstract", "Methods", "SeriesInformation", "TableOfContents", "TechnicalInfo", "Other"], "title": "Type"}}}}, "creators": {"uniqueItems": true, "description": "The full name of the creators. The personal name format should be: family, given (e.g.: Smith, John).", "type": "array", "title": "Creators", "items": {"required": ["creator_name"], "additionalProperties": false, "type": "object", "properties": {"creator_name": {"type": "string"}}}}, "_files": {"type": "array"}, "community_specific": {"type": "object"}, "_oai": {"type": "object"}, "_deposit": {"type": "object"}, "_pid": {"description": "Array of persistent identifiers pointing to this record.", "title": "Persistent Identifiers"}, "embargo_date": {"format": "date-time", "description": "The date marking the end of the embargo period. The record will be marked as open access on the specified date at midnight. Please note that the record metadata is always publicly accessible, and only the data files can have private access.", "type": "string", "title": "Embargo Date"}, "disciplines": {"uniqueItems": true, "description": "The scientific disciplines linked with the resource.", "type": "array", "title": "Disciplines", "items": {"type": "string"}}, "resource_types": {"description": "The type(s) of the resource.", "type": "array", "title": "Resource Type", "items": {"required": ["resource_type_general"], "additionalProperties": false, "type": "object", "properties": {"resource_type": {"type": "string", "title": "Description"}, "resource_type_general": {"enum": ["Audiovisual", "Collection", "Dataset", "Event", "Image", "InteractiveResource", "Model", "PhysicalObject", "Service", "Software", "Sound", "Text", "Workflow", "Other"], "title": "Category"}}}, "minItems": 1, "uniqueItems": true}, "publication_state": {"description": "State of the publication workflow.", "enum": ["draft", "submitted", "published"], "type": "string", "title": "Publication State"}, "contributors": {"uniqueItems": true, "description": "The list of all other contributors. Please mention all persons that were relevant in the creation of the resource.", "type": "array", "title": "Contributors", "items": {"required": ["contributor_name", "contributor_type"], "additionalProperties": false, "type": "object", "properties": {"contributor_name": {"type": "string", "title": "Name"}, "contributor_type": {"enum": ["ContactPerson", "DataCollector", "DataCurator", "DataManager", "Distributor", "Editor", "HostingInstitution", "Producer", "ProjectLeader", "ProjectManager", "ProjectMember", "RegistrationAgency", "RegistrationAuthority", "RelatedPerson", "Researcher", "ResearchGroup", "RightsHolder", "Sponsor", "Supervisor", "WorkPackageLeader", "Other"], "title": "Type"}}}}, "alternate_identifiers": {"uniqueItems": true, "description": "Any kind of other reference such as a URN, URI or an ISBN number.", "type": "array", "title": "Alternate identifiers", "items": {"required": ["alternate_identifier", "alternate_identifier_type"], "additionalProperties": false, "type": "object", "properties": {"alternate_identifier": {"type": "string"}, "alternate_identifier_type": {"type": "string", "title": "Type"}}}}, "license": {"description": "Specify the license under which this data set is available to the users (e.g. GPL, Apache v2 or Commercial). Please use the License Selector for help and additional information.", "title": "License", "required": ["license"], "additionalProperties": false, "type": "object", "properties": {"license": {"type": "string"}, "license_uri": {"format": "uri", "type": "string", "title": "URL"}}}, "publisher": {"description": "The entity responsible for making the resource available, either a person, an organization, or a service.", "type": "string", "title": "Publisher"}, "publication_date": {"format": "date", "description": "The date when the data was or will be made publicly available (e.g. 1971-07-13)", "type": "string", "title": "Publication Date"}, "titles": {"description": "The title(s) of the uploaded resource, or a name by which the resource is known.", "type": "array", "title": "Titles", "items": {"required": ["title"], "additionalProperties": false, "type": "object", "properties": {"title": {"type": "string"}}}, "minItems": 1, "uniqueItems": true}, "open_access": {"description": "Indicate whether the record''s files are publicly accessible or not. In case of restricted access the uploaded files will only be accessible by the record''s owner and the community administrators. Please note that the record''s metadata is always publicly accessible. ", "type": "boolean", "title": "Open Access"}, "language": {"description": "The primary language of the resource. Please use ISO_639-3 language codes.", "type": "string", "title": "Language"}, "version": {"description": "Denote the version of the resource.", "type": "string", "title": "Version"}, "contact_email": {"format": "email", "description": "Contact email information for this record.", "type": "string", "title": "Contact Email"}, "community": {"description": "The community to which the record has been submitted.", "type": "string", "title": "Community"}, "$schema": {"type": "string"}, "keywords": {"uniqueItems": true, "description": "A list of keywords or key phrases describing the resource.", "type": "array", "title": "Keywords", "items": {"type": "string"}}}, "additionalProperties": false, "type": "object", "$schema": "http://json-schema.org/draft-04/schema#"}');


--
-- Data for Name: b2share_community_schema_version; Type: TABLE DATA; Schema: public; Owner: b2share
--

INSERT INTO b2share_community_schema_version (community, version, released, root_schema, community_schema) VALUES ('d952913c-451e-4b5c-817e-d578dc8a4469', 0, '2017-11-03 09:04:44.864944', 0, '{"required":["27193e5b-97e6-4f6f-8e87-3694589bcebe"],"properties":{"27193e5b-97e6-4f6f-8e87-3694589bcebe":{"$ref":"http://localhost:5000/schemas/27193e5b-97e6-4f6f-8e87-3694589bcebe/versions/0#/json_schema"}},"additionalProperties":false,"$schema":"http://json-schema.org/draft-04/schema#","type":"object"}');
INSERT INTO b2share_community_schema_version (community, version, released, root_schema, community_schema) VALUES ('c4234f93-da96-4d2f-a2c8-fa83d0775212', 0, '2017-11-03 09:04:44.903298', 0, '{"required":["419e94c9-9c8b-4527-b12c-51fdd1f27947"],"properties":{"419e94c9-9c8b-4527-b12c-51fdd1f27947":{"$ref":"http://localhost:5000/schemas/419e94c9-9c8b-4527-b12c-51fdd1f27947/versions/0#/json_schema"}},"additionalProperties":false,"$schema":"http://json-schema.org/draft-04/schema#","type":"object"}');
INSERT INTO b2share_community_schema_version (community, version, released, root_schema, community_schema) VALUES ('0afede87-2bf2-4d89-867e-d2ee57251c62', 0, '2017-11-03 09:04:44.939292', 0, '{"required":["2a01ee91-36fe-4edb-9734-73d22ac78821"],"properties":{"2a01ee91-36fe-4edb-9734-73d22ac78821":{"$ref":"http://localhost:5000/schemas/2a01ee91-36fe-4edb-9734-73d22ac78821/versions/0#/json_schema"}},"additionalProperties":false,"$schema":"http://json-schema.org/draft-04/schema#","type":"object"}');
INSERT INTO b2share_community_schema_version (community, version, released, root_schema, community_schema) VALUES ('893fad89-dc4a-4f1b-a9ba-4240aa18e12b', 0, '2017-11-03 09:04:44.976352', 0, '{"additionalProperties":false,"required":["c46a2f19-58fc-4487-9176-5c538e028e55"],"properties":{"c46a2f19-58fc-4487-9176-5c538e028e55":{"$ref":"http://localhost:5000/schemas/c46a2f19-58fc-4487-9176-5c538e028e55/versions/0#/json_schema"}},"$schema":"http://json-schema.org/draft-04/schema#","type":"object"}');
INSERT INTO b2share_community_schema_version (community, version, released, root_schema, community_schema) VALUES ('4ba7c0fd-1435-4313-9c13-4d888d60321a', 0, '2017-11-03 09:04:45.017781', 0, '{"required":["fa52bec3-a847-4602-8af5-b8d41a5215bc"],"properties":{"fa52bec3-a847-4602-8af5-b8d41a5215bc":{"$ref":"http://localhost:5000/schemas/fa52bec3-a847-4602-8af5-b8d41a5215bc/versions/0#/json_schema"}},"additionalProperties":false,"$schema":"http://json-schema.org/draft-04/schema#","type":"object"}');
INSERT INTO b2share_community_schema_version (community, version, released, root_schema, community_schema) VALUES ('867c4e67-9227-4b6f-8595-c97d37e9de61', 0, '2017-11-03 09:04:45.076648', 0, '{"additionalProperties":false,"required":["e06cafbc-0598-4dd8-9029-9bf1f74d8b2e"],"properties":{"e06cafbc-0598-4dd8-9029-9bf1f74d8b2e":{"$ref":"http://localhost:5000/schemas/e06cafbc-0598-4dd8-9029-9bf1f74d8b2e/versions/0#/json_schema"}},"$schema":"http://json-schema.org/draft-04/schema#","type":"object"}');
INSERT INTO b2share_community_schema_version (community, version, released, root_schema, community_schema) VALUES ('8d963a29-5e19-492b-8cfe-97da4f54fad2', 0, '2017-11-03 09:04:45.136376', 0, '{"required":["668b996d-9e0e-4fff-be58-53d33316c5c6"],"properties":{"668b996d-9e0e-4fff-be58-53d33316c5c6":{"$ref":"http://localhost:5000/schemas/668b996d-9e0e-4fff-be58-53d33316c5c6/versions/0#/json_schema"}},"additionalProperties":false,"$schema":"http://json-schema.org/draft-04/schema#","type":"object"}');
INSERT INTO b2share_community_schema_version (community, version, released, root_schema, community_schema) VALUES ('99916f6f-9a2c-4feb-a342-6552ac7f1529', 0, '2017-11-03 09:04:45.193588', 0, '{"required":["362e6f81-68fb-4d71-9496-34ca00e59769"],"properties":{"362e6f81-68fb-4d71-9496-34ca00e59769":{"$ref":"http://localhost:5000/schemas/362e6f81-68fb-4d71-9496-34ca00e59769/versions/0#/json_schema"}},"additionalProperties":false,"$schema":"http://json-schema.org/draft-04/schema#","type":"object"}');
INSERT INTO b2share_community_schema_version (community, version, released, root_schema, community_schema) VALUES ('e9b9792e-79fb-4b07-b6b4-b9c2bd06d095', 0, '2017-11-03 09:04:45.212695', 0, '{"type":"object","properties":{},"additionalProperties":false,"$schema":"http://json-schema.org/draft-04/schema#"}');
INSERT INTO b2share_community_schema_version (community, version, released, root_schema, community_schema) VALUES ('94a9567e-2fba-4677-8fde-a8b68bdb63e8', 0, '2017-11-03 09:04:45.26246', 0, '{"additionalProperties":false,"required":["5108aff5-be5b-4d92-968a-22930ee65e94"],"properties":{"5108aff5-be5b-4d92-968a-22930ee65e94":{"$ref":"http://localhost:5000/schemas/5108aff5-be5b-4d92-968a-22930ee65e94/versions/0#/json_schema"}},"$schema":"http://json-schema.org/draft-04/schema#","type":"object"}');
INSERT INTO b2share_community_schema_version (community, version, released, root_schema, community_schema) VALUES ('b344f92a-cd0e-4e4c-aa09-28b5f95f7e41', 0, '2017-11-03 09:04:45.312603', 0, '{"required":["cee77dd0-9149-4a7b-9c28-85a8f7052bd9"],"properties":{"cee77dd0-9149-4a7b-9c28-85a8f7052bd9":{"$ref":"http://localhost:5000/schemas/cee77dd0-9149-4a7b-9c28-85a8f7052bd9/versions/0#/json_schema"}},"additionalProperties":false,"$schema":"http://json-schema.org/draft-04/schema#","type":"object"}');


--
-- Data for Name: files_location; Type: TABLE DATA; Schema: public; Owner: b2share
--

INSERT INTO files_location (created, updated, id, name, uri, "default") VALUES ('2017-11-03 09:04:44.01686', '2017-11-03 09:04:47.523153', 1, 'local', 'file:///usr/var/b2share-instance/files', true);


--
-- Data for Name: files_bucket; Type: TABLE DATA; Schema: public; Owner: b2share
--

INSERT INTO files_bucket (created, updated, id, default_location, default_storage_class, size, quota_size, max_file_size, locked, deleted) VALUES ('2017-11-03 09:04:45.82737', '2017-11-03 09:04:46.021279', '6c628250-50a9-4d88-af1f-fb8da8661666', 1, 'S', 9, 21474836480, 10737418240, true, false);
INSERT INTO files_bucket (created, updated, id, default_location, default_storage_class, size, quota_size, max_file_size, locked, deleted) VALUES ('2017-11-03 09:04:46.037998', '2017-11-03 09:04:46.07204', '2545b96f-f9b4-4b76-8a20-66ec7fa5603b', 1, 'S', 9, 21474836480, 10737418240, true, false);
INSERT INTO files_bucket (created, updated, id, default_location, default_storage_class, size, quota_size, max_file_size, locked, deleted) VALUES ('2017-11-03 09:04:46.641192', '2017-11-03 09:04:46.802333', 'a3b52d49-a2bd-40b7-9555-36897e9f604b', 1, 'S', 9, 21474836480, 10737418240, true, false);
INSERT INTO files_bucket (created, updated, id, default_location, default_storage_class, size, quota_size, max_file_size, locked, deleted) VALUES ('2017-11-03 09:04:46.82002', '2017-11-03 09:04:46.909227', '0444f79e-7148-41e4-8995-2c978af3a5a1', 1, 'S', 9, 21474836480, 10737418240, true, false);
INSERT INTO files_bucket (created, updated, id, default_location, default_storage_class, size, quota_size, max_file_size, locked, deleted) VALUES ('2017-11-03 09:04:47.525915', '2017-11-03 09:04:47.725251', 'c5b06a32-3401-4ad4-b672-376aca67dd9e', 1, 'S', 9, 21474836480, 10737418240, true, false);
INSERT INTO files_bucket (created, updated, id, default_location, default_storage_class, size, quota_size, max_file_size, locked, deleted) VALUES ('2017-11-03 09:04:47.752354', '2017-11-03 09:04:47.813204', '37f0f783-0537-4c2d-9256-8d2e944a97af', 1, 'S', 9, 21474836480, 10737418240, true, false);
--- Non published deposit draft's bucket
INSERT INTO files_bucket (created, updated, id, default_location, default_storage_class, size, quota_size, max_file_size, locked, deleted) VALUES ('2017-11-04 09:04:47.752354', '2017-11-04 09:04:47.813204', '46f649f1-7a86-4eae-82a2-8aef2625521e', 1, 'S', 9, 21474836480, 10737418240, true, false);
--- Hard deleted deposit's bucket (the file and bucket remain for now but should be deleted. See issue #1572)
INSERT INTO files_bucket (created, updated, id, default_location, default_storage_class, size, quota_size, max_file_size, locked, deleted) VALUES ('2017-11-07 15:23:02.719529', '2017-11-07 15:23:26.633379', 'a5645d6d-451d-4d3d-ac21-c25e93d11da0', 1, 'S', 13, 21474836480, 10737418240, false, false);
--- Soft deleted deposit's bucket and its non deleted record
INSERT INTO files_bucket (created, updated, id, default_location, default_storage_class, size, quota_size, max_file_size, locked, deleted) VALUES ('2016-12-21 13:55:36.184829', '2016-12-21 13:59:11.331594', 'c83cb78a-1592-4cfe-9fc0-4bfc35903de6', 1, 'S', 3, 21474836480, 10737418240, false, false);
INSERT INTO files_bucket (created, updated, id, default_location, default_storage_class, size, quota_size, max_file_size, locked, deleted) VALUES ('2016-12-21 13:55:36.184829', '2016-12-21 13:59:11.331594', '02e429f2-3b18-45d4-9089-79dece4caba5', 1, 'S', 3, 21474836480, 10737418240, false, false);


--
-- Data for Name: files_buckettags; Type: TABLE DATA; Schema: public; Owner: b2share
--



--
-- Data for Name: files_files; Type: TABLE DATA; Schema: public; Owner: b2share
--

INSERT INTO files_files (created, updated, id, uri, storage_class, size, checksum, readable, writable, last_check_at, last_check) VALUES ('2017-11-03 09:04:45.887101', '2017-11-03 09:04:46.061855', '7b2c8b95-00c0-44b5-9087-27ff128f1036', 'file:///usr/var/b2share-instance/files/7b/2c/8b95-00c0-44b5-9087-27ff128f1036/data', 'S', 9, 'md5:c8afdb36c52cf4727836669019e69222', true, false, NULL, true);
INSERT INTO files_files (created, updated, id, uri, storage_class, size, checksum, readable, writable, last_check_at, last_check) VALUES ('2017-11-03 09:04:46.685728', '2017-11-03 09:04:46.888531', '1e3f6c94-31d4-46b8-b455-fd70ca3a1aee', 'file:///usr/var/b2share-instance/files/1e/3f/6c94-31d4-46b8-b455-fd70ca3a1aee/data', 'S', 9, 'md5:c8afdb36c52cf4727836669019e69222', true, false, NULL, true);
INSERT INTO files_files (created, updated, id, uri, storage_class, size, checksum, readable, writable, last_check_at, last_check) VALUES ('2017-11-03 09:04:47.581233', '2017-11-03 09:04:47.800309', '6d50b8ca-0b32-4fd1-9fd5-f4a1a52eec75', 'file:///usr/var/b2share-instance/files/6d/50/b8ca-0b32-4fd1-9fd5-f4a1a52eec75/data', 'S', 9, 'md5:c8afdb36c52cf4727836669019e69222', true, false, NULL, true);
--- Deleted deposit's file (the file and bucket remain for now but should be deleted. See issue #1572)
INSERT INTO files_files (created, updated, id, uri, storage_class, size, checksum, readable, writable, last_check_at, last_check) VALUES ('2017-11-07 15:23:26.468502', '2017-11-07 15:23:26.620844', 'dfcb1788-1619-4880-bb89-16c5f7c2dc8c', 'file:///usr/var/b2share-instance/files/df/cb/1788-1619-4880-bb89-16c5f7c2dc8c/data', 'S', 13, 'md5:d6eb32081c822ed572b70567826d9d9d', true, false, NULL, true);
--- Soft deleted deposit's file
INSERT INTO files_files (created, updated, id, uri, storage_class, size, checksum, readable, writable, last_check_at, last_check) VALUES ('2016-12-21 13:58:38.782533', '2017-12-01 21:51:17.000115', 'b888901d-4b86-4cb6-86c1-3c995756dddc', 'file:///usr/var/b2share-instance/files/b8/88/901d-4b86-4cb6-86c1-3c995756dddc/data', 'S', 3, 'md5:aa559b4e3523a6c931f08f4df52d58f2', true, false, NULL, true);


--
-- Name: files_location_id_seq; Type: SEQUENCE SET; Schema: public; Owner: b2share
--

SELECT pg_catalog.setval('files_location_id_seq', 1, true);


--
-- Data for Name: files_multipartobject; Type: TABLE DATA; Schema: public; Owner: b2share
--



--
-- Data for Name: files_multipartobject_part; Type: TABLE DATA; Schema: public; Owner: b2share
--



--
-- Data for Name: files_object; Type: TABLE DATA; Schema: public; Owner: b2share
--

INSERT INTO files_object (created, updated, bucket_id, key, version_id, file_id, _mimetype, is_head) VALUES ('2017-11-03 09:04:45.87638', '2017-11-03 09:04:45.894349', '6c628250-50a9-4d88-af1f-fb8da8661666', 'myfile', '0fc5f5aa-da5f-4e32-ba17-242edf6f7eb0', '7b2c8b95-00c0-44b5-9087-27ff128f1036', NULL, true);
INSERT INTO files_object (created, updated, bucket_id, key, version_id, file_id, _mimetype, is_head) VALUES ('2017-11-03 09:04:46.054384', '2017-11-03 09:04:46.066304', '2545b96f-f9b4-4b76-8a20-66ec7fa5603b', 'myfile', '458c570a-4dd7-49c9-b881-6fc32326ddb3', '7b2c8b95-00c0-44b5-9087-27ff128f1036', NULL, true);
INSERT INTO files_object (created, updated, bucket_id, key, version_id, file_id, _mimetype, is_head) VALUES ('2017-11-03 09:04:46.680803', '2017-11-03 09:04:46.68688', 'a3b52d49-a2bd-40b7-9555-36897e9f604b', 'myfile', 'd1717642-a563-4554-9ce4-9e7278a37a4a', '1e3f6c94-31d4-46b8-b455-fd70ca3a1aee', NULL, true);
INSERT INTO files_object (created, updated, bucket_id, key, version_id, file_id, _mimetype, is_head) VALUES ('2017-11-03 09:04:46.860806', '2017-11-03 09:04:46.89366', '0444f79e-7148-41e4-8995-2c978af3a5a1', 'myfile', '084fbf14-6d1b-497a-903d-bca93d8ec061', '1e3f6c94-31d4-46b8-b455-fd70ca3a1aee', NULL, true);
INSERT INTO files_object (created, updated, bucket_id, key, version_id, file_id, _mimetype, is_head) VALUES ('2017-11-03 09:04:47.572535', '2017-11-03 09:04:47.582241', 'c5b06a32-3401-4ad4-b672-376aca67dd9e', 'myfile', '30797ee8-42cb-4986-a753-59031af5cebb', '6d50b8ca-0b32-4fd1-9fd5-f4a1a52eec75', NULL, true);
INSERT INTO files_object (created, updated, bucket_id, key, version_id, file_id, _mimetype, is_head) VALUES ('2017-11-03 09:04:47.791338', '2017-11-03 09:04:47.805738', '37f0f783-0537-4c2d-9256-8d2e944a97af', 'myfile', 'd7facd2f-68ea-4184-80d3-4dd778a323f6', '6d50b8ca-0b32-4fd1-9fd5-f4a1a52eec75', NULL, true);
--- Deleted deposit (the file and bucket remain for now but should be deleted. See issue #1572)
INSERT INTO files_object (created, updated, bucket_id, key, version_id, file_id, _mimetype, is_head) VALUES ('2017-11-07 15:23:26.441388', '2017-11-07 15:23:26.484648', 'a5645d6d-451d-4d3d-ac21-c25e93d11da0', 'test-file.txt', 'b0c43299-1614-4d1e-9edd-6fea2a973ca7', 'dfcb1788-1619-4880-bb89-16c5f7c2dc8c', NULL, true);
--- Soft deleted deposit's bucket
INSERT INTO files_object (created, updated, bucket_id, key, version_id, file_id, _mimetype, is_head) VALUES ('2016-12-21 13:58:38.778974', '2016-12-21 13:58:38.783342', 'c83cb78a-1592-4cfe-9fc0-4bfc35903de6', '512MB.file', 'dc5b7627-671d-4a59-a465-970da523360c', 'b888901d-4b86-4cb6-86c1-3c995756dddc', NULL, true);
INSERT INTO files_object (created, updated, bucket_id, key, version_id, file_id, _mimetype, is_head) VALUES ('2016-12-21 13:58:38.778974', '2016-12-21 13:58:38.783342', '02e429f2-3b18-45d4-9089-79dece4caba5', '512MB.file', '994b69ac-9ed8-49b2-8a33-89c8e8508da5', 'b888901d-4b86-4cb6-86c1-3c995756dddc', NULL, true);


--
-- Data for Name: oaiserver_set; Type: TABLE DATA; Schema: public; Owner: b2share
--

INSERT INTO oaiserver_set (created, updated, id, spec, name, description, search_pattern) VALUES ('2017-11-03 09:04:44.103199', '2017-11-03 09:04:44.103219', 1, 'c4234f93-da96-4d2f-a2c8-fa83d0775212', 'Aalto', 'Aalto University', NULL);
INSERT INTO oaiserver_set (created, updated, id, spec, name, description, search_pattern) VALUES ('2017-11-03 09:04:44.167984', '2017-11-03 09:04:44.168', 2, '99916f6f-9a2c-4feb-a342-6552ac7f1529', 'BBMRI', 'Biomedical Research.', NULL);
INSERT INTO oaiserver_set (created, updated, id, spec, name, description, search_pattern) VALUES ('2017-11-03 09:04:44.186641', '2017-11-03 09:04:44.186657', 3, '0afede87-2bf2-4d89-867e-d2ee57251c62', 'CLARIN', 'Linguistic data', NULL);
INSERT INTO oaiserver_set (created, updated, id, spec, name, description, search_pattern) VALUES ('2017-11-03 09:04:44.202557', '2017-11-03 09:04:44.202577', 4, '94a9567e-2fba-4677-8fde-a8b68bdb63e8', 'DRIHM', 'Meteorology and climate data.', NULL);
INSERT INTO oaiserver_set (created, updated, id, spec, name, description, search_pattern) VALUES ('2017-11-03 09:04:44.223489', '2017-11-03 09:04:44.223505', 5, 'b344f92a-cd0e-4e4c-aa09-28b5f95f7e41', 'EISCAT', 'Incoherent scatter radar data', NULL);
INSERT INTO oaiserver_set (created, updated, id, spec, name, description, search_pattern) VALUES ('2017-11-03 09:04:44.238965', '2017-11-03 09:04:44.238989', 6, 'e9b9792e-79fb-4b07-b6b4-b9c2bd06d095', 'EUDAT', 'The big Eudat community. Use this community if no other is suited for you', NULL);
INSERT INTO oaiserver_set (created, updated, id, spec, name, description, search_pattern) VALUES ('2017-11-03 09:04:44.257003', '2017-11-03 09:04:44.257022', 7, '893fad89-dc4a-4f1b-a9ba-4240aa18e12b', 'EUON', 'Ontological data.', NULL);
INSERT INTO oaiserver_set (created, updated, id, spec, name, description, search_pattern) VALUES ('2017-11-03 09:04:44.278596', '2017-11-03 09:04:44.278612', 8, '867c4e67-9227-4b6f-8595-c97d37e9de61', 'GBIF', 'Biodiversity data.', NULL);
INSERT INTO oaiserver_set (created, updated, id, spec, name, description, search_pattern) VALUES ('2017-11-03 09:04:44.298224', '2017-11-03 09:04:44.298239', 9, 'd952913c-451e-4b5c-817e-d578dc8a4469', 'LTER', 'Long-Term Ecosystem Research in Europe', NULL);
INSERT INTO oaiserver_set (created, updated, id, spec, name, description, search_pattern) VALUES ('2017-11-03 09:04:44.317037', '2017-11-03 09:04:44.317051', 10, '4ba7c0fd-1435-4313-9c13-4d888d60321a', 'NRM', 'Herbarium data.', NULL);
INSERT INTO oaiserver_set (created, updated, id, spec, name, description, search_pattern) VALUES ('2017-11-03 09:04:44.337293', '2017-11-03 09:04:44.337307', 11, '8d963a29-5e19-492b-8cfe-97da4f54fad2', 'RDA', 'Research Data Alliance', NULL);


--
-- Name: oaiserver_set_id_seq; Type: SEQUENCE SET; Schema: public; Owner: b2share
--

SELECT pg_catalog.setval('oaiserver_set_id_seq', 11, true);


--
-- Data for Name: oauth2server_client; Type: TABLE DATA; Schema: public; Owner: b2share
--



--
-- Data for Name: oauth2server_token; Type: TABLE DATA; Schema: public; Owner: b2share
--



--
-- Name: oauth2server_token_id_seq; Type: SEQUENCE SET; Schema: public; Owner: b2share
--

SELECT pg_catalog.setval('oauth2server_token_id_seq', 1, false);


--
-- Data for Name: oauthclient_remoteaccount; Type: TABLE DATA; Schema: public; Owner: b2share
--



--
-- Name: oauthclient_remoteaccount_id_seq; Type: SEQUENCE SET; Schema: public; Owner: b2share
--

SELECT pg_catalog.setval('oauthclient_remoteaccount_id_seq', 1, false);


--
-- Data for Name: oauthclient_remotetoken; Type: TABLE DATA; Schema: public; Owner: b2share
--



--
-- Data for Name: oauthclient_useridentity; Type: TABLE DATA; Schema: public; Owner: b2share
--



--
-- Data for Name: pidstore_pid; Type: TABLE DATA; Schema: public; Owner: b2share
--

INSERT INTO pidstore_pid (created, updated, id, pid_type, pid_value, pid_provider, status, object_type, object_uuid) VALUES ('2017-11-03 09:04:45.347433', '2017-11-03 09:04:45.347454', 1, 'b2dep', 'a1c2ef96a1e446fa9bd7a2a46d2242d4', NULL, 'R', 'rec', 'a1c2ef96-a1e4-46fa-9bd7-a2a46d2242d4');
INSERT INTO pidstore_pid (created, updated, id, pid_type, pid_value, pid_provider, status, object_type, object_uuid) VALUES ('2017-11-03 09:04:45.975537', '2017-11-03 09:04:45.975553', 2, 'b2rec', 'a1c2ef96a1e446fa9bd7a2a46d2242d4', NULL, 'R', 'rec', '9d518b6d-70b4-47b5-9e69-1f35fd4eb1d1');
INSERT INTO pidstore_pid (created, updated, id, pid_type, pid_value, pid_provider, status, object_type, object_uuid) VALUES ('2017-11-03 09:04:45.979942', '2017-11-03 09:04:45.979967', 3, 'oai', 'oai:b2share.eudat.eu:b2rec/a1c2ef96a1e446fa9bd7a2a46d2242d4', 'oai', 'R', 'rec', '9d518b6d-70b4-47b5-9e69-1f35fd4eb1d1');
INSERT INTO pidstore_pid (created, updated, id, pid_type, pid_value, pid_provider, status, object_type, object_uuid) VALUES ('2017-11-03 09:04:46.481281', '2017-11-03 09:04:46.481296', 4, 'b2dep', '47077e3c4b9f4852a40709e338ad4620', NULL, 'R', 'rec', '47077e3c-4b9f-4852-a407-09e338ad4620');
INSERT INTO pidstore_pid (created, updated, id, pid_type, pid_value, pid_provider, status, object_type, object_uuid) VALUES ('2017-11-03 09:04:46.72583', '2017-11-03 09:04:46.725847', 5, 'b2rec', '47077e3c4b9f4852a40709e338ad4620', NULL, 'R', 'rec', '1eb14309-87de-4f41-ad93-840e76fa0e15');
INSERT INTO pidstore_pid (created, updated, id, pid_type, pid_value, pid_provider, status, object_type, object_uuid) VALUES ('2017-11-03 09:04:46.730679', '2017-11-03 09:04:46.7307', 6, 'oai', 'oai:b2share.eudat.eu:b2rec/47077e3c4b9f4852a40709e338ad4620', 'oai', 'R', 'rec', '1eb14309-87de-4f41-ad93-840e76fa0e15');
INSERT INTO pidstore_pid (created, updated, id, pid_type, pid_value, pid_provider, status, object_type, object_uuid) VALUES ('2017-11-03 09:04:47.318029', '2017-11-03 09:04:47.318046', 7, 'b2dep', '1033083fedf4408fb5611f23527a926d', NULL, 'R', 'rec', '1033083f-edf4-408f-b561-1f23527a926d');
INSERT INTO pidstore_pid (created, updated, id, pid_type, pid_value, pid_provider, status, object_type, object_uuid) VALUES ('2017-11-03 09:04:47.651005', '2017-11-03 09:04:47.651024', 8, 'b2rec', '1033083fedf4408fb5611f23527a926d', NULL, 'R', 'rec', '29ad6eb8-559e-4b0d-a1cd-e5b1f1f268ff');
INSERT INTO pidstore_pid (created, updated, id, pid_type, pid_value, pid_provider, status, object_type, object_uuid) VALUES ('2017-11-03 09:04:47.656581', '2017-11-03 09:04:47.656597', 9, 'oai', 'oai:b2share.eudat.eu:b2rec/1033083fedf4408fb5611f23527a926d', 'oai', 'R', 'rec', '29ad6eb8-559e-4b0d-a1cd-e5b1f1f268ff');
--- Non published deposit PID
INSERT INTO pidstore_pid (created, updated, id, pid_type, pid_value, pid_provider, status, object_type, object_uuid) VALUES ('2017-11-04 09:04:47.318029', '2017-11-04 09:04:47.318046', 10, 'b2dep', '9544056edff2505fb5611f11127b817e', NULL, 'R', 'rec', '9544056e-dff2-505f-b561-1f11127b817e');
--- Hard Deleted deposit PID
INSERT INTO pidstore_pid (created, updated, id, pid_type, pid_value, pid_provider, status, object_type, object_uuid) VALUES ('2017-11-07 15:23:02.095302', '2017-11-07 15:33:52.390569', 11, 'b2dep', '6cd752bd21904e218a5f787c5dc416ab', NULL, 'D', 'rec', '6cd752bd-2190-4e21-8a5f-787c5dc416ab');
--- Soft Deleted deposit PID whose PID was not deleted. This is an invalid state which should be fixed by the upgrade. This should be fixed by the upgrade.
INSERT INTO pidstore_pid (created, updated, id, pid_type, pid_value, pid_provider, status, object_type, object_uuid) VALUES ('2016-12-21 13:55:36.118510', '2016-12-21 13:55:36.118521', 12, 'b2dep', '9d2cba26de4442af9633140e35e8a357', NULL, 'R', 'rec', '9d2cba26-de44-42af-9633-140e35e8a357');
INSERT INTO pidstore_pid (created, updated, id, pid_type, pid_value, pid_provider, status, object_type, object_uuid) VALUES ('2016-12-21 13:55:36.118510', '2016-12-21 13:55:36.118521', 13, 'b2rec', '9d2cba26de4442af9633140e35e8a357', NULL, 'R', 'rec', 'ed6c104a-1243-4ed8-86c5-2b1691b81f37');
INSERT INTO pidstore_pid (created, updated, id, pid_type, pid_value, pid_provider, status, object_type, object_uuid) VALUES ('2016-12-21 13:55:36.118510', '2016-12-21 13:55:36.118521', 14, 'oai', 'oai:b2share.eudat.eu:b2rec/9d2cba26de4442af9633140e35e8a357', NULL, 'R', 'oai', 'ed6c104a-1243-4ed8-86c5-2b1691b81f37');
--- Mis-deleted record. The pid is not deleted but the record is. This shouold be fixed by the upgrade.
INSERT INTO pidstore_pid (created, updated, id, pid_type, pid_value, pid_provider, status, object_type, object_uuid) VALUES ('2016-12-21 13:55:36.118510', '2016-12-21 13:55:36.118521', 15, 'b2rec', 'b953a54fb3a44d3e9392b6edfce5697d', NULL, 'R', 'rec', '331acc49-d97a-4415-969d-97c82424fc99');


--
-- Name: pidstore_pid_id_seq; Type: SEQUENCE SET; Schema: public; Owner: b2share
--

SELECT pg_catalog.setval('pidstore_pid_id_seq', 15, true);


--
-- Data for Name: pidstore_recid; Type: TABLE DATA; Schema: public; Owner: b2share
--



--
-- Name: pidstore_recid_recid_seq; Type: SEQUENCE SET; Schema: public; Owner: b2share
--

SELECT pg_catalog.setval('pidstore_recid_recid_seq', 1, false);


--
-- Data for Name: pidstore_redirect; Type: TABLE DATA; Schema: public; Owner: b2share
--



--
-- Data for Name: records_metadata; Type: TABLE DATA; Schema: public; Owner: b2share
--

INSERT INTO records_metadata (created, updated, id, json, version_id) VALUES ('2017-11-03 09:04:46.118913', '2017-11-03 09:04:46.118928', '9d518b6d-70b4-47b5-9e69-1f35fd4eb1d1', '{"_pid": [{"type": "b2rec", "value": "a1c2ef96a1e446fa9bd7a2a46d2242d4"}], "resource_types": [{"resource_type_general": "Text"}], "community": "99916f6f-9a2c-4feb-a342-6552ac7f1529", "open_access": true, "community_specific": {"362e6f81-68fb-4d71-9496-34ca00e59769": {"study_name": "REST", "study_id": "REST", "categories_of_data_collected": ["Biological samples"], "sex": ["Male"], "principal_investigator": "Amilcar Flores", "study_design": ["Other"], "study_description": "REST mediates androgen receptor actions on gene repression and predicts early recurrence of prostate cancer", "material_type": ["Other"], "disease": "C61"}}, "_oai": {"id": "a1c2ef96a1e446fa9bd7a2a46d2242d4", "updated": "2017-11-03T09:04:45Z", "sets": ["99916f6f-9a2c-4feb-a342-6552ac7f1529"]}, "descriptions": [{"description_type": "Abstract", "description": "REST mediates androgen receptor actions on gene repression and predicts early recurrence of prostate cancer"}], "_deposit": {"id": "a1c2ef96a1e446fa9bd7a2a46d2242d4", "pid": {"type": "b2rec", "revision_id": 0, "value": "a1c2ef96a1e446fa9bd7a2a46d2242d4"}, "owners": [1], "status": "published", "created_by": 1}, "_files": [{"checksum": "md5:c8afdb36c52cf4727836669019e69222", "bucket": "2545b96f-f9b4-4b76-8a20-66ec7fa5603b", "size": 9, "version_id": "458c570a-4dd7-49c9-b881-6fc32326ddb3", "key": "myfile"}], "contact_email": "x@example.com", "titles": [{"title": "REST paper 2014"}], "publication_state": "published", "$schema": "http://localhost:5000/communities/99916f6f-9a2c-4feb-a342-6552ac7f1529/schemas/0#/json_schema", "keywords": ["prostate cancer", "REST", "TFBS", "ChiP-seq"]}', 1);
INSERT INTO records_metadata (created, updated, id, json, version_id) VALUES ('2017-11-03 09:04:45.429632', '2017-11-03 09:04:46.261512', 'a1c2ef96-a1e4-46fa-9bd7-a2a46d2242d4', '{"resource_types": [{"resource_type_general": "Text"}], "community": "99916f6f-9a2c-4feb-a342-6552ac7f1529", "$schema": "http://localhost:5000/communities/99916f6f-9a2c-4feb-a342-6552ac7f1529/schemas/0#/draft_json_schema", "_pid": [{"type": "b2rec", "value": "a1c2ef96a1e446fa9bd7a2a46d2242d4"}], "descriptions": [{"description_type": "Abstract", "description": "REST mediates androgen receptor actions on gene repression and predicts early recurrence of prostate cancer"}], "_oai": {"id": "a1c2ef96a1e446fa9bd7a2a46d2242d4", "updated": "2017-11-03T09:04:45Z", "sets": ["99916f6f-9a2c-4feb-a342-6552ac7f1529"]}, "community_specific": {"362e6f81-68fb-4d71-9496-34ca00e59769": {"study_name": "REST", "study_id": "REST", "categories_of_data_collected": ["Biological samples"], "sex": ["Male"], "principal_investigator": "Amilcar Flores", "study_description": "REST mediates androgen receptor actions on gene repression and predicts early recurrence of prostate cancer", "material_type": ["Other"], "disease": "C61", "study_design": ["Other"]}}, "_deposit": {"id": "a1c2ef96a1e446fa9bd7a2a46d2242d4", "pid": {"type": "b2rec", "revision_id": 0, "value": "a1c2ef96a1e446fa9bd7a2a46d2242d4"}, "owners": [1], "status": "published", "created_by": 1}, "contact_email": "x@example.com", "titles": [{"title": "REST paper 2014"}], "publication_state": "published", "open_access": true, "keywords": ["prostate cancer", "REST", "TFBS", "ChiP-seq"]}', 2);
INSERT INTO records_metadata (created, updated, id, json, version_id) VALUES ('2017-11-03 09:04:46.976313', '2017-11-03 09:04:46.976331', '1eb14309-87de-4f41-ad93-840e76fa0e15', '{"resource_types": [{"resource_type_general": "Text"}], "keywords": ["Research Data Alliance", "RDA", "Governance", "Foundation", "RDA Policy"], "_oai": {"id": "47077e3c4b9f4852a40709e338ad4620", "updated": "2017-11-03T09:04:46Z", "sets": ["8d963a29-5e19-492b-8cfe-97da4f54fad2"]}, "community_specific": {"668b996d-9e0e-4fff-be58-53d33316c5c6": {"coverage": "Official Document", "format": "Text"}}, "_deposit": {"id": "47077e3c4b9f4852a40709e338ad4620", "pid": {"type": "b2rec", "revision_id": 0, "value": "47077e3c4b9f4852a40709e338ad4620"}, "owners": [1], "status": "published", "created_by": 1}, "$schema": "http://localhost:5000/communities/8d963a29-5e19-492b-8cfe-97da4f54fad2/schemas/0#/json_schema", "alternate_identifiers": [{"alternate_identifier_type": "DOI", "alternate_identifier": "10.15497/A675341C-F705-4136-B7C3-B9C14B556186"}], "_pid": [{"type": "b2rec", "value": "47077e3c4b9f4852a40709e338ad4620"}], "community": "8d963a29-5e19-492b-8cfe-97da4f54fad2", "open_access": true, "descriptions": [{"description_type": "Abstract", "description": "A document describing the high-level structures of the Research Data Alliance Foundation. This document is separate from the regular governance document, which describes procedures and processes."}], "_files": [{"checksum": "md5:c8afdb36c52cf4727836669019e69222", "bucket": "0444f79e-7148-41e4-8995-2c978af3a5a1", "size": 9, "version_id": "084fbf14-6d1b-497a-903d-bca93d8ec061", "key": "myfile"}], "contact_email": "x@rd-alliance.org", "license": {"license": "Creative Commons Attribution (CC-BY)", "license_uri": "http://creativecommons.org/licenses/by/4.0/"}, "titles": [{"title": "RDA Foundation Governance Document"}], "publication_state": "published", "creators": [{"creator_name": "Research Data Alliance Council"}, {"creator_name": "RDA2"}]}', 1);
INSERT INTO records_metadata (created, updated, id, json, version_id) VALUES ('2017-11-03 09:04:46.506919', '2017-11-03 09:04:47.184145', '47077e3c-4b9f-4852-a407-09e338ad4620', '{"resource_types": [{"resource_type_general": "Text"}], "keywords": ["Research Data Alliance", "RDA", "Governance", "Foundation", "RDA Policy"], "_oai": {"id": "47077e3c4b9f4852a40709e338ad4620", "updated": "2017-11-03T09:04:46Z", "sets": ["8d963a29-5e19-492b-8cfe-97da4f54fad2"]}, "community_specific": {"668b996d-9e0e-4fff-be58-53d33316c5c6": {"coverage": "Official Document", "format": "Text"}}, "_deposit": {"id": "47077e3c4b9f4852a40709e338ad4620", "pid": {"type": "b2rec", "revision_id": 0, "value": "47077e3c4b9f4852a40709e338ad4620"}, "owners": [1], "status": "published", "created_by": 1}, "$schema": "http://localhost:5000/communities/8d963a29-5e19-492b-8cfe-97da4f54fad2/schemas/0#/draft_json_schema", "alternate_identifiers": [{"alternate_identifier_type": "DOI", "alternate_identifier": "10.15497/A675341C-F705-4136-B7C3-B9C14B556186"}], "community": "8d963a29-5e19-492b-8cfe-97da4f54fad2", "_pid": [{"type": "b2rec", "value": "47077e3c4b9f4852a40709e338ad4620"}], "creators": [{"creator_name": "Research Data Alliance Council"}, {"creator_name": "RDA2"}], "descriptions": [{"description_type": "Abstract", "description": "A document describing the high-level structures of the Research Data Alliance Foundation. This document is separate from the regular governance document, which describes procedures and processes."}], "contact_email": "x@rd-alliance.org", "license": {"license": "Creative Commons Attribution (CC-BY)", "license_uri": "http://creativecommons.org/licenses/by/4.0/"}, "titles": [{"title": "RDA Foundation Governance Document"}], "publication_state": "published", "open_access": true}', 2);
INSERT INTO records_metadata (created, updated, id, json, version_id) VALUES ('2017-11-03 09:04:47.913535', '2017-11-03 09:04:47.913553', '29ad6eb8-559e-4b0d-a1cd-e5b1f1f268ff', '{"_pid": [{"type": "b2rec", "value": "1033083fedf4408fb5611f23527a926d"}], "resource_types": [{"resource_type_general": "Text"}], "community": "0afede87-2bf2-4d89-867e-d2ee57251c62", "open_access": true, "creators": [{"creator_name": "Daniel Zeman"}], "community_specific": {"2a01ee91-36fe-4edb-9734-73d22ac78821": {"ling_resource_type": ["Text"], "language_code": "eng"}}, "_oai": {"id": "1033083fedf4408fb5611f23527a926d", "updated": "2017-11-03T09:04:47Z", "sets": ["0afede87-2bf2-4d89-867e-d2ee57251c62"]}, "descriptions": [{"description_type": "Abstract", "description": "Description of verbal paradigms in Bengali. The description is written in Czech."}], "_deposit": {"id": "1033083fedf4408fb5611f23527a926d", "pid": {"type": "b2rec", "revision_id": 0, "value": "1033083fedf4408fb5611f23527a926d"}, "owners": [1], "status": "published", "created_by": 1}, "_files": [{"checksum": "md5:c8afdb36c52cf4727836669019e69222", "bucket": "37f0f783-0537-4c2d-9256-8d2e944a97af", "size": 9, "version_id": "d7facd2f-68ea-4184-80d3-4dd778a323f6", "key": "myfile"}], "contact_email": "x@example.com", "titles": [{"title": "\u010casov\u00e1n\u00ed sloves v beng\u00e1l\u0161tin\u011b"}], "publication_state": "published", "$schema": "http://localhost:5000/communities/0afede87-2bf2-4d89-867e-d2ee57251c62/schemas/0#/json_schema"}', 1);
INSERT INTO records_metadata (created, updated, id, json, version_id) VALUES ('2017-11-03 09:04:47.367063', '2017-11-03 09:04:48.096744', '1033083f-edf4-408f-b561-1f23527a926d', '{"resource_types": [{"resource_type_general": "Text"}], "community": "0afede87-2bf2-4d89-867e-d2ee57251c62", "_pid": [{"type": "b2rec", "value": "1033083fedf4408fb5611f23527a926d"}], "creators": [{"creator_name": "Daniel Zeman"}], "descriptions": [{"description_type": "Abstract", "description": "Description of verbal paradigms in Bengali. The description is written in Czech."}], "_oai": {"id": "1033083fedf4408fb5611f23527a926d", "updated": "2017-11-03T09:04:47Z", "sets": ["0afede87-2bf2-4d89-867e-d2ee57251c62"]}, "$schema": "http://localhost:5000/communities/0afede87-2bf2-4d89-867e-d2ee57251c62/schemas/0#/draft_json_schema", "_deposit": {"id": "1033083fedf4408fb5611f23527a926d", "pid": {"type": "b2rec", "revision_id": 0, "value": "1033083fedf4408fb5611f23527a926d"}, "owners": [1], "status": "published", "created_by": 1}, "community_specific": {"2a01ee91-36fe-4edb-9734-73d22ac78821": {"ling_resource_type": ["Text"], "language_code": "eng"}}, "contact_email": "x@example.com", "titles": [{"title": "\u010casov\u00e1n\u00ed sloves v beng\u00e1l\u0161tin\u011b"}], "publication_state": "published", "open_access": true}', 2);
--- Non published deposit draft
INSERT INTO records_metadata (created, updated, id, json, version_id) VALUES ('2017-11-04 09:04:47.367063', '2017-11-04 09:04:48.096744', '9544056e-dff2-505f-b561-1f11127b817e', '{"resource_types": [{"resource_type_general": "Text"}], "community": "0afede87-2bf2-4d89-867e-d2ee57251c62", "_pid": [{"type": "b2rec", "value": "9544056edff2505fb5611f11127b817e"}], "creators": [{"creator_name": "Daniel Zeman"}], "descriptions": [{"description_type": "Abstract", "description": "This is an unpublished draft record description."}], "$schema": "http://localhost:5000/communities/0afede87-2bf2-4d89-867e-d2ee57251c62/schemas/0#/draft_json_schema", "_deposit": {"id": "1033083fedf4408fb5611f23527a926d", "pid": {"type": "b2rec", "revision_id": 0, "value": "1033083fedf4408fb5611f23527a926d"}, "owners": [1], "status": "published", "created_by": 1}, "community_specific": {"2a01ee91-36fe-4edb-9734-73d22ac78821": {"ling_resource_type": ["Text"], "language_code": "eng"}}, "contact_email": "x@example.com", "titles": [{"title": "This is an unpublished a draft record"}], "publication_state": "draft", "open_access": true}', 2);
--- Soft deleted deposit and its non deleted record
INSERT INTO records_metadata (created, updated, id, json, version_id) VALUES ('2016-12-21 13:55:36.136869', '2016-12-21 15:04:21.185352', '9d2cba26-de44-42af-9633-140e35e8a357', NULL, 2);
INSERT INTO records_metadata (created, updated, id, json, version_id) VALUES ('2016-12-21 13:55:36.136869', '2016-12-21 15:04:21.185352', 'ed6c104a-1243-4ed8-86c5-2b1691b81f37', '{"titles": [{"title": "test_upload"}], "open_access": true, "_pid": [{"type": "b2rec", "value": "9d2cba26de4442af9633140e35e8a357"}, {"type": "ePIC_PID", "value": "http://hdl.handle.net/11304/a42592ce-aee6-4b6f-9bd1-8909c7625e03"}], "creators": [{"creator_name": "John Doe"}], "$schema": "http://localhost:5000/communities/e9b9792e-79fb-4b07-b6b4-b9c2bd06d095/schemas/0#/json_schema", "license": {"license_uri": "http://creativecommons.org/publicdomain/mark/1.0/", "license": "Public Domain Mark (PD)"}, "community_specific": {}, "_files": [{"version_id": "994b69ac-9ed8-49b2-8a33-89c8e8508da5", "bucket": "02e429f2-3b18-45d4-9089-79dece4caba5", "key": "512MB.file", "checksum": "md5:aa559b4e3523a6c931f08f4df52d58f2", "ePIC_PID": "http://hdl.handle.net/11304/76166cb2-f453-4a07-b7a8-68bea9db51b3", "size": 536870912}], "community": "e9b9792e-79fb-4b07-b6b4-b9c2bd06d095", "publication_state": "published", "_oai": {"id": "oai:b2share.eudat.eu:b2rec/9d2cba26de4442af9633140e35e8a357", "sets": [], "updated": "2016-12-21T13:59:10Z"}, "descriptions": [{"description_type": "Abstract", "description": "One 512MB file"}], "_deposit": {"id": "9d2cba26de4442af9633140e35e8a357", "status": "published", "created_by": 2, "pid": {"type": "b2rec", "revision_id": 0, "value": "9d2cba26de4442af9633140e35e8a357"}, "owners": [2]}, "keywords": ["one gigabyte file"]}', 2);
--- Mis-deleted record. The pid is not deleted but the record is.
INSERT INTO records_metadata (created, updated, id, json, version_id) VALUES ('2016-12-21 13:55:36.136869', '2016-12-21 15:04:21.185352', '331acc49-d97a-4415-969d-97c82424fc99', NULL, 1);



--
-- Data for Name: records_buckets; Type: TABLE DATA; Schema: public; Owner: b2share
--

INSERT INTO records_buckets (record_id, bucket_id) VALUES ('a1c2ef96-a1e4-46fa-9bd7-a2a46d2242d4', '6c628250-50a9-4d88-af1f-fb8da8661666');
INSERT INTO records_buckets (record_id, bucket_id) VALUES ('9d518b6d-70b4-47b5-9e69-1f35fd4eb1d1', '2545b96f-f9b4-4b76-8a20-66ec7fa5603b');
INSERT INTO records_buckets (record_id, bucket_id) VALUES ('47077e3c-4b9f-4852-a407-09e338ad4620', 'a3b52d49-a2bd-40b7-9555-36897e9f604b');
INSERT INTO records_buckets (record_id, bucket_id) VALUES ('1eb14309-87de-4f41-ad93-840e76fa0e15', '0444f79e-7148-41e4-8995-2c978af3a5a1');
INSERT INTO records_buckets (record_id, bucket_id) VALUES ('1033083f-edf4-408f-b561-1f23527a926d', 'c5b06a32-3401-4ad4-b672-376aca67dd9e');
INSERT INTO records_buckets (record_id, bucket_id) VALUES ('29ad6eb8-559e-4b0d-a1cd-e5b1f1f268ff', '37f0f783-0537-4c2d-9256-8d2e944a97af');
--- Non published deposit draft's bucket
INSERT INTO records_buckets (record_id, bucket_id) VALUES ('9544056e-dff2-505f-b561-1f11127b817e', '46f649f1-7a86-4eae-82a2-8aef2625521e');
--- bucket of the soft deleted deposit and its non deleted record
INSERT INTO records_buckets (record_id, bucket_id) VALUES ('9d2cba26-de44-42af-9633-140e35e8a357', 'c83cb78a-1592-4cfe-9fc0-4bfc35903de6');
INSERT INTO records_buckets (record_id, bucket_id) VALUES ('ed6c104a-1243-4ed8-86c5-2b1691b81f37', '02e429f2-3b18-45d4-9089-79dece4caba5');


--
-- Data for Name: records_metadata_version; Type: TABLE DATA; Schema: public; Owner: b2share
--

INSERT INTO records_metadata_version (created, updated, id, json, version_id, transaction_id, end_transaction_id, operation_type) VALUES ('2017-11-03 09:04:46.118913', '2017-11-03 09:04:46.118928', '9d518b6d-70b4-47b5-9e69-1f35fd4eb1d1', '{"_pid": [{"type": "b2rec", "value": "a1c2ef96a1e446fa9bd7a2a46d2242d4"}], "resource_types": [{"resource_type_general": "Text"}], "community": "99916f6f-9a2c-4feb-a342-6552ac7f1529", "open_access": true, "community_specific": {"362e6f81-68fb-4d71-9496-34ca00e59769": {"study_name": "REST", "study_id": "REST", "categories_of_data_collected": ["Biological samples"], "sex": ["Male"], "principal_investigator": "Amilcar Flores", "study_design": ["Other"], "study_description": "REST mediates androgen receptor actions on gene repression and predicts early recurrence of prostate cancer", "material_type": ["Other"], "disease": "C61"}}, "_oai": {"id": "a1c2ef96a1e446fa9bd7a2a46d2242d4", "updated": "2017-11-03T09:04:45Z", "sets": ["99916f6f-9a2c-4feb-a342-6552ac7f1529"]}, "descriptions": [{"description_type": "Abstract", "description": "REST mediates androgen receptor actions on gene repression and predicts early recurrence of prostate cancer"}], "_deposit": {"id": "a1c2ef96a1e446fa9bd7a2a46d2242d4", "pid": {"type": "b2rec", "revision_id": 0, "value": "a1c2ef96a1e446fa9bd7a2a46d2242d4"}, "owners": [1], "status": "published", "created_by": 1}, "_files": [{"checksum": "md5:c8afdb36c52cf4727836669019e69222", "bucket": "2545b96f-f9b4-4b76-8a20-66ec7fa5603b", "size": 9, "version_id": "458c570a-4dd7-49c9-b881-6fc32326ddb3", "key": "myfile"}], "contact_email": "x@example.com", "titles": [{"title": "REST paper 2014"}], "publication_state": "published", "$schema": "http://localhost:5000/communities/99916f6f-9a2c-4feb-a342-6552ac7f1529/schemas/0#/json_schema", "keywords": ["prostate cancer", "REST", "TFBS", "ChiP-seq"]}', 1, 1, NULL, 0);
INSERT INTO records_metadata_version (created, updated, id, json, version_id, transaction_id, end_transaction_id, operation_type) VALUES ('2017-11-03 09:04:45.429632', '2017-11-03 09:04:46.261512', 'a1c2ef96-a1e4-46fa-9bd7-a2a46d2242d4', '{"resource_types": [{"resource_type_general": "Text"}], "community": "99916f6f-9a2c-4feb-a342-6552ac7f1529", "open_access": true, "descriptions": [{"description_type": "Abstract", "description": "REST mediates androgen receptor actions on gene repression and predicts early recurrence of prostate cancer"}], "community_specific": {"362e6f81-68fb-4d71-9496-34ca00e59769": {"study_name": "REST", "study_id": "REST", "categories_of_data_collected": ["Biological samples"], "sex": ["Male"], "principal_investigator": "Amilcar Flores", "study_description": "REST mediates androgen receptor actions on gene repression and predicts early recurrence of prostate cancer", "material_type": ["Other"], "disease": "C61", "study_design": ["Other"]}}, "_deposit": {"id": "a1c2ef96a1e446fa9bd7a2a46d2242d4", "owners": [1], "status": "draft", "created_by": 1}, "contact_email": "x@example.com", "keywords": ["prostate cancer", "REST", "TFBS", "ChiP-seq"], "titles": [{"title": "REST paper 2014"}], "publication_state": "draft", "$schema": "http://localhost:5000/communities/99916f6f-9a2c-4feb-a342-6552ac7f1529/schemas/0#/draft_json_schema"}', 2, 1, NULL, 1);
INSERT INTO records_metadata_version (created, updated, id, json, version_id, transaction_id, end_transaction_id, operation_type) VALUES ('2017-11-03 09:04:46.976313', '2017-11-03 09:04:46.976331', '1eb14309-87de-4f41-ad93-840e76fa0e15', '{"resource_types": [{"resource_type_general": "Text"}], "keywords": ["Research Data Alliance", "RDA", "Governance", "Foundation", "RDA Policy"], "_oai": {"id": "47077e3c4b9f4852a40709e338ad4620", "updated": "2017-11-03T09:04:46Z", "sets": ["8d963a29-5e19-492b-8cfe-97da4f54fad2"]}, "community_specific": {"668b996d-9e0e-4fff-be58-53d33316c5c6": {"coverage": "Official Document", "format": "Text"}}, "_deposit": {"id": "47077e3c4b9f4852a40709e338ad4620", "pid": {"type": "b2rec", "revision_id": 0, "value": "47077e3c4b9f4852a40709e338ad4620"}, "owners": [1], "status": "published", "created_by": 1}, "$schema": "http://localhost:5000/communities/8d963a29-5e19-492b-8cfe-97da4f54fad2/schemas/0#/json_schema", "alternate_identifiers": [{"alternate_identifier_type": "DOI", "alternate_identifier": "10.15497/A675341C-F705-4136-B7C3-B9C14B556186"}], "_pid": [{"type": "b2rec", "value": "47077e3c4b9f4852a40709e338ad4620"}], "community": "8d963a29-5e19-492b-8cfe-97da4f54fad2", "open_access": true, "descriptions": [{"description_type": "Abstract", "description": "A document describing the high-level structures of the Research Data Alliance Foundation. This document is separate from the regular governance document, which describes procedures and processes."}], "_files": [{"checksum": "md5:c8afdb36c52cf4727836669019e69222", "bucket": "0444f79e-7148-41e4-8995-2c978af3a5a1", "size": 9, "version_id": "084fbf14-6d1b-497a-903d-bca93d8ec061", "key": "myfile"}], "contact_email": "x@rd-alliance.org", "license": {"license": "Creative Commons Attribution (CC-BY)", "license_uri": "http://creativecommons.org/licenses/by/4.0/"}, "titles": [{"title": "RDA Foundation Governance Document"}], "publication_state": "published", "creators": [{"creator_name": "Research Data Alliance Council"}, {"creator_name": "RDA2"}]}', 1, 1, NULL, 0);
INSERT INTO records_metadata_version (created, updated, id, json, version_id, transaction_id, end_transaction_id, operation_type) VALUES ('2017-11-03 09:04:46.506919', '2017-11-03 09:04:47.184145', '47077e3c-4b9f-4852-a407-09e338ad4620', '{"resource_types": [{"resource_type_general": "Text"}], "community": "8d963a29-5e19-492b-8cfe-97da4f54fad2", "open_access": true, "creators": [{"creator_name": "Research Data Alliance Council"}, {"creator_name": "RDA2"}], "community_specific": {"668b996d-9e0e-4fff-be58-53d33316c5c6": {"coverage": "Official Document", "format": "Text"}}, "descriptions": [{"description_type": "Abstract", "description": "A document describing the high-level structures of the Research Data Alliance Foundation. This document is separate from the regular governance document, which describes procedures and processes."}], "_deposit": {"id": "47077e3c4b9f4852a40709e338ad4620", "owners": [1], "status": "draft", "created_by": 1}, "alternate_identifiers": [{"alternate_identifier_type": "DOI", "alternate_identifier": "10.15497/A675341C-F705-4136-B7C3-B9C14B556186"}], "contact_email": "x@rd-alliance.org", "license": {"license": "Creative Commons Attribution (CC-BY)", "license_uri": "http://creativecommons.org/licenses/by/4.0/"}, "titles": [{"title": "RDA Foundation Governance Document"}], "publication_state": "draft", "$schema": "http://localhost:5000/communities/8d963a29-5e19-492b-8cfe-97da4f54fad2/schemas/0#/draft_json_schema", "keywords": ["Research Data Alliance", "RDA", "Governance", "Foundation", "RDA Policy"]}', 2, 1, NULL, 1);
INSERT INTO records_metadata_version (created, updated, id, json, version_id, transaction_id, end_transaction_id, operation_type) VALUES ('2017-11-03 09:04:47.913535', '2017-11-03 09:04:47.913553', '29ad6eb8-559e-4b0d-a1cd-e5b1f1f268ff', '{"_pid": [{"type": "b2rec", "value": "1033083fedf4408fb5611f23527a926d"}], "resource_types": [{"resource_type_general": "Text"}], "community": "0afede87-2bf2-4d89-867e-d2ee57251c62", "open_access": true, "creators": [{"creator_name": "Daniel Zeman"}], "community_specific": {"2a01ee91-36fe-4edb-9734-73d22ac78821": {"ling_resource_type": ["Text"], "language_code": "eng"}}, "_oai": {"id": "1033083fedf4408fb5611f23527a926d", "updated": "2017-11-03T09:04:47Z", "sets": ["0afede87-2bf2-4d89-867e-d2ee57251c62"]}, "descriptions": [{"description_type": "Abstract", "description": "Description of verbal paradigms in Bengali. The description is written in Czech."}], "_deposit": {"id": "1033083fedf4408fb5611f23527a926d", "pid": {"type": "b2rec", "revision_id": 0, "value": "1033083fedf4408fb5611f23527a926d"}, "owners": [1], "status": "published", "created_by": 1}, "_files": [{"checksum": "md5:c8afdb36c52cf4727836669019e69222", "bucket": "37f0f783-0537-4c2d-9256-8d2e944a97af", "size": 9, "version_id": "d7facd2f-68ea-4184-80d3-4dd778a323f6", "key": "myfile"}], "contact_email": "x@example.com", "titles": [{"title": "\u010casov\u00e1n\u00ed sloves v beng\u00e1l\u0161tin\u011b"}], "publication_state": "published", "$schema": "http://localhost:5000/communities/0afede87-2bf2-4d89-867e-d2ee57251c62/schemas/0#/json_schema"}', 1, 1, NULL, 0);
INSERT INTO records_metadata_version (created, updated, id, json, version_id, transaction_id, end_transaction_id, operation_type) VALUES ('2017-11-03 09:04:47.367063', '2017-11-03 09:04:48.096744', '1033083f-edf4-408f-b561-1f23527a926d', '{"resource_types": [{"resource_type_general": "Text"}], "community": "0afede87-2bf2-4d89-867e-d2ee57251c62", "open_access": true, "descriptions": [{"description_type": "Abstract", "description": "Description of verbal paradigms in Bengali. The description is written in Czech."}], "$schema": "http://localhost:5000/communities/0afede87-2bf2-4d89-867e-d2ee57251c62/schemas/0#/draft_json_schema", "_deposit": {"id": "1033083fedf4408fb5611f23527a926d", "owners": [1], "status": "draft", "created_by": 1}, "community_specific": {"2a01ee91-36fe-4edb-9734-73d22ac78821": {"ling_resource_type": ["Text"], "language_code": "eng"}}, "contact_email": "x@example.com", "titles": [{"title": "\u010casov\u00e1n\u00ed sloves v beng\u00e1l\u0161tin\u011b"}], "publication_state": "draft", "creators": [{"creator_name": "Daniel Zeman"}]}', 2, 1, NULL, 1);
INSERT INTO records_metadata_version (created, updated, id, json, version_id, transaction_id, end_transaction_id, operation_type) VALUES ('2017-11-07 15:23:02.240581', '2017-11-07 15:23:02.240599', '6cd752bd-2190-4e21-8a5f-787c5dc416ab', '{"$schema": "https://localhost/api/communities/e9b9792e-79fb-4b07-b6b4-b9c2bd06d095/schemas/0#/draft_json_schema", "_deposit": {"id": "6cd752bd21904e218a5f787c5dc416ab", "created_by": 2, "status": "draft", "owners": [1]}, "publication_state": "draft", "open_access": true, "community": "e9b9792e-79fb-4b07-b6b4-b9c2bd06d095", "titles": [{"title": "This is a deleted deposit"}]}', 1, 5, NULL, 2);
INSERT INTO records_metadata_version (created, updated, id, json, version_id, transaction_id, end_transaction_id, operation_type) VALUES ('2017-11-07 15:23:02.240581', '2017-11-07 15:23:02.240599', '6cd752bd-2190-4e21-8a5f-787c5dc416ab', '{"$schema": "https://localhost/api/communities/e9b9792e-79fb-4b07-b6b4-b9c2bd06d095/schemas/0#/draft_json_schema", "_deposit": {"id": "6cd752bd21904e218a5f787c5dc416ab", "created_by": 2, "status": "draft", "owners": [1]}, "publication_state": "draft", "open_access": true, "community": "e9b9792e-79fb-4b07-b6b4-b9c2bd06d095", "titles": [{"title": "This is a deleted deposit"}]}', 1, 2, 5, 0);


--
-- Data for Name: transaction; Type: TABLE DATA; Schema: public; Owner: b2share
--

INSERT INTO transaction (issued_at, id, remote_addr, user_id) VALUES ('2017-11-03 09:04:45.416258', 1, NULL, 1);


--
-- Name: transaction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: b2share
--

SELECT pg_catalog.setval('transaction_id_seq', 1, true);


--
-- PostgreSQL database dump complete
--

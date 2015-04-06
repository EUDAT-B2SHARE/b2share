-- id, collection name, search parameter
INSERT INTO collection VALUES (100,'Generic','980:Generic',NULL,NULL);
INSERT INTO collection VALUES (101,'Linguistics','980:Linguistics',NULL,NULL);
INSERT INTO collection VALUES (102,'DRIHM','980:DRIHM',NULL,NULL);
INSERT INTO collection VALUES (103,'EUON','980:EUON',NULL,NULL);
INSERT INTO collection VALUES (104,'BBMRI','980:BBMRI',NULL,NULL);
INSERT INTO collection VALUES (105,'NRM','980:NRM',NULL,NULL);
INSERT INTO collection VALUES (106,'GBIF','980:GBIF',NULL,NULL);
INSERT INTO collection VALUES (107,'RDA','980:RDA',NULL,NULL);
-- I don't know what the forth value is. First is parent collection (1 should
-- be site collection), second is child collection. Third I assume is "regular"
-- or "virtual" relationship but I'm not sure what this means...
INSERT INTO collection_collection VALUES (1,100,'r',1);
INSERT INTO collection_collection VALUES (1,101,'r',2);
INSERT INTO collection_collection VALUES (1,102,'r',3);
INSERT INTO collection_collection VALUES (1,103,'r',4);
INSERT INTO collection_collection VALUES (1,104,'r',5);
INSERT INTO collection_collection VALUES (1,105,'r',6);
INSERT INTO collection_collection VALUES (1,106,'r',7);
INSERT INTO collection_collection VALUES (1,107,'r',8);

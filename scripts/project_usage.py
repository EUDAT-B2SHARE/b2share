#!/usr/bin/python

###################################################
### Eudat B2Share storage accounting collector ###
###################################################

import MySQLdb as mdb;
import json
import requests
import datetime
import subprocess

db_con = None
db_name = "invenio"
db_user = ""
db_pwd = ""

RCT_AUTH_TOKEN = ""
RCT_SERVICE_UUID = ""

testing = 0

# DRIHM - 5c29b4c7fe6d4b4d8c779a40b2bb742a
# CLARIN - 601bd733189b4fdd976d8e7c6d987b25
# BBMRI - 8186b5c480f148f3bb747e4e530a5d32
# EUON - 4f3094018821495c9317225cf76c2a7f
# EUDAT - b9e37dca5bc74f4592d2750f023c42af
# NRM - 91f1a264906a4e7688a479e620cba8c8

projects = {
'5c29b4c7fe6d4b4d8c779a40b2bb742a':19,
'601bd733189b4fdd976d8e7c6d987b25':1,
'b9e37dca5bc74f4592d2750f023c42af':2,
'4f3094018821495c9317225cf76c2a7f':4,
'8186b5c480f148f3bb747e4e530a5d32':17
'91f1a264906a4e7688a479e620cba8c8':20
}

RCT_API_PREFIX = "https://rct.eudat.eu/api/1.0/"
RCT_SERVICE_URI = RCT_API_PREFIX+"services/"+RCT_SERVICE_UUID+"/"

try:
        db_con = mdb.connect('localhost',db_user,db_pwd,db_name)

        for k in projects.keys():
                cur = db_con.cursor()
                cur.execute("select t1.id_bibdoc,t2.id_bibrec,sum(t3.filesize),count(t1.id_bibrec) from bibrec_bibdoc as t1, bibrec_bib98x as t2, bibdocfsinfo as t3 where t2.id_bibxxx=%s AND t1.id_bibrec=t2.id_bibrec AND t1.id_bibdoc=t3.id_bibdoc",(projects[k],))

                ret = cur.fetchone()

                cur.execute("select count(*) from bibrec_bib98x WHERE id_bibxxx=%s",(projects[k],))
                ret2 = cur.fetchone()
                
                RCT_RESOURCE_UUID = k

                if ret2[0] is not None and ret[2] is not None:
                        record = {
                                'storagespace': RCT_API_PREFIX+"storagespaces/"+RCT_RESOURCE_UUID+"/",
                                'service': RCT_SERVICE_URI,
                                'used_objects': int(ret2[0]),
                                'used_space': int(ret[2]),
                                'measure_time': datetime.datetime.now().isoformat()
                        }
                        records = [record,]

                        data = json.dumps(records)

                        print "used_space: " + str(ret[2])
                        print "used_objects: " + str(ret2[0])

                        url = RCT_API_PREFIX+"storagespaceaccountingrecords/"
                        headers = {
                                'Authorization': 'Token '+RCT_AUTH_TOKEN,
                                'Content-Type': 'application/json',
                        }

                        if testing == 0:
                                r = requests.post(url,data=data,headers=headers)
                                print "Status: " + str(r.status_code)

except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)

finally:
        if db_con:
                db_con.close()


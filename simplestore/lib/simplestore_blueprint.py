from flask import Flask, request, current_app

from invenio.webinterface_handler_flask_utils import InvenioBlueprint
from invenio.config import CFG_TMPDIR
from invenio.websubmit_config import InvenioWebSubmitFunctionError
from invenio.websubmit_functions.Shared_Functions import ParamFromFile
from invenio.bibtask import task_low_level_submission, bibtask_allocate_sequenceid


blueprint = InvenioBlueprint('simplestore', __name__, url_prefix="/simplestore")


@blueprint.route('/submit')
#@blueprint.invenio_authenticated
@blueprint.invenio_templated(template='simplestore-submit.html')
def submit_example():
    # construct a MARC
    entry = """
    <example>
    </example>
    """
    # submit a new entry and get a processing_id
    processing_id = 43 #_submit(entry)
    if False and approval_required:
        # poll for the processing id as long as the session is live
        # return "The record was submitted with the PID: %s " %record id
        pass
    return dict(processing_id = processing_id)
    #return "The record was submitted for processing %s" % processing_id


def _submit(entry):
    return 43
    # ???
    sequence_id = bibtask_allocate_sequenceid(curdir)
    # create a temporary file for submission
    tmp_fd, tmpfile = tempfile.mkstemps()
    # dump generated MARC into the entry
    os.write(tmp_fd, entry)
    os.close(tmp_fd)
    # submit the entry to the processing unit
    bibupload_id = task_low_level_submission('bibupload', 'websubmit.simplestore', '-r', '-i', tmpfile, '-P', '3', '-I', str(sequence_id))
    return bibupload_id


def _expand_entry(origId, addMARC):
    """Expand metadata of the entry with orgiId unique id with the provided addMARC xml metadata"""
    # lookup an entry object
    entry = lookup_entry(origId)
    # update entries MARC entry with the new fields
    some.utils.updateMARC(entry.marc, addMarc)


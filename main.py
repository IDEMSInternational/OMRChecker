from firebase_admin import firestore
import firebase_admin
import functions_framework
from google.cloud import storage

from pathlib import Path
import uuid
import json
from src.entry import process_from_url


def upload_blob_from_memory(bucket_name, contents, destination_blob_name):
    """Uploads a file to the bucket."""

    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The contents to upload to the file
    # contents = "these are my contents"

    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(contents)

    print(
        f"{destination_blob_name} with contents {contents} uploaded to {bucket_name}."
    )


@functions_framework.http
def hello_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args

    if 'image_url' in request_json:
        image_url = request_json['image_url']
    else:
        return json.dumps({'error' : 'Missing Image URL'})

    if 'student_name' in request_json:
        student_name = request_json['student_name']
    else:
        return json.dumps({'error' : 'Missing Student name'})

    out = process_from_url(image_url, Path("inputs/sheet_small_markers/template.json"))
    out['uuid'] = str(uuid.uuid4())
    return json.dumps(out)

    # if request_json and 'name' in request_json:
    #     name = request_json['name']
    # elif request_args and 'name' in request_args:
    #     name = request_args['name']
    # else:
    #     name = 'World'
    # db = firestore.client()
    # doc_ref = db.collection(u'users').document(u'alovelace')
    # doc_ref.set({
    #     u'first': u'Ada',
    #     u'last': u'Lovelace',
    #     u'born': 1815
    # })
    # upload_blob_from_memory('competition-sheet-photos', 'file content', 'text.txt')
    # return 'Hello {}!'.format(name)

# Application Default credentials are automatically created.
app = firebase_admin.initialize_app()
from firebase_admin import firestore
import firebase_admin
import functions_framework
from google.cloud import storage

import io
import csv
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

def validate_processing(request_json):
    required_fields = {
        "student_name",
        "image_url",
        "teacher_name",
        "teacher_uuid",
        "school_name",
        "district",
        "sector",
        "type_of_school",
        "competition_id"
    }

    for field in required_fields:
        if field not in request_json:
            return f'Missing {field}'
    return None


def validate_submission(request_json):
    required_fields = {
        "uuid",
        "competition_id",
        "student_name",
        "gender",
        "level",
        "answers"
    }

    for field in required_fields:
        if field not in request_json:
            return f'Missing {field}'
    return None


def write_record(data):
    # data is a dict
    db = firestore.client()
    doc_ref = db.collection(u'student_sheets').document(data['uuid'])
    doc_ref.set(data)


def update_record(data):
    db = firestore.client()
    doc_ref = db.collection(u'student_sheets').document(data['uuid'])
    if not doc_ref.get().exists:
        return 'Invalid UUID', 400
    doc_ref.set(data | {'validated' : True}, merge=True)
    return "Success", 200


def get_field(field, doc):
    if field in doc:
        return doc[field]
    else:
        # qXX
        qid = int(field[1:])-1
        return doc['answers'][qid]


def list_records(competition_id):
    db = firestore.client()
    col_ref = db.collection(u'student_sheets')
    q = col_ref.where(u'competition_id', u'==', competition_id) \
               .where(u'validated', u'==', True)
    docs = q.stream()
    fieldnames = [
        "validated",
        "student_name",
        "gender",
        "level",
    ] + [f'q{i}' for i in range(1,21)] + [
        "teacher_name",
        "school_name",
        "district",
        "sector",
        "type_of_school",
        "teacher_uuid",
        "uuid",
        "image_url",
    ]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for doc in docs:
        doc = doc.to_dict()
        writer.writerow({field : get_field(field, doc) for field in fieldnames})
    return output.getvalue()


def process_image(request):
    request_json = request.get_json(silent=True)
    if not request_json:
        return 'No Data', 400
    result = validate_processing(request_json)
    if result is not None:
        return result, 400
    image_url = request_json['image_url']
    student_name = request_json['student_name']
    out = process_from_url(image_url, Path("inputs/sheet_small_markers/template.json"))
    out['uuid'] = str(uuid.uuid4())
    write_record(request_json | out | {'validated' : False})
    # TODO: store image
    # TODO: timestamps
    # TODO: Rapidpro: safe escaping for json sending
    # upload_blob_from_memory('competition-sheet-photos', 'file content', 'text.txt')
    return json.dumps(out), 200


def submit_answers(request):
    request_json = request.get_json(silent=True)
    if not request_json:
        return 'No Data', 400
    result = validate_submission(request_json)
    if result is not None:
        return result, 400
    return update_record(request_json | {'validated' : True})


def show_records(request):
    request_args = request.args
    if not 'competition_id' in request_args:
        return "Nothing to see here (no competition_id).", 200
    cid = request_args['competition_id']
    out = list_records(cid)
    return out, 200


@functions_framework.http
def serve(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """

    path = request.path.strip('/')
    if path == 'process_image':
        return process_image(request)
    elif path == 'submit_answers':
        return submit_answers(request)
    else:
        return show_records(request)


# Application Default credentials are automatically created.
app = firebase_admin.initialize_app()
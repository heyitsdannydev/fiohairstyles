from __future__ import annotations

import uuid
from pathlib import PurePosixPath

from app.controllers import DOCUMENTS_BUCKET, _s3, _table
from app.controllers.appointment import _key_from_sk
from app.models.appointment import Appointment

_DOWNLOAD_URL_TTL = 300  # seconds


def _get_item(sk: str) -> dict | None:
    return _table.get_item(Key=_key_from_sk(sk)).get("Item")


def add_appointment_document(
    sk: str, label: str, filename: str, content: bytes, content_type: str
) -> Appointment | None:
    item = _get_item(sk)
    if item is None:
        return None

    # Keep just the basename so a client-supplied path can't escape the
    # per-appointment prefix; the uuid segment keeps keys unique even when
    # two files share a name.
    safe_name = PurePosixPath(filename or "document").name or "document"
    key = f"appointments/{sk}/{uuid.uuid4()}/{safe_name}"

    _s3.put_object(
        Bucket=DOCUMENTS_BUCKET,
        Key=key,
        Body=content,
        ContentType=content_type or "application/octet-stream",
    )

    files = list(item.get("Files") or [])
    files.append({"Label": label, "S3Path": key})
    _table.update_item(
        Key=_key_from_sk(sk),
        UpdateExpression="SET #f = :files",
        ExpressionAttributeNames={"#f": "Files"},
        ExpressionAttributeValues={":files": files},
    )
    item["Files"] = files
    return Appointment(**item)


def delete_appointment_document(sk: str, s3_path: str) -> Appointment | None:
    item = _get_item(sk)
    if item is None:
        return None

    files = list(item.get("Files") or [])
    remaining = [f for f in files if f.get("S3Path") != s3_path]
    if len(remaining) == len(files):
        # Nothing matched — treat as a no-op rather than deleting an
        # unrelated object from the bucket.
        return Appointment(**item)

    _s3.delete_object(Bucket=DOCUMENTS_BUCKET, Key=s3_path)
    _table.update_item(
        Key=_key_from_sk(sk),
        UpdateExpression="SET #f = :files",
        ExpressionAttributeNames={"#f": "Files"},
        ExpressionAttributeValues={":files": remaining},
    )
    item["Files"] = remaining
    return Appointment(**item)


def appointment_document_url(sk: str, s3_path: str) -> str | None:
    item = _get_item(sk)
    if item is None:
        return None

    files = item.get("Files") or []
    if not any(f.get("S3Path") == s3_path for f in files):
        # Only hand out URLs for documents actually attached to this
        # appointment.
        return None

    return _s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": DOCUMENTS_BUCKET, "Key": s3_path},
        ExpiresIn=_DOWNLOAD_URL_TTL,
    )

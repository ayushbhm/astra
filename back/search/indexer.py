import hashlib
import struct

from models.model import Case, CaseSearchEmbedding, db
from search.providers import NVIDIA_MODEL, nvidia_embedder


def case_document(case):
    tags = ", ".join(sorted(tag.name for tag in case.tags))
    return "\n".join(filter(None, [
        f"Case title: {case.title or ''}",
        f"Place: {case.place or ''}; state: {case.state or ''}",
        f"Tags: {tags}" if tags else "",
        f"Life events and case notes: {(case.story or '')[:12000]}",
    ]))


def _pack(vector):
    return struct.pack(f"<{len(vector)}f", *(float(value) for value in vector))


def _fingerprint(document):
    return hashlib.sha256(document.encode("utf-8")).hexdigest()


def sync_case_index():
    cases = Case.query.order_by(Case.id.asc()).all()
    existing = {row.case_id: row for row in CaseSearchEmbedding.query.all()}
    changed = []
    unchanged = 0
    live_ids = {case.id for case in cases}

    for case in cases:
        document = case_document(case)
        fingerprint = _fingerprint(document)
        row = existing.get(case.id)
        if row and row.content_hash == fingerprint and row.model == NVIDIA_MODEL:
            unchanged += 1
        else:
            changed.append((case, document, fingerprint))

    indexed = 0
    for offset in range(0, len(changed), 16):
        batch = changed[offset:offset + 16]
        vectors = nvidia_embedder.embed([item[1] for item in batch], input_type="passage")
        for (case, _document, fingerprint), vector in zip(batch, vectors):
            row = existing.get(case.id) or CaseSearchEmbedding(case_id=case.id)
            row.content_hash = fingerprint
            row.model = NVIDIA_MODEL
            row.vector = _pack(vector)
            db.session.add(row)
            existing[case.id] = row
            indexed += 1

    removed = 0
    for case_id, row in existing.items():
        if case_id not in live_ids:
            db.session.delete(row)
            removed += 1
    db.session.commit()
    return {"indexed": indexed, "unchanged": unchanged, "removed": removed, "total": len(cases)}

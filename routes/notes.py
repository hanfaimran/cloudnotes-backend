from flask import Blueprint, request, jsonify, session
from extensions import db
from models.models import Note
from utils.cloudinary_helper import upload_file_to_cloudinary
import cloudinary

notes_bp = Blueprint("notes", __name__)


def get_current_user_id():
    return session.get("user_id")


@notes_bp.route("/", methods=["GET"])
def get_notes():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    search = request.args.get("q", "").strip()
    query = Note.query.filter_by(user_id=user_id)

    if search:
        query = query.filter(
            db.or_(
                Note.title.ilike(f"%{search}%"),
                Note.content.ilike(f"%{search}%")
            )
        )

    notes = query.order_by(Note.pinned.desc(), Note.updated_at.desc()).all()
    return jsonify({"notes": [n.to_dict() for n in notes]}), 200


@notes_bp.route("/", methods=["POST"])
def create_note():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    color = request.form.get("color", "#ffffff")
    pinned = request.form.get("pinned", "false") == "true"

    if not title:
        return jsonify({"error": "Title is required"}), 400

    image_url = None
    file_url = None
    file_name = None

    if "image" in request.files:
        file = request.files["image"]
        if file.filename:
            result = upload_file_to_cloudinary(file, folder="cloudnotes/images", resource_type="image")
            if result:
                image_url = result["secure_url"]

    if "file" in request.files:
        file = request.files["file"]
        if file.filename:
            file_name = file.filename
            result = upload_file_to_cloudinary(file, folder="cloudnotes/files", resource_type="raw")
            if result:
                file_url = result["secure_url"]

    note = Note(
        user_id=user_id,
        title=title,
        content=content,
        color=color,
        pinned=pinned,
        image_url=image_url,
        file_url=file_url,
        file_name=file_name
    )
    db.session.add(note)
    db.session.commit()
    return jsonify({"note": note.to_dict()}), 201


@notes_bp.route("/<int:note_id>", methods=["PUT"])
def update_note(note_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    note = Note.query.filter_by(id=note_id, user_id=user_id).first()
    if not note:
        return jsonify({"error": "Note not found"}), 404

    title = request.form.get("title", note.title).strip()
    content = request.form.get("content", note.content)
    color = request.form.get("color", note.color)
    pinned = request.form.get("pinned")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    note.title = title
    note.content = content
    note.color = color
    if pinned is not None:
        note.pinned = pinned == "true"

    if "image" in request.files:
        file = request.files["image"]
        if file.filename:
            result = upload_file_to_cloudinary(file, folder="cloudnotes/images", resource_type="image")
            if result:
                note.image_url = result["secure_url"]

    if "file" in request.files:
        file = request.files["file"]
        if file.filename:
            note.file_name = file.filename
            result = upload_file_to_cloudinary(file, folder="cloudnotes/files", resource_type="raw")
            if result:
                note.file_url = result["secure_url"]

    db.session.commit()
    return jsonify({"note": note.to_dict()}), 200


@notes_bp.route("/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    note = Note.query.filter_by(id=note_id, user_id=user_id).first()
    if not note:
        return jsonify({"error": "Note not found"}), 404

    db.session.delete(note)
    db.session.commit()
    return jsonify({"message": "Note deleted"}), 200


@notes_bp.route("/<int:note_id>/pin", methods=["PATCH"])
def toggle_pin(note_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    note = Note.query.filter_by(id=note_id, user_id=user_id).first()
    if not note:
        return jsonify({"error": "Note not found"}), 404

    note.pinned = not note.pinned
    db.session.commit()
    return jsonify({"note": note.to_dict()}), 200

import cloudinary
import cloudinary.uploader
from flask import current_app


def configure_cloudinary():
    cloudinary.config(
        cloud_name=current_app.config["CLOUDINARY_CLOUD_NAME"],
        api_key=current_app.config["CLOUDINARY_API_KEY"],
        api_secret=current_app.config["CLOUDINARY_API_SECRET"],
        secure=True
    )


def upload_file_to_cloudinary(file, folder="cloudnotes", resource_type="auto"):
    try:
        configure_cloudinary()
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type=resource_type
        )
        return result
    except Exception as e:
        print(f"Cloudinary upload error: {e}")
        return None

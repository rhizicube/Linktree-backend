from fastapi import UploadFile, File
from core.settings import settings
import secrets, os, shutil


def save_uploaded_image(file:UploadFile=File(...)) -> str:
	"""Function to save uploaded image

	Args:
		file (UploadFile, optional): Uploaded image. Defaults to File(...).

	Returns:
		str: image path
	"""
	filename, file_extension = os.path.splitext(file.filename)
	img_token = secrets.token_hex(10) + file_extension
	img_path = os.path.join(settings.MEDIA_ROOT, img_token)
	with open(img_path, 'wb') as f:
		shutil.copyfileobj(file.file, f)
	return img_path
from fastapi import UploadFile, File
from core.settings import settings
import secrets, os, shutil
from ipaddress import ip_address, IPv4Address


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


def valid_ip_address(addr: str) -> str:
	"""Function to identify if the given IP address is of type IPv4 or IPv6

	Args:
		addr (str): IP address

	Returns:
		str: IPv4 or IPv6 or invalid
	"""
	try:
		return "IPv4" if type(ip_address(addr)) is IPv4Address else "IPv6"
	except Exception as e:
		return "Invalid"


import secrets, string, urllib
from user_agents import parse
from core.constants import locationDatabaseIPv4, locationDatabaseIPv6
from utilities.generic import valid_ip_address

from db_connect.config import mongoDB




async def create_cookie_id() -> str:
	"""Function to create cookie

	Returns:
		str: cookie id
	"""
	mongoDBConnection = mongoDB.database
	short_url_length = 25
	distinct_sessions = await mongoDBConnection["views"].distinct("session_id")
	print(distinct_sessions)
	while True:
		res = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(short_url_length))
		if str(res) not in distinct_sessions:
			break
	cookie_id = str(res)
	return cookie_id

def get_client_details(request) -> tuple:
	"""Function to get visitor's device type and location details based on their IP address

	Args:
		request (Request): API Request

	Returns:
		tuple: device type as string, and location details as dict
	"""
	user_agent = parse(request.headers.get('user-agent'))
	device_type = None
	if user_agent.is_mobile:
		device_type = "mobile"
	elif user_agent.is_pc:
		device_type = "pc"
	elif user_agent.is_tablet:
		device_type = "tablet"
	elif user_agent.is_bot:
		device_type = "bot"
	elif user_agent.is_email_client:
		device_type = "email_client"
	elif user_agent.is_touch_capable:
		device_type = "touch_capable"
	else:
		device_type = "other"

	client_host = request.client.host
	if client_host == "127.0.0.1":
		# Local testing
		client_host = urllib.request.urlopen('https://ident.me').read().decode('utf8')
	
	# If visitor's location to be found from the database corresponding to the type of IP address (IPv4/IPv6)
	ip_address_type = valid_ip_address(client_host)
	if ip_address_type == "IPv4":
		locobj = locationDatabaseIPv4.get_all(client_host)
	elif ip_address_type == "IPv6":
		locobj = locationDatabaseIPv6.get_all(client_host)
	else:
		print("Invalid IP address", client_host)
		return device_type, {}

	
	location = {"ip": locobj.ip, "country": locobj.country_long, "region": locobj.region, "city": locobj.city, "latitude": locobj.latitude, "longitude": locobj.longitude}
	
	return device_type, location

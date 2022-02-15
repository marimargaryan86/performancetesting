import re
import uuid

COLOR_REGEX = "^[0-9A-F]{6}$"
LANGUAGE_REGEX = re.compile("^[A-Z]{2}(-[A-Z]{2})?$", flags=re.IGNORECASE)
LATITUDE_MIN = -90
LATITUDE_MAX = 90
LONGITUDE_MIN = -180
LONGITUDE_MAX = 180
NAMESPACE = uuid.UUID("3cbbd269-773c-481b-bc1c-c59dfc19a063")

LLM_ENDPOINT = "http://localhost:11434/api/generate"
LLM_MODEL = "llama3.2:3b"

MAP_PROVIDER = "osm"  # future: "google"

MAX_RESULTS = 5

# OpenStreetMap / Nominatim
NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"
OSRM_BASE_URL = "https://router.project-osrm.org"
PHOTON_BASE_URL = "https://photon.komoot.io/api"


USER_AGENT = "LocalLLM-Maps/1.0 (learning project; contact: yourname@example.com)"


LLM_REQUEST_TIMEOUT = 60  # seconds
HTTP_REQUEST_TIMEOUT = 10

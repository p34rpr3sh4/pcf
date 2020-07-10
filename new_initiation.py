from system.db_initiation import create_db
from system.config_load import change_secret_key
from system.cert_initiation import create_self_signed_cert

create_db()

change_secret_key()

create_self_signed_cert()

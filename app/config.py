import os


class Config:

    # ======================================
    # FLASK
    # ======================================

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "centro_medico_secret_key_2026"
    )

    DEBUG = True


    # ======================================
    # MYSQL
    # ======================================

    MYSQL_HOST = "localhost"

    MYSQL_USER = "root"

    MYSQL_PASSWORD = "77454419"

    MYSQL_DB = "centro_medico"


    # ======================================
    # OPCIONAL
    # ======================================

    MYSQL_CURSORCLASS = "DictCursor"
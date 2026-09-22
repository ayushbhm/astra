class Config:
    SECRET_KEY = 'your_secret_key'
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///house.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = "redis://127.0.0.1:6379"
    #CELERY_BROKER_URL = 'redis://localhost:6379/0'
    #CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
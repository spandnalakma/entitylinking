import logging.config
from pythonjsonlogger import jsonlogger
from flask_restful import Api, Resource
from flask import Flask, jsonify, request

from api.NER import NER


application = Flask(__name__)
api = Api(application)

# Logger Configuration
logging.config.fileConfig('logging.ini')
logger = logging.getLogger('Logger')


class CheckHealth(Resource):
    @staticmethod
    def get():
        return 'Server is working!'


api.add_resource(NER, '/ner')
api.add_resource(CheckHealth, '/health')

if __name__ == '__main__':
    logger.info('Server is running.')
    application.run(debug=True)

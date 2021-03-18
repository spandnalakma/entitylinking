import en_core_web_lg

from nltk.stem import PorterStemmer, WordNetLemmatizer
from collections import defaultdict
from flask import jsonify, request
from flask_restful import Resource
import re
import nltk
from .preprocessing import preprocess
import logging
import spacy
import requests
from requests import utils
import sys
sys.path.append(".")  # Adds higher directory to python modules path.

nltk.download('wordnet')
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()
logger = logging.getLogger('Logger')

#spacy_NE_recognizer = en_core_web_lg.load()
spacy_NE_recognizer = spacy.load("./output_50k_model/nlp")



def remap_entity_label(spacy_label):
    spacy_property_map = {
        'org': 'brands',
        'location': 'locations',
        'loc': 'locations',
        'gpe': 'geopolitical',
        'event': 'events',
        'language': 'languages',
        'law': 'laws',
        'norp': 'nationalities',
        'person': 'people',
        'percent': 'percentages',
        'product': 'products',
        'ordinal': 'ordinal',
    }
    return spacy_property_map[spacy_label.lower()]


def recognize_custom_named_entities(text):

    ne_dictionary = {}

    # Function: To add / append NER with QId
    def fit_named_entity(entity_name, start_char, end_char, category, wiki):
        print(entity_name, start_char, end_char, category)
        print("wiki object", wiki)

        def create_named_entity_instance():
            instance = {
                'startChar': start_char,
                'endChar': end_char,
            }

            return instance

        
        def create_named_entity():
            ne_dictionary[category].append({
                'name': entity_name,
                'wikiId': wiki['wikiId'],
                'referenceUrl': wiki['refrence_url'],
                'instances': [create_named_entity_instance()],
            })

        def append_named_entity_instance(constructed_token_index):

            # finds if instance already exists on given constructed token. returns True \ False
            def does_instance_exist():
                for instance in ne_dictionary[category][constructed_token_index]['instances']:
                    return start_char == instance['startChar'] and end_char == instance['endChar']

            if not does_instance_exist():
                ne_dictionary[category][constructed_token_index]['instances'].append(
                    create_named_entity_instance())

        def index_of_named_entity():
            if category not in ne_dictionary:
                ne_dictionary.update({category: list()})
                return False

            for index, entity in enumerate(ne_dictionary[category]):
                if entity_name == entity['name']:
                    return index
            return False

        
        found_named_entity_idx = index_of_named_entity()

        
        if found_named_entity_idx is not False:
            append_named_entity_instance(found_named_entity_idx)
        else:
            create_named_entity()

    
    spacy_document = spacy_NE_recognizer(preprocess(text))
    lang = "en"
    wikipedia_url = ''
    wikipedia_title = ''
    for entity in spacy_document.ents:
        Qid = entity.kb_id_
        url = (
            'https://www.wikidata.org/w/api.php'
            '?action=wbgetentities'
            '&props=sitelinks/urls'
            f'&ids={Qid}'
            '&format=json'
        )
        json_res = requests.get(url).json()
        entities = json_res.get('entities')
        print(entities)
        if entities:
            entity_ = entities.get(Qid)
            if entity_:
                sitelinks = entity_.get('sitelinks')
                if sitelinks:
                    sitelink = sitelinks.get(f'{lang}wiki')
                    if sitelink:
                        wiki_url = sitelink.get('url')
                        wikipedia_title = sitelink.get('title')
                        if wiki_url:
                            wikipedia_url = requests.utils.unquote(
                                wiki_url)
        wiki = {"wikiId": Qid, "Description": wikipedia_title,
                "refrence_url": wikipedia_url}
        fit_named_entity(entity_name=entity.text, start_char=entity.start_char, end_char=entity.end_char,
                         category=remap_entity_label(entity.label_), wiki=wiki)

    return ne_dictionary


class NER(Resource):
    @staticmethod
    def post():
        posted_data = dict(request.get_json())
        text = posted_data['text']

        logger.info("Start: Request for Recognize Named Entities")

        result = jsonify(recognize_custom_named_entities(text))
        logger.info("Finish: Request for Recognize Named Entities")
        return result

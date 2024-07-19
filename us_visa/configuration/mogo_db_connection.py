import os ,sys 
from us_visa.exception import ClassificationException
from us_visa.logger import logging 

from us_visa.configuration import VisaClassficationConfiguration 
from us_visa.entity.config_entity import MongoDBCOnfig

import pymongo ,certifi 


ca = certifi.where() #To deal with timout error


class MongoDBClient:
    """This Class will help you to make connection with MongoDB Database where your data is saved"""
    client =None
    def __init__(self ,config : MongoDBCOnfig) -> None:
        try:
            self.config = config
            if MongoDBClient.client is None:
                mongodb_url = self.config.mongodb_url
                if mongodb_url is None:
                    raise Exception(f"Unale to find Environment Key")
                
                MongoDBClient.client = pymongo.MongoClient(mongodb_url, tlsCAFile=ca)
            self.client = MongoDBClient.client 
            self.database = self.client[self.config.database_name]
            self.database_name = self.config.database_name
            logging.info("MongoDB Connection succrsfull")
        except Exception as e:
            raise ClassificationException(e ,sys) from e 
        
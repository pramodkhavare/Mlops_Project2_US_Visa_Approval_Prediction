from us_visa.configuration.mogo_db_connection import MongoDBClient
from us_visa.configuration import VisaClassfication
from us_visa.exception import ClassificationException
from us_visa.constants import * 
import sys ,os 
import numpy as np 

class USVisaData:
    """
        This class help to export entire mongo db record as pandas dataframe
    """ 
    
    def __init__(self):
        try:
            self.mogodeb_client = MongoDBClient()
        except Exception as e:
            raise ClassificationException(e ,sys) from e
        
     
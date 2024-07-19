from us_visa.exception import ClassificationException
from us_visa.logger import logging 

from us_visa.pipline.training_pipeline import TrainPipeline 
from us_visa.configuration import VisaClassficationConfiguration


pipeline = TrainPipeline(config=VisaClassficationConfiguration())
pipeline.run_pipeline()

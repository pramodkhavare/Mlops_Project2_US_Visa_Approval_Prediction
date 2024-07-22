from us_visa.configuration import VisaClassficationConfiguration
import os ,sys 
from us_visa.configuration import ModelTrainingConfig  
from us_visa.entity.config_entity import DataIngestionConfig ,MongoDBCOnfig,ModelTrainingConfig
from us_visa.entity.artifact_entity import DataIngestionArtifact ,DataTransformationArtifact ,ClassificationMetricArtifact ,ModelTrainingArtifacts
from us_visa.logger import logging
from us_visa.exception import ClassificationException
import os ,sys 
import tarfile 
import pandas as pd 
import numpy as np 
from us_visa.utils.main_utils import read_yaml ,save_numpy_array  ,save_object ,load_array ,load_object
from us_visa.constants import *
import pickle
from typing import List
# from Housing.src.entity.model_factory import evaluate_regression_model
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from neuro_mf import ModelFactory

class US_Visa_Prediction():
    def __init__(self ,model_obj , preprocessor_obj):
        self.model_obj = model_obj 
        self.preprocessor_obj = preprocessor_obj 
        
    def predict(self ,X):
        try:
            transformed_feature = self.preprocessor_obj.transform(X)
            prediction = self.model_obj.predict(transformed_feature) 
            return prediction
        except  Exception as e:
            logging.info("Unable To Predict Output")
            raise VisaClassficationConfiguration(e,sys) from e 
        
        
class ModelTrainer():
    def __init__(self ,
                 model_training_config : ModelTrainingConfig ,
                 data_transformation_artifacts : DataTransformationArtifact):
        try:
            logging.info(f'\n\n{"*" *20} Model Training Started{"*" *20}')
            self.model_training_config = model_training_config 
            self.data_transformation_artifacts = data_transformation_artifacts
        except  Exception as e:
            raise VisaClassficationConfiguration(e,sys) from e 
        
    def get_model_object_and_report(self ,train_array :np.array ,test_array :np.array):
        """
        Method Name :   get_model_object_and_report
        Description :   This function uses neuro_mf to get the best model object and report of the best model
        
        Output      :   Returns metric artifact object and best model object
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            
            logging.info("Using Neuro MF to get best model and report")
            
            logging.info("Extracting Model Information From Config File")
            model_config_file_path= self.model_training_config.model_config_file_path
            
            
            model_factory = ModelFactory(
                model_config_path=model_config_file_path
            )
            

            x_train ,y_train ,x_test ,y_test = train_array[: ,:-1] ,train_array[: ,-1] ,test_array[: ,:-1] ,test_array[: ,-1]
            logging.info(f"Shape of train and test data is x_train: [{x_train.shape}] ,x_test : [{x_test.shape}] ,y_train: [{y_train.shape}] ,y_test:[{y_test.shape}]")
            
            
            base_accuracy = self.model_training_config.base_accuracy
            best_model_details =model_factory.get_best_model(X=x_train 
                                                            ,y=y_train ,base_accuracy=base_accuracy)
            
            best_model_obj = best_model_details.best_model
            
            
            
            logging.info(f"Best Model We Found On Training Data Is :[{best_model_obj}]")
    
            y_pred = best_model_obj.predict(x_test)
            
            
            accuracy = accuracy_score(y_test ,y_pred)
            f1 = f1_score(y_test ,y_pred)
            precision = precision_score(y_test ,y_pred)
            recall = recall_score(y_test ,y_pred)
            print(000000000000000)
            print(accuracy ,f1 ,precision ,recall)
            metricArtifacct = ClassificationMetricArtifact(
                f1_score= f1 ,
                precision= precision ,
                recall_score= recall 
            )   
            
            return   best_model_details , metricArtifacct       
            
        except  Exception as e:
            raise VisaClassficationConfiguration(e,sys) from e 
        
        
    def initiate_model_training(self)->ModelTrainingArtifacts:
        try:
            logging.info("Loading Transformed Data Into Varible")  
            
            transformed_train_file_path = self.data_transformation_artifacts.transformed_train_file_path
            transformed_test_file_path = self.data_transformation_artifacts.transformed_test_file_path 
            
            train_array = load_array(transformed_train_file_path)
            test_array = load_array(transformed_test_file_path)
            
            best_model_object , metricArtifacct = self.get_model_object_and_report(
                train_array= train_array ,test_array= test_array
            )
            
            preprocessing_obj = load_object(file_path= self.data_transformation_artifacts.preprocessor_file_path)
            
            if best_model_object.best_score < self.model_training_config.base_accuracy:
                logging.info("No Best Model Was Found With Accuracy More than base accuracy")
                raise Exception ("No Best Model Found More Than Base Accuracy")
            
            model_for_training_prediction = US_Visa_Prediction(
                model_obj= best_model_object ,
                preprocessor_obj= preprocessing_obj
            )
            
            trained_model_file_path =os.path.join(self.model_training_config.trained_model_dir_path ,self.model_training_config.trained_model_name)
            print(1223)
            save_object(file_path=trained_model_file_path ,obj=model_for_training_prediction)
            print(1223)
            model_trainer_artifacts = ModelTrainingArtifacts(
                trained_model_file_path= trained_model_file_path,
                metrics_artifact= metricArtifacct
            )
            logging.info(model_trainer_artifacts)

            return model_trainer_artifacts
            
            
        except  Exception as e:
            raise VisaClassficationConfiguration(e,sys) from e 

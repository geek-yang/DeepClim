# -*- coding: utf-8 -*-
"""
Copyright Netherlands eScience Center
Function        : Evaluation matrix
Author          : Yang Liu (y.liu@esciencecenter.nl)
First Built     : 2020.04.01
Last Update     : 2020.04.01
Contributor     :
Description     : This scripts provides the basic functions, which will be used by other modules.
Return Values   : time series / array
Caveat!         :
"""

import math
import numpy as np
import os
import torch
import torch.nn as nn
import torch.nn.functional as F

def RMSE(x,y):
    """
    Calculate the RMSE. x is input series and y is reference series.
    It calculates RMSE over the domain, not over time. The spatial structure
    will not be kept.
    ----------------------
    param x: input time series with the shape [time, lat, lon]
    param y: reference time series with the shape [time, lat, lon]
    """
    # error score for temporal-spatial fields, without keeping spatial pattern
    x_series = x.reshape(x.shape[0],-1)
    y_series = y.reshape(y.shape[0],-1)
    rmse = np.sqrt(np.mean((x_series - y_series)**2,1))
    rmse_std = np.sqrt(np.std((x_series - y_series)**2,1))
    
    return rmse, rmse_std

def MAE(x,y):
    """
    Calculate the MAE. x is input series and y is reference series.
    It calculate MAE over time and keeps the spatial structure.
    """
    # error score for temporal-spatial fields, keeping spatial pattern
    mae = np.mean(np.abs(x-y),0)
      
    return mae

def accuracy(pred, label):
    """
    Calculate accuracy score.
    """
    #print("Input size must be [seq, lat, lon]")
    seq, lat, lon = pred.shape
    boolean = (pred==label)
    accu_seq = np.mean(np.mean(boolean.astype(float),2),1)
    accu_spa = np.mean(boolean.astype(float),0)
        
    return accu_seq, accu_spa

# positive is sea ice = 1

def recall(pred, label):
    """
    True positive / Total actual positive
    Input fields must contain only 0 / 1. 1 is positive.
    """
    #print("Input size must be [seq, lat, lon]")
    seq, lat, lon = pred.shape
    # initialize dummy matrix
    pred_dummy_1 = np.zeros(pred.shape,dtype=int)
    label_dummy_1 = np.zeros(label.shape,dtype=int)
    # True positive
    # create dummy matrix to save the labels
    pred_dummy_1[:] = pred[:]
    label_dummy_1[:] = label[:]
    # change the label of negative events
    pred_dummy_1[pred == 0] = 2
    label_dummy_1[label == 0] = 3
    # count True Positive events
    truePositive = (pred_dummy_1 == label_dummy_1)
    
    # initialize dummy matrix
    pred_dummy_2 = np.zeros(pred.shape,dtype=int)
    label_dummy_2 = np.zeros(label.shape,dtype=int)
    # False negative (is 1 but predict 0)
    # create dummy matrix to save the labels (reset dummy)
    pred_dummy_2[:] = pred[:]
    label_dummy_2[:] = label[:]
    pred_dummy_2[pred == 0] = 2
    label_dummy_2[label == 1] = 2
    # count False Positive events
    falseNegative = (pred_dummy_2 == label_dummy_2)
    
#    recall_seq = np.mean(np.mean(np.nan_to_num(truePositive.astype(float) / 
#                                     (truePositive.astype(float) + falseNegative.astype(float))),2),1)
        
    recall_seq = np.sum(np.sum(truePositive.astype(float),2),1) / (np.sum(np.sum(truePositive.astype(float),2),1) +
                                                                    np.sum(np.sum(falseNegative.astype(float),2),1))
        
#    recall_spa = np.mean(np.nan_to_num(truePositive.astype(float) / 
#                                           (truePositive.astype(float) + falseNegative.astype(float))),0)
        
    recall_spa = np.sum(truePositive.astype(float),0) / (np.sum(truePositive.astype(float),0) +
                                                          np.sum(falseNegative.astype(float),0))
        
    #return recall_seq, recall_spa
    return np.nan_to_num(recall_seq), np.nan_to_num(recall_spa)
    
def precision(pred, label):
    """
    True positive / Total predicted positive
    Input fields must contain only 0 / 1. 1 is positive.
    """
    #print("Input size must be [seq, lat, lon]")
    seq, lat, lon = pred.shape
    # initialize dummy matrix
    pred_dummy_1 = np.zeros(pred.shape,dtype=int)
    label_dummy_1 = np.zeros(label.shape,dtype=int)
    # True positive
    # create dummy matrix to save the labels
    pred_dummy_1[:] = pred[:]
    label_dummy_1[:] = label[:]
    # change the label of negative events
    pred_dummy_1[pred == 0] = 2
    label_dummy_1[label == 0] = 3
    # count True Positive events
    truePositive = (pred_dummy_1 == label_dummy_1)

    # initialize dummy matrix
    pred_dummy_2 = np.zeros(pred.shape,dtype=int)
    label_dummy_2 = np.zeros(label.shape,dtype=int)
    # False positive (is 0 but predict 1)
    # create dummy matrix to save the labels (reset dummy)
    pred_dummy_2[:] = pred[:]
    label_dummy_2[:] = label[:]
    pred_dummy_2[pred == 1] = 2
    label_dummy_2[label == 0] = 2
    # count False Positive events
    falsePositive = (pred_dummy_2 == label_dummy_2)
  
    prec_seq = np.sum(np.sum(truePositive.astype(float),2),1) / (np.sum(np.sum(truePositive.astype(float),2),1) +
                                                                 np.sum(np.sum(falsePositive.astype(float),2),1))
        
    prec_spa = np.sum(truePositive.astype(float),0) / (np.sum(truePositive.astype(float),0) +
                                                       np.sum(falsePositive.astype(float),0))
       
    return np.nan_to_num(prec_seq), np.nan_to_num(prec_spa)
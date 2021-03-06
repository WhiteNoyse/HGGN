#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 16 12:12:18 2018

@author: sulem
"""

import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm

import torch
import torch.nn as nn
from torch.autograd import Variable
from torch import optim
import torch.nn.functional as F

import logging
logging.basicConfig(level=logging.INFO)

if torch.cuda.is_available():
    dtype = torch.cuda.FloatTensor
    dtype_l = torch.cuda.LongTensor
    torch.cuda.manual_seed(0)
else:
    dtype = torch.FloatTensor
    dtype_l = torch.LongTensor
    torch.manual_seed(0)
    

class Logger(object):
    
    def __init__(self, log_dir):
        
        plots_dir = os.path.join(log_dir, 'plots/')
        
        if not os.path.isdir(log_dir):
            # if the directory does not exist we create the directory
            os.mkdir(log_dir)
            os.mkdir(plots_dir)
            logging.info('New directory created')
        else:                      
            # clean previous logged data under the same directory name
            self._remove(log_dir)
            os.mkdir(log_dir)
            os.mkdir(plots_dir)
            logging.info('Old directory cleaned')
        
        self.path = log_dir
        self.exp_file = os.path.join(log_dir, 'experiment.txt')
        self.res_file = os.path.join(log_dir, 'results.txt')
        self.plotsdir = plots_dir
        
        self.loss_train = []
        self.loss_test = []
        self.error_train = []
        self.error_test = []
        self.time_epoch = []
        self.test_time = []
        self.args = None
        self.models = []
      
        
    @staticmethod
    def _remove(path):
        
        if os.path.isfile(path):
            os.remove(path)  # remove the file
        
        elif os.path.isdir(path):
            import shutil
            shutil.rmtree(path) # remove dir and all contains
    
    
    def add_info(self, info):
        with open(self.exp_file, 'a') as file:
            file.write(info + '\n')
            
    def add_res(self, info):
        with open(self.res_file, 'a') as file:
            file.write(info + '\n')
            
    
    def write_settings(self, args):
        self.args = {}
        # write info
        with open(self.exp_file, 'a') as file:
            for arg in vars(args):
                file.write(str(arg) + ' : ' + str(getattr(args, arg)) + '\n')
                self.args[str(arg)] = getattr(args, arg)
                
    
    def save_model(self, model):
        save_dir = os.path.join(self.path, 'parameters/')
        # Create directory if necessary
        try:
            os.stat(save_dir)
        except:
            os.mkdir(save_dir)
        mpath = os.path.join(save_dir, 'gnn.pt')
        try :
            torch.save(model, mpath)
            logging.info('Model saved')
        except:
            logging.error("Issue saving model or model parameters")
            
        def add_avg_test_loss(self, loss):
            self.loss_test.append(loss)
            
            
    def load_model(self, dpath):
        path = os.path.join(dpath, 'parameters/gnn.pt')
        if os.path.exists(path):
            logging.info('GNN successfully loaded from {}'.format(path))
            return torch.load(path)
        else:
            raise ValueError('Parameter path {} does not exist.'.format(path))
                
    
    def add_train_loss(self, epoch, loss):
        self.loss_train.append(loss)
        with open(self.res_file, 'a') as file:
            file.write('Epoch {} : training loss = {:6f}'.format(epoch,loss) + '\n')


    def add_train_error(self, epoch, error):
        self.error_train.append(error)
        with open(self.res_file, 'a') as file:
            file.write('Epoch {} : training error = {:6f}'.format(epoch,error) + '\n')
                       
    
    def add_epoch_time(self, epoch, time):
        self.time_epoch.append(time)
        with open(self.res_file, 'a') as file:
            file.write('Epoch {} : training time = {}'.format(epoch,time) + '\n')
    
    def add_model(self, name_model):
        self.models.append(name_model)
    
    def add_test_loss(self, batch, loss):
        self.loss_test.append(loss)
        with open(self.res_file, 'a') as file:
            file.write('Batch {} : test loss = {:6f}'.format(batch,loss) + '\n')
  
      
    def add_test_error(self, batch, err):
        self.error_test.append(err)
        with open(self.res_file, 'a') as file:
            file.write('Batch {} : test error = {:6f}'.format(batch,err) + '\n')
    
    
    def add_test_time(self,batch, time):
        self.test_time.append(time)
        with open(self.res_file, 'a') as file:
            file.write('Batch {} : test time = '.format(batch,time) + '\n')    

    def write_test_perf(self):
        Ntest = len(self.error_test) // len(self.models)
        with open(self.res_file, 'a') as file:
            
            for i,m in enumerate(self.models):
                
                file.write('Performance of model ' + m + ' on the test set : ' + '\n')
                file.write('Average Loss : {} Average error ratio : {} Test time : {}'
                           .format(self.loss_test[(Ntest-1)*(i+1)],
                                   self.error_test[(Ntest-1)*(i+1)],
                                   self.test_time[i]) + '\n')
        
        
    def plot_train_logs(self):
        
        Nepochs = len(self.error_train) // len(self.models)
        iters = range(Nepochs)
        
        for i,m in enumerate(self.models):
            
            loss = self.loss_train[i*Nepochs:(i+1)*Nepochs]
            error = self.error_train[i*Nepochs:(i+1)*Nepochs]
            
            plt.figure(i, figsize=(20, 20))
            plt.clf()
            # plot loss
            plt.subplot(3, 1, 1)
            plt.semilogy(iters, loss, 'b')
            plt.xlabel('epochs')
            plt.ylabel('Cross Entropy Loss')
            plt.title('Model ' + m + ' : Average Training Loss over the epochs ')
            # plot error
            plt.subplot(3, 1, 2)
            plt.plot(iters, error, 'b')
            plt.xlabel('epochs')
            plt.ylabel('Error ratio')
            plt.title('Model ' + m + ' : Average Training error over the epochs')
           
            plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=2.0)
            
            image = 'model_' + str(i) + '_training.png'
            path = os.path.join(self.plotsdir, image) 
            plt.savefig(path)
        
    
    def plot_test_logs(self):
        
        Ntest = len(self.error_test) // len(self.models)
        
        for i in range (len(self.models)):
            
            loss = self.loss_test[i*Ntest:(i+1)*Ntest]
            error = self.error_test[i*Ntest:(i+1)*Ntest]
            
            iters = range(len(loss))
            
            plt.figure(i+2, figsize=(20, 20))
            plt.clf()
            # plot average loss over one epoch
            plt.subplot(3, 1, 1)
            plt.semilogy(iters, loss, 'b')
            plt.xlabel('iterations')
            plt.ylabel('Cross Entropy Loss')
            plt.title('Model {} : Average Test Loss over batchs of 30 instances'.format(self.models[i]))
            # plot accuracy
            plt.subplot(3, 1, 2)
            plt.plot(iters, error, 'b')
            plt.xlabel('iterations')
            plt.ylabel('Accuracy')
            plt.title('Model {} : Average Test error'.format(self.models[i]))
            
            plt.tight_layout(pad=0.8, w_pad=0.5, h_pad=2.0)
            
            image = 'model_' + self.models[i] + '_test.png'
            path = os.path.join(self.plotsdir, image) 
            plt.savefig(path)
                
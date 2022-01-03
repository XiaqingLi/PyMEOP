'''PyMEOP J.Maxwell 2021
'''

import datetime
import time
import socket
import sys
import os
import yaml
import pytz
import logging
from PyQt5.QtWidgets import QMainWindow, QErrorMessage, QTabWidget, QLabel, QWidget
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QValidator
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from logging.handlers import TimedRotatingFileHandler

from app.gui_run_tab import RunTab
from app.gui_find_tab import FindTab
from app.classes import Event
from app.instruments import ProbeLaser, WavelengthMeter, LabJack, LockIn


class MainWindow(QMainWindow):
    '''Main window of application

    Attributes:

    '''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.error_dialog = QErrorMessage(self)
        self.status_bar = self.statusBar()
        self.status_bar.showMessage('Ready.')

        self.config_filename = 'config.yaml'
        self.load_settings()


        self.left = 100
        self.top = 100
        self.title = 'JLab Polarization Display'
        self.width = 1200
        self.height = 800
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

        # Make tabs
        self.run_tab = RunTab(self)
        self.tab_widget.addTab(self.run_tab, "Run")
        self.find_tab = FindTab(self)
        self.tab_widget.addTab(self.find_tab, "Find Peaks")
		
        try:
            self.probe = ProbeLaser(self.settings)            
            self.status_bar.showMessage(f"Connected to probe laser at {self.settings['probe_ip']}")
        except:
            print(f"Unable to connect to probe laser at {self.settings['probe_ip']}")
            
        try: 
            self.meter = WavelengthMeter(self.settings)           
            self.status_bar.showMessage(f"Connected to wavelength meter at {self.settings['meter_ip']}")
        except Exception as e:
            print(f"Unable to connect to meter at {self.settings['meter_ip']}, {e}")
                 
        try: 
            self.lockin = LockIn(self.settings)
            self.status_bar.showMessage(f"Connected to lock-in at {self.settings['lockin_ip']}")
        except Exception as e:
            print(f"Unable to connect to Lock In at {self.settings['lockin_ip']}, {e}")
            
            
        # try: 
            # self.labjack = LabJack(self.settings)
        # except Exception as e:
            # print(f"Unable to connect to LabJack at {self.settings['labjack_ip']}, {e}")
        
    def load_settings(self):
        '''Load settings from YAML config file'''

        with open(self.config_filename) as f:                           # Load settings from YAML file
           self.config_dict = yaml.load(f, Loader=yaml.FullLoader)
        self.settings = self.config_dict['settings']                    # dict of settings

        self.status_bar.showMessage(f"Loaded settings from {self.config_filename}.")

    def divider(self):
        div = QLabel ('')
        div.setStyleSheet ("QLabel {background-color: #eeeeee; padding: 0; margin: 0; border-bottom: 0 solid #eeeeee; border-top: 1 solid #eeeeee;}")
        div.setMaximumHeight (2)
        return div


class Event():
    '''Data and method object for single event point. Takes config instance on init.
    '''
       
    def __init__(self, parent):
        self.parent = parent
        
        self.start_time =  datetime.datetime.now(tz=datetime.timezone.utc)        
        self.start_stamp = self.start_time.timestamp()


    def print_event(self, eventfile):
        '''Print out event to eventfile, formatting to dict to write to json line.
        
        Args:
            eventfile: File object to write event to
        '''
        
        exclude_list = [ 'parent' ]
        json_dict = {}        
        #json_dict.update(self.scan.__dict__)
        for key, entry in self.__dict__.items():               # filter event attributes for json dict
            if isinstance(entry, datetime.datetime):
                json_dict.update({key:entry.__str__()})  # datetime to string
            elif key in exclude_list: pass
            else:
                json_dict.update({key:entry})
        for key, entry in json_dict.items():   
            if isinstance(entry, np.ndarray):       
                json_dict[key] = entry.tolist()    
        json_record = json.dumps(json_dict)
        eventfile.write(json_record+'\n')               # write to file as json line
'''PyMEOP J.Maxwell 2021
'''
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from labjack import ljm
import telnetlib
import time

            
class ProbeLaser():      
    '''Access Probe laser over telnet
    '''
    
    
    def __init__(self, settings):
        '''Open connection to Toptica DLC controller
        '''  
        self.ip = settings['probe_ip']
        self.port = 1998
        
        try:
            self.tn = telnetlib.Telnet(self.ip, port=self.port, timeout=2)
            
            outp = self.tn.read_until(bytes(">", 'ascii'),2).decode('ascii')
            self.tn.write(bytes("(param-disp 'laser1:dl:cc:current-set)\n", 'ascii'))
            outp = self.tn.read_until(bytes(">", 'ascii'),2).decode('ascii')
            
         
            
        except Exception as e:
            print(f"Probe connection failed on {self.ip}: {e}")
            
    # def __del__(self):
        # self.tn.close()
        
    def read_current(self):
        '''
        '''
        self.tn.write(bytes(f"(param-disp 'laser1:dl:cc:current-set)\n", 'ascii'))
        outp = self.tn.read_until(bytes(">", 'ascii'),2).decode('ascii')
        return outp
        
    def set_current(self, current):
        '''Arguments:
                curent: float
        '''
        self.tn.write(bytes(f"(param-set! 'laser1:dl:cc:current-set {current})\n", 'ascii'))
        outp = self.tn.read_until(bytes(">", 'ascii'),2).decode('ascii')
        return outp
        
        
    def read_temp(self, temp):
        '''
        '''
        self.tn.write(bytes(f"(param-disp 'laser1:dl:tc:temp-set)\n", 'ascii'))
        outp = self.tn.read_until(bytes(">", 'ascii'),2).decode('ascii')
        return outp
        
    def set_temp(self, temp):
        '''Arguments:
                temp: float
        '''
        self.tn.write(bytes(f"(param-set! 'laser1:dl:tc:temp-set {temp})\n", 'ascii'))
        outp = self.tn.read_until(bytes(">", 'ascii'),2).decode('ascii')
        return outp

	        
class WavelengthMeter():
    '''Access Wavelength meter'''
    

    def __init__(self, settings):
        '''Start connection over telnet'''        
        self.ip = settings['meter_ip']
        self.port = 5025
 
        try:
            self.tn = telnetlib.Telnet(self.ip, port=self.port, timeout=4)
            self.tn.write(bytes(f"MEAS:POW:WAV?\n", 'ascii'))
            outp = self.tn.read_some().decode('ascii')   
                        
        except Exception as e:
            print(f"Meter connection failed on {self.ip}: {e}")
                
    def __del__(self):
        #self.tn.close()  
        pass
        
    def start_cont(self):
        '''Start continuous measurements'''
        self.tn.write(bytes(f"INIT:CONT 1\r", 'ascii'))
        
    def stop_cont(self):
        '''Stop continuous measurements'''
        self.tn.write(bytes(f"INIT:CONT 0\r", 'ascii')) 
    
    def read_wavelength(self, channel):
        '''Arguments:
                channel: 1 or 2 for pump or probe
            Returns wavelenth in nm    
                
        '''
        self.tn.write(bytes(f"FETC:POW:WAV?\r", 'ascii'))
        outp = self.tn.read_some().decode('ascii')
        return float(outp)*1e9      
	
        
class LockIn():
    '''Access lock-in meter'''
    

    def __init__(self, settings):
        '''Start connection over telnet'''        
        self.ip = settings['lockin_ip']
        self.port = 23
 
        try:
            self.tn = telnetlib.Telnet(self.ip, port=self.port, timeout=5)
            outp = self.tn.read_until(bytes("\r", 'ascii'),2).decode('ascii')
                        
        except Exception as e:
            print(f"Lock-in connection failed on {self.ip}: {e}")
                
    def __del__(self):
        #self.tn.close()  
        pass
        
    def read_all(self):
        '''Returns both all four lock-in parameters as x,y,r,theta
        '''
        self.tn.write(bytes(f"SNAPD?\r", 'ascii'))
        x, y, r, th = self.tn.read_until(bytes("\r", 'ascii'),2).decode('ascii').split(',')
        return x, y, r   
        
class SigGen():
    '''Access signal generator for discharge control'''
    

    def __init__(self, settings):
        '''Start connection over telnet'''        
        self.ip = settings['siggen_ip']
        self.port = 5025
 
        try:
            self.tn = telnetlib.Telnet(self.ip, port=self.port, timeout=2)
            outp = self.tn.read_until(bytes("\r", 'ascii'),2).decode('ascii')
                        
        except Exception as e:
            print(f"Signal generator connection failed on {self.ip}: {e}")
            
        self.init_settings()
            
    def init_settings(self):
        '''Set initial settings'''
        
        self.tn.write(bytes(f"ENBL 0\r", 'ascii'))            # BNC output off
        self.tn.write(bytes(f"AMPR 0.1 Vpp\r", 'ascii'))      # N output to 0.1 Vpp
        self.tn.write(bytes(f"FREQ 12 MHz\r", 'ascii'))       # Freq start at 12 MHz
        self.tn.write(bytes(f"ENBR 1\r", 'ascii'))            # N output on
        self.tn.write(bytes(f"TYPE 0\r", 'ascii'))            # AM modulation
        self.tn.write(bytes(f"ADEP 50.0\r", 'ascii'))         # Modulation to 50% depth
        self.tn.write(bytes(f"MFNC 0\r", 'ascii'))            # Modulation is sine wave
        self.tn.write(bytes(f"RATE 1 kHz\r", 'ascii'))        # Modulation to 1 kHz
        self.tn.write(bytes(f"MODL 1\r", 'ascii'))            # Modulation ON           
                
    def __del__(self):
        #self.tn.close()  
        pass
        
    def set_freq(self, freq):
        '''Set RF frequency in MHz'''
        self.tn.write(bytes(f"FREQ {freq} MHz\r", 'ascii'))
        
    def set_amp(self, amp):
        '''Set amplitude in volt peak to peak'''
        self.tn.write(bytes(f"AMPR {amp} Vpp\r", 'ascii'))
        
class LabJack():      
    '''Access LabJack device 
    '''
    
    def __init__(self, settings):
        '''Open connection to LabJack
        '''  
        ip = settings['labjack_ip']
        try:
            self.lj = ljm.openS("T4", "TCP", ip) 
        except Exception as e:
            print(f"Connection to LabJack failed on {ip}: {e}")

        
    
    def read_back(self):
        '''Read voltage in
        '''
        aNames = ["AIN0","AIN1"]
        return ljm.eReadNames(self.lj, len(aNames), aNames)
        
    # def __del__(self):
        # '''Close on delete'''
        # ljm.close(self.lj) 
            
# -*- coding: utf-8 -*-
"""Script that records multichannel audio from a given audio device. 
The device is triggered and stopped at the user-given times,
and a WAV file is saved at the required folder destination. 

This script was originally written to run Dr. Sue Anne Zollinger's
8-channel recording system. 

Created on Thu Sep 27 14:48:19 2018

@author: Thejasvi Beleyur
@email : tbeleyur@orn.mpg.de, thejasvib@gmail.com
"""

import sounddevice as sd 
import Queue 
import matplotlib.pyplot as plt 
plt.rcParams['agg.path.chunksize'] = 10000


def scheduled_multichannel_recorder():
    ''' This function inititates recording at a user-given time
    from the audio device  and continues the recording until the 
    required end time. 
    
    Each file is saved with the timestamp the file was
    saved at in the end of the filename.
    
    Parameters:
        
        start_end_time : tuple with 2 string entries. The script
            
        
        device_name : string. The name of the device as shown when
                      sounddevice.query_devices() is called. 
                      Be aware that the same soundcard may appear
                      in different configurations (stereo in, stereo out, 
                      different stereo channel combinations,etc.) and 
                      choose the configuration you need. Defaults to 
                      'M-Audio M-Track Eight ASIO' as this is the 
                      device Sue Anne's using ! 
        
        num_channels : int. Number of channels to record from. 
                       The number of channels is always counted from the 1st 
                       one. Eg. if there's an 8-channel system, and you want 
                       to record from only 5, then channels 1,2,3,4,5 will 
                       be used. An arbitrary set of channels eg. 1,3,4,5,6
                       cannot be set in this version of the function. 
        
        samplerate : int. The samplingrate in Hertz. 
        
        destination_folder : string. The location where the file is to be 
                              saved.
                              
        Keyword Arguments : 
            
        file_prefix : string. To alter the name of the file based on the 
                      experiment underway. Eg. if file_prefix is set to
                      'Expt1', then all the files will be called 
                      'Expt1_2018-09-29_20-02-23.wav'
    
    Returns:

        multichannel wav file        
    '''


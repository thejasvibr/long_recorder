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
import datetime as dt
import numpy as np
import sounddevice as sd 
import soundfile as sf
import time 
import queue 
import matplotlib.pyplot as plt 
plt.rcParams['agg.path.chunksize'] = 10000


def scheduled_multichannel_recorder(end_time_HHMM,
                                    destination_folder,
                                    device_name= 'M-Audio M-Track Eight ASIO (64)',
                                    num_channels=8,
                                    fs=44100,                                    
                                    **kwargs):
    ''' This function inititates recording at a user-given time
    from the audio device  and continues the recording until the 
    required end time. 
    
    Each file is saved with the timestamp the file was
    saved at in the end of the filename.

    
    Parameters:
        
        end_time_HHMM : string. The timestamp must
                         be in HH:MM 24 hour format. eg. 13:15
        
        destination_folder : string. The location where the file is to be 
                              saved.


        device_name : string. The name of the device as shown when
                      sounddevice.query_devices() is called. 
                      Be aware that the same soundcard may appear
                      in different configurations (stereo in, stereo out, 
                      different stereo channel combinations,etc.) and 
                      choose the configuration you need. Defaults to 
                      'M-Audio M-Track Eight ASIO (64)' as this is the 
                      device Sue Anne's using ! 
        
        num_channels : int. Number of channels to record from. 
                       The number of channels is always counted from the 1st 
                       one. Eg. if there's an 8-channel system, and you want 
                       to record from only 5, then channels 1,2,3,4,5 will 
                       be used. An arbitrary set of channels eg. 1,3,4,5,6
                       cannot be set in this version of the function. 
                       Defaults to 8
        
        samplerate : int. The samplingrate in Hertz. Defaults to 44100, 
                     If any other sampling rate is being used, please check 
                     that it is changed also in the software driver of the 
                     soundcard.
        
        
                              
        Keyword Arguments : 
            
        file_prefix : string. To alter the name of the file based on the 
                      experiment underway. Eg. if file_prefix is set to
                      'Expt1', then all the files will be called 
                      'Expt1_2018-09-29_20-02-23.wav'
        

    Returns:

        multichannel wav file        
    '''

    assert (num_channels >=1), 'The number of recording channels must be >=1'

    YDM_today = get_YDM_fortoday()
    
    end_time_string = YDM_today + '_' + end_time_HHMM
    
    end_time = convert_YDMHHmm_to_posix(end_time_string)

    if 'file_prefix' not in kwargs.keys():
        
        file_prefix = 'Recording_'
    else:
        file_prefix = kwargs['file_prefix']

    dev_num = get_device_indexnumber(device_name)

    start_timestamp = make_timestamp()
    file_name = destination_folder+ file_prefix+'_' +start_timestamp+'.wav'

    with sf.SoundFile(file_name, mode='w', samplerate=fs,
                      channels=num_channels) as f:
    
        with sd.InputStream(samplerate=fs, device=dev_num,
    							channels=num_channels, callback=callback_function):
           while time.time() < end_time:    
                f.write(q.get())

q = queue.Queue()      

def callback_function(indata, frames, time, status):
    	"""This is called (from a separate thread) for each audio block."""
    	if status:
    		print(status)
    	q.put(indata.copy())


def get_device_indexnumber(device_name):
    '''
    Check for the device name in all of the recognised devices and
    return the index number within the list.

    this function is taken from the fieldrecorder recording class.

    '''
    device_list = sd.query_devices()

    tgt_dev_name = device_name
    tgt_dev_bool = [tgt_dev_name in each_device['name'] for each_device in device_list]

    if not True in tgt_dev_bool:

        print (sd.query_devices())

        raise ValueError('The input device \n' + tgt_dev_name+
        '\n could not be found, please look at the list above'+
                         ' for all the recognised devices'+
                         ' \n Please use sd.query_devices to check the  recognised'
                         +' devices on this computer')

    if sum(tgt_dev_bool) > 1 :
       raise ValueError('Multiple devices with the same string found'
       + ' please enter a more specific device name'
       ' \n Please use sd.query_devices to check the recognised'+
       ' devices on this computer')

    else:
        tgt_ind = int(np.argmax(np.array(tgt_dev_bool)))
    
    
    return(tgt_ind)


def get_YDM_fortoday():
    '''get year date and month for today and output it as
    YYYY-MM-DD string.
    '''
    timenow = dt.datetime.now()
    year, month, day = timenow.year, timenow.month, timenow.day
    YDM_timestamp = str(year)+'-'+str(month)+'-'+str(day)
    return(YDM_timestamp)    

def convert_YDMHHmm_to_posix(timestamp):
    '''
    thanks to Laurent Laporte ! 
    https://tinyurl.com/yd7bdrbp

    '''
    # convert the string timestamp into a time object
    target_time = dt.datetime.strptime(timestamp, '%Y-%m-%d_%H:%M')
    posix_targettime = time.mktime(target_time.timetuple())
    return(posix_targettime)

def make_timestamp():
    '''Makes a YYYY-mm-dd_HH-MM-SS timestampe of when the file was initiated'''
    now = dt.datetime.now()
    timestamp = dt.datetime.strftime(now, '%Y-%m-%d_%H-%M-%S')
    return(timestamp)
        
if __name__ == '__main__':
    
    # define the start and stop times of the recording to be run
    timenow = dt.datetime.now()
    hour, minute = timenow.hour, timenow.minute

    stop_time = str(timenow.hour)+':'+str(timenow.minute+2)

    folder_location = 'C://Users//tbeleyur//Documents//figuring_out//sueanne//'
    dev_name = 'Microsoft Sound Mapper - Input'
    scheduled_multichannel_recorder(stop_time, 
                                    destination_folder = folder_location,
									device_name = dev_name,
                                    num_channels=2,
                                    )   
    
    




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
import soundfile 
import time 
import Queue 
import matplotlib.pyplot as plt 
plt.rcParams['agg.path.chunksize'] = 10000


def scheduled_multichannel_recorder(start_end_time,
                                    destination_folder,
                                    device_name= 'M-Audio M-Track Eight ASIO (64)',
                                    num_channels=8,
                                    samplerate=44100,                                    
                                    **kwargs):
    ''' This function inititates recording at a user-given time
    from the audio device  and continues the recording until the 
    required end time. 
    
    Each file is saved with the timestamp the file was
    saved at in the end of the filename.

    
    Parameters:
        
        start_end_time : tuple with 2 string entries. The timestamp must
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
        
        block_size : int. Number of samples to be read in every call 
                     to the sounddevic Stream. Defaults to 4096.   
    
    Returns:

        multichannel wav file        
    '''
    input_start_time, input_end_time = start_end_time

    YDM_today = get_YDM_fortoday()
    start_time_string = YDM_today +'_' + input_start_time
    end_time_string = YDM_today + '_' + input_end_time
    
    start_time = convert_YDMHHmm_to_posix(start_time_string)
    end_time = convert_YDMHHmm_to_posix(end_time_string)
   
    

    assert (end_time > start_time), 'End of recording time is earlier \
    than start time!!'

    assert (num_channels >=1), 'The number of recording channels must be >=1'

    #assert(start_time >= time.time()), 'The start time has already passed !!'
    
    if 'block_size' not in kwargs.keys():
        block_size = 4096
    else:
        block_size = kwargs['block_size']

    device_indnum = get_device_indexnumber(device_name)
    print(device_name, device_indnum)

    S = sd.Stream(samplerate=samplerate, blocksize=block_size,
                  device=device_indnum, channels=num_channels)

    q = Queue.Queue()
    print(time.time(), start_time)

    while time.time() < start_time:
        # do nothing in particular and wait for 1 second
        time.sleep(1)

    if time.time() >= start_time:
        print('Recording has begun.....')

        S.start()
        i = 0 
        while time.time() <= end_time:
            
            in_data, overflowed = S.read(block_size)
            
            if not overflowed  & i > 0 :
                q.put(in_data)

    
    all_buffers = empty_qcontentsintolist(q)
    save_qcontents_aswav(all_buffers, destination_folder, samplerate,
                        num_channels)
        
        
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


def empty_qcontentsintolist(q):
    '''
    this function is taken from the fieldrecorder recording class.

    '''
    try:
        q_contents = [ q.get() for i in range(q.qsize()) ]

    except:
        raise IOError('Unable to empty queue object contents')

    return(q_contents)

def save_qcontents_aswav(q_contents, destination_folder, fs, num_channels):
    '''
    this function is taken from the fieldrecorder recording class.

    '''

    print('Saving file now...')

    rec = np.concatenate(q_contents)
    save_channels = range(num_channels)
    print(rec.shape)
    rec2besaved = rec[:,save_channels]

    timenow = dt.datetime.now()
    timestamp = timenow.strftime('%Y-%m-%d_%H-%M-%S')
    idnumber =  int(time.mktime(timenow.timetuple())) #the unix time which provides a 10 digit unique identifier

    main_filename = 'MULTIWAV_' + timestamp+'_'+str(idnumber) +'.WAV'

    try:
        print('trying to save file... ')

        soundfile.write(destination_folder+main_filename,rec2besaved,fs)

        print('File saved')

        pass

    except:
        raise IOError('Could not save file !!')

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

        
if __name__ == '__main__':
    
    # define the start and stop times of the recording to be run
    timenow = dt.datetime.now()
    hour, minute = timenow.hour, timenow.minute
    
    start_time = str(timenow.hour)+':'+str(timenow.minute+1)
    end_time = str(timenow.hour)+':'+str(timenow.minute+20)
    
    start_stop_time = (start_time,end_time)

    folder_location = 'C://Users//tbeleyur//Documents//figuring_out//sueanne//'

    scheduled_multichannel_recorder(start_stop_time, 
                                    destination_folder = folder_location,
									num_channels=3
                                    )   
    
    




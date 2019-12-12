# -*- coding: utf-8 -*-
"""
Module name: dso200

Copyright:
----------------------------------------------------------------------
dso200 is Copyright (c) 2014 Good Will Instrument Co., Ltd All Rights Reserved.

This program is free software; you can redistribute it and/or modify it under the terms 
of the GNU Lesser General Public License as published by the Free Software Foundation; 
either version 2.1 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
See the GNU Lesser General Public License for more details.

You can receive a copy of the GNU Lesser General Public License from 
http://www.gnu.org/

Note:
dso200 uses third party software which is copyrighted by its respective copyright holder. 
For details see the copyright notice of the individual package.

----------------------------------------------------------------------
Description:
dso200 is a python driver module used to get waveform and image from DSO.

Module imported:
  1. PySerial 2.7
  2. Numpy 1.8.0
  3. PIL 1.1.7

Version: 1.03

Modified on DEC 11 2018

Author: Kevin Meng
"""
from gw_com import com
from PIL import Image
from struct import unpack
import numpy as np
import array
import struct
import os, sys, time

__version__ = "1.03" #dso200 module's version.

def generate_lut():
    global lu_table
    num=65536
    lu_table=[]
    for i in xrange(num):
        pixel888=[0]*3
        pixel888[0]=(i>>8)&0xf8
        pixel888[1]=(i>>3)&0xfc
        pixel888[2]=(i<<3)&0xf8
        lu_table.append(pixel888)

class Dso200:
    def __init__(self, interface):
        if(os.name=='posix'): #unix
            if(os.uname()[1]=='raspberrypi'):
                self.osname='pi'
            else:
                self.osname='unix'
        else:
            self.osname='win'
        if(interface != ''):
            self.connect(interface)
            self.connection_status=1
        else:
            self.connection_status=0
        global inBuffer
        self.ver=__version__ #Driver version.
        self.iWave=[[], []]
        self.vdiv=[[], []]
        self.vunit=[[], []]
        self.dt=[[], []]
        self.vpos=[[], []]
        self.hpos=[[], []]
        self.ch_list=[]
        self.info=[[], []]
        generate_lut()
        
    def connect(self, str):
        if('/dev/ttyACM' in str) or ('COM' in str): #Check if str is COM port.
            try:
                self.IO=com(str)
            except:
                print 'Open COM port failed!'
                return
            self.IO.clearBuf()
        else:
            return
        self.write=self.IO.write
        self.read=self.IO.read
        self.readBytes=self.IO.readBytes
        self.closeIO=self.IO.closeIO
        self.write('*IDN?\n')
        model_name=self.read().split(',')[1]
        print '%s connected to %s successfully!'%(model_name, str)
        if(model_name != ''):
            self.connection_status=1
        else:
            self.connection_status=0
            print 'Device not found!'
            return
        
        if not os.path.exists('port.config'):
            f = open('port.config', 'wb')
            f.write(str)
            f.close()

    def getBlockData(self): #Used to get image data.
        global inBuffer
        inBuffer=self.readBytes(10)
        length=len(inBuffer)
        self.headerlen = 2 + int(inBuffer[1])
        pkg_length = int(inBuffer[2:self.headerlen]) + self.headerlen + 1 #Block #48000[..8000bytes raw data...]<LF>
        print "Data transferring...  "

        pkg_length=pkg_length-length
        while True:
            print('%8d\r' %pkg_length),
            if(pkg_length==0):
                break
            else:
                if(pkg_length > 100000):
                    length=100000
                else:
                    length=pkg_length
                try:
                    buf=self.readBytes(length)
                except:
                    print 'KeyboardInterrupt!'
                    self.closeIO()
                    sys.exit(0)
                num=len(buf)
                inBuffer+=buf
                pkg_length=pkg_length-num

    def ImageDecode(self):
        raw_data=[]
        #Convert 8 bits array to 16 bits array.
        data = unpack('<%sH' % (len(inBuffer[self.headerlen:-1])/2), inBuffer[self.headerlen:-1])
        l=len(data)
        if( l%2 != 0):   #Ignore reserved data.
            l=l-1
        package_length=len(data)
        index=0
        bmp_size=0
        while True:
            length =data[index]
            value =data[index+1]
            index+=2
            bmp_size+=length
            buf=[ value for x in xrange(0,length)]
            raw_data+=buf
            if(index>=l):
                break

        #Get Orientation info.(800x480 or 480x800)
        self.write(':ROTATE?\n')
        state = self.read()           #Get rotate info. 0:Portrait, 1:Landscape
        if(state[0] == '1'):
            width = 800
            height = 480
        else:
            width = 480
            height = 800
        #Convert from rgb565 into rgb888
        index=0
        rgb_buf=[]
        num=width*height
        for index in xrange(num):
            rgb_buf+=lu_table[raw_data[index]]
        img_buf=struct.pack("1152000B", *rgb_buf)
        self.im=Image.frombuffer('RGB',(width,height), img_buf, 'raw', 'RGB',0,1)
        if(self.osname=='pi'):
            self.im=self.im.transpose(Image.FLIP_TOP_BOTTOM) #For raspberry pi only.

    def getRawData(self, header_on,  ch): #Used to get waveform's raw data.
        global inBuffer
        self.dataMode=[]
        print('Waiting CH%d data... ' % ch)
        if(header_on==True):
            self.write(":HEAD ON\n")
        else:
            self.write(":HEAD OFF\n")

        if(self.checkAcqState(ch)== -1):
            return
        self.write(":ACQ%d:MEM?\n" % ch)                    #Write command(get raw datas) to DSO.

        index=len(self.ch_list)
        if(header_on == True):
            if(index==0): #Getting first waveform => reset self.info.
                self.info=[[], []]
                
            self.info[index]=self.read().split(';')
            num=len(self.info[index])
            self.info[index][num-1]=self.info[index][num-2] #Convert info[] to csv compatible format.
            self.info[index][num-2]='Mode,Fast'
            sCh = [s for s in self.info[index] if "Source" in s]
            self.ch_list.append(sCh[0].split(',')[1])
            sDt = [s for s in self.info[index] if "Sampling Period" in s]
            self.dt[index]=float(sDt[0].split(',')[1])
            sDv = [s for s in self.info[index] if "Vertical Scale" in s]
            self.vdiv[index]=float(sDv[0].split(',')[1])
            sVpos=[s for s in self.info[index] if "Vertical Position" in s]
            self.vpos[index]=float(sVpos[0].split(',')[1])
            sHpos = [s for s in self.info[index] if "Horizontal Position" in s]
            self.hpos[index]=float(sHpos[0].split(',')[1])
            sVunit=[s for s in self.info[index] if "Vertical Units" in s]
            self.vunit[index]=sVunit[0].split(',')[1]
            #print sHpos, self.vdiv[index],  self.dt[index],  self.hpos[index], sDv
        self.getBlockData()
        self.points_num=len(inBuffer[self.headerlen:-1])/2   #Calculate sample points length.
        self.iWave[index] = unpack('>%sh' % (len(inBuffer[self.headerlen:-1])/2), inBuffer[self.headerlen:-1])
        del inBuffer
        return index #Return the buffer index.

    def checkAcqState(self,  ch):
        str_stat=":ACQ%d:STAT?\n" % ch
        loop_cnt = 0
        max_cnt=0
        while True:                                #Checking acquisition is ready or not.
            self.write(str_stat)
            state=self.read()
            if(state[0] == '1'):
                break
            time.sleep(0.1)
            loop_cnt +=1
            if(loop_cnt >= 50):
                print('Please check signal!')
                loop_cnt=0
                max_cnt+=1
                if(max_cnt==5):
                    return -1
        return 0

    def convertWaveform(self, ch, factor):
        dv=self.vdiv[ch]/25
        if(factor==1):
            num=self.points_num
            fWave=[0]*num
            for x in xrange(num):           #Convert 16 bits signed to floating point number.
                fWave[x]=float(self.iWave[ch][x])*dv
        else: #Reduced to helf points.
            num=self.points_num/factor
            fWave=[0]*num
            for x in xrange(num):           #Convert 16 bits signed to floating point number.
                i=factor*x
                fWave[x]=float(self.iWave[ch][i])*dv
        return fWave

    def readRawDataFile(self,  fileName):
        #Check file format(csv or lsf)
        self.info=[[], []]
        if(fileName.lower().endswith('.csv')):
            self.dataType='csv'
        elif(fileName.lower().endswith('.lsf')):
            self.dataType='lsf'
        else:
            return -1
        f = open(fileName, 'rb')
        info=[]
        #Read file header.
        if(self.dataType=='csv'):
            for x in xrange(26):
                info.append(f.readline().split(',\n')[0])
            if(info[0].split(',')[1]!='0.20'): #Check format version
                f.close()
                print('Format error!')
                return -1
            count=info[5].count('CH')  #Check channel number in file.
            wave=f.read().splitlines() #Read raw data from file.
            self.points_num=len(wave)
        else:
            info=f.readline().split(';') #The last item will be '\n'.
            #print len(info),  info
            if(info[0].split('Format,')[1]!='0.20'): #Check format version
                f.close()
                print('Format error!')
                return -1
            if(f.read(1)!='#'):
                print('Format error!')
                sys.exit(0)
            digit=int(f.read(1))
            num=int(f.read(digit))
            count=1
            wave=f.read() #Read raw data from file.
            self.points_num=len(wave)/2   #Calculate sample points length.
        f.close()

        if(count==1): #1 channel
            ch=0
            self.iWave[ch]=[0]*self.points_num
            sCh=[s for s in info if "Source" in s]
            self.ch_list.append(sCh[0].split(',')[1])
            sVunit = [s for s in info if "Vertical Units" in s]
            self.vunit[ch] =sVunit[0].split(',')[1]      #Get vertical units.
            sDv = [s for s in info if "Vertical Scale" in s]
            self.vdiv[ch] = float(sDv[0].split(',')[1])  #Get vertical scale. => Voltage for ADC's single step.
            sVpos=[s for s in info if "Vertical Position" in s]
            self.vpos[ch] =float(sVpos[0].split(',')[1]) #Get vertical position.
            sHpos = [s for s in info if "Horizontal Position" in s]
            self.hpos[ch] =float(sHpos[0].split(',')[1]) #Get horizontal position.
            sDt = [s for s in info if "Sampling Period" in s]
            self.dt[ch]=float(sDt[0].split(',')[1])      #Get sample period.
            dv1=self.vdiv[ch]/25
            vpos=int(self.vpos[ch]/dv1)+128
            vpos1=self.vpos[ch]
            num=self.points_num
            if(self.dataType=='csv'):
                for x in xrange(26):
                    self.info[ch].append(info[x])
                for x in xrange(num):
                    value=int(wave[x].split(',')[0])
                    self.iWave[ch][x]=value
            else: #lsf file
                for x in xrange(24):
                    self.info[ch].append(info[x])
                self.info[ch].append('Mode,Fast') #Convert info[] to csv compatible format.
                self.info[ch].append('Waveform Data')
                self.iWave[ch] = np.array(unpack('<%sh' % (len(wave)/2), wave))
                for x in xrange(num):            #Convert 16 bits signed number to floating point number.
                    self.iWave[ch][x]-=vpos
            del wave
            return 1
        elif(count==2): #2 channel, csv file only.
            #write waveform's info to self.info[]
            for ch in xrange(count):
                self.info[ch].append(info[0])
            for x in xrange(1, 26):
                str=info[x].split(',')
                for ch in xrange(count):
                    self.info[ch].append('%s,%s'%(str[2*ch],  str[2*ch+1]))
            for ch in xrange(count):
                self.iWave[ch]=[0]*self.points_num
                sCh=[s for s in info if "Source" in s]
                self.ch_list.append(sCh[0].split(',')[2*ch+1])
                sVunit = [s for s in info if "Vertical Units" in s]
                self.vunit[ch] =sVunit[0].split(',')[2*ch+1]      #Get vertical units.
                sDv = [s for s in info if "Vertical Scale" in s]
                self.vdiv[ch] = float(sDv[0].split(',')[2*ch+1])  #Get vertical scale. => Voltage for ADC's single step.
                sVpos=[s for s in info if "Vertical Position" in s]
                self.vpos[ch] =float(sVpos[0].split(',')[2*ch+1]) #Get vertical position.
                sHpos = [s for s in info if "Horizontal Position" in s]
                self.hpos[ch] =float(sHpos[0].split(',')[2*ch+1]) #Get horizontal position.
                sDt = [s for s in info if "Sampling Period" in s]
                self.dt[ch]=float(sDt[0].split(',')[2*ch+1])      #Get sample period.

            num=self.points_num
            for ch in xrange(count):
                self.iWave[ch]=[0]*num
            for i in xrange(num):
                str=wave[i].split(',')
                for ch in xrange(count):
                    index=2*ch
                    self.iWave[ch][i]=int(str[index])
        else:
            return -1

        del wave
        return count

    def isChannelOn(self, ch):
        self.write(":CHAN%d:DISP?\n" % ch)
        onoff=self.read()
        onoff=onoff[:-1]
        if(onoff=='ON'):
            return True
        else:
            return False

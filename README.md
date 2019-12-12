![Python logo](/image/python-logo.png)

This is a Python program.




OpenWave-200
============
![GetImage](/image/OpenWave256x256.jpg)

This icon is copyright 2014 (c) Good Will Instrument Co., Ltd all rights reserved.




OpenWave-200 is an open-source project. It's a simple python program that can get image or raw data from digital storage oscilloscope(GDS-200/300, IDS-200/300) via USB port.  

Users can execute the same source code on Windows, Linux(Ubuntu) and Raspbian(on Raspberry Pi 2) operating system without changing a word. By using this version, users can also create multiple DSO connections at the same time, and continuous waveform updating is selectable now.


Equipment
------------
You have to get a new digital storage oscilloscope - GDS-200/300(GOOD WILL INSTRUMENT), IDS-200/300(RS Pro) and a PC or NB with MS Windows or Ubuntu Linux OS.




Environment
------------
Currently OpenWave-200 may be executed on Windows XP/7/8/10 32 or 64 bits OS. You have to download and install the USB driver(dso_vpo V1.08) from [www.gwinstek.com](http://www.gwinstek.com) or [here](/dso_vpo_v108.zip) when the first connection with GDS-200/300. 

Please unzip the [OpenWave-200 V1.03.zip](/OpenWave-200_V1.03.zip) and find the OpenWave-200.exe in the folder. OpenWave-200.exe can be executed directly without installation. Please be noticed that the path name and folder name can't be double-byte characters.

The OpenWave-200 source code can also be executed on Ubuntu 32 bits Linux OS or Raspbian OS(on Raspberry Pi 2). The USB driver is not required in this environment.


Command Line Execution
------------
- **Windows Example:**

1.  Connected via USB(please find the port number in the Device Manager)
    ```
    D:\OpenWave-200 V1.03>OpenWave-200 COM5
    ```

2.  Automatically reading config file or scanning port
    ```
    D:\OpenWave-200 V1.03>OpenWave-200
    ```


- **Linux(or Raspbian) Example:**

1.  Connected via USB(please find the device under /dev)
    ```
    user@Ubuntu:~/workspace_python/OpenWave-200 V1.03$ sudo python OpenWave-200.py ttyACM1
    ```
    
2.  Automatically reading config file or scanning port
    ```
    user@Ubuntu:~/workspace_python/OpenWave-200 V1.03$ sudo python OpenWave-200.py
    ```
    
***Tips:***

1.  *If you are using Linux, please add your username to group ```dialout``` to get proper privilege level for device accessing.*
    ```
    user@Ubuntu:~/workspace_python/OpenWave-200 V1.03$ $ sudo adduser xxxx dialout     #xxxx is your username
    ```

2.  *You can also create a `port.config` file containing `COM5` or `ttyACM1`(as an example) in the folder for next time quick connection.*

3.  *If you are using Raspbian on a Raspberry Pi2. Please use root account, that will help you to avoid privilege issues.  You might get trouble if you find your DSO is connected as ttyACM0. Your will have to change some system configuration files manually.*



Development Tools
------------
- **Packages:**
   If you want to modify the source code and run the program by yourself. You have to install the development tools and packages as follows:
   * Python 2.7.9
   * PySerial 2.7
   * Matplotlib 1.3.1
   * Numpy 1.8.0
   * PIL 1.1.7
   * PySide 1.2.1
   * dateutil 2.2
   * pyparsing 2.0.1
   * six 1.4.1

 *OpenWave-200 is developed under Windows 32 bits environment, and all the packages are Windows 32bits version.*
 
- **Ubuntu Linux:**
   OpenWave-200 is also tested under Ubuntu 10.04 (32 bits) with the same version of the packages listed above.  And the following package and libraries are required:
   * nose-1.3.4
   * qt4-qmake
   * libqt4-dev

- **Raspbian Linux:**
   OpenWave-200 is also tested on Raspberry Pi 2 with the following package and libraries:
   * python-matplotlib
   * python-numpy
   * python-scipy
   * libatlas-base-dev
   * gfortran
   * python-pip
   * scipy
   * Pillow
   * python-pyside
   * python-serial
   * pyserial


- **Python IDE:**
   If you need a Python IDE tool, Eric4 4.5.19  is recommended:


- **Executable File:**
   If you want to convert python program into stand-alone executables under Windows. The following packages are required:
   * PyInstaller 2.1
   * pywin32 218.4 .



   
Screenshot
------------
**Get image:**
![GetImage](/image/pic1.png)


**Get raw data:**
![GetRawData](/image/pic2.png)


**Screenshot -- Win 7:**
![MS Windows](/image/Win7_Screenshot.jpg)


**Screenshot -- Ubuntu Linux:**
![Ubuntu Linux](/image/Ubuntu1004_Screenshot.jpg)


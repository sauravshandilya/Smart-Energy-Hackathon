''' 
This code helps in controlling the ACs based upon the user preference.
If the user selects POWERSAVER mode, only 2 ACs are allowed to be switched on.
If the user selects USERDEFINED mode, the no of ACs to be switched 
on are determined upon the intervel to which the minimum temperature selected 
selected belongs. The interval is defined using machine learned data
The machine learned data is sorted from higher temperature intervals to lower
The mintemp if falls in a particular interval checks for the no of ACs that 
has to be switched on for that particular interval, 
assigns it to no of ACs to be used. Then lower temerature is assigned as mintemp.
Higher temerature is assigned as mintemp+3. 


Then the required no ACs are switched on. Temperature is checked every one minute until
mintemp is reached and then ACs are switched off. Then waits for temperature to rise 
to reach the desired mintemp+3 when another combination for that particular no of ACs are switched on again.
This process is continued

Here we have use code from http://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/software-install
 to fetch data from the AM2302 temperature sensors. Here ./Adafruit_DHT is renamed as ./hackTemp

'''
#TODO need to implement the option for getting data from the config.csv file and auto config the intervals
#also add the option for running MACHINELEARN to update the config.csv 


# Currently we have used option for max 4 ACs and used data from the set of combinations which  we tried 
# and observed to hardcode the intervals


import RPi.GPIO as GPIO
import time
import subprocess
import re

#setting up the pins for the ACs

onlist={"1":"6","2":"2","3":"4","4":"8"}  #acstart lookup
offlist={"1":"5","2":"1","3":"3","4":"7"}  #acstop lookup
oldTemperature=17.9        #setting a minimum value than AC's lowest set
temper=17.9
#GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)

#setting up the AC pin values
GPIO.setup(16,GPIO.OUT)                     
GPIO.setup(18,GPIO.OUT)
GPIO.setup(22,GPIO.OUT)
GPIO.setup(24,GPIO.OUT)

#following function fetches data from the temperature sensor
#and sets it to oldTemperature and temper
def checktemp():
    #the ./hackTemp is run with 2302 as model of sensor. 27 the pin to which sensor is connected.
    output =subprocess.check_output(["./hackTemp","2302",'27']);
    #regular expression extracts temperature data 
    matches = re.search("Temp =\s+([0-9.]+)", output)
    global oldTemperature
    global temper
    if (not matches):
	#sets oldTemperature data as current temperature data if no matches occur 
        temper=oldTemperature;
    else:
	#if match found the oldTemperature and current temperature are updated maintained
        temper=float(matches.group(1))
        oldTemperature=temper

checktemp()

#does checktemp() with one minute delay
def slowchecktemp():
    time.sleep(30)
    checktemp()
    time.sleep(30)

#following function contains the pins which are connect RPi to Arduinos for controlling ACs

def onoff(sel):
    if sel==1:                     # Fan Mode 
        GPIO.output(16,False)

    if sel==2:                     # Compressor Mode 
        GPIO.output(16,True)


    if sel==7:                    # Fan mode 
        GPIO.output(18,False)
    if sel==8:                     # Compressor Mode 
        GPIO.output(18,True)
    if sel==5:                     # Fan Mode 
        GPIO.output(22,False)
    if sel==6:                     # Compressor mode 
        GPIO.output(22,True)
    if sel==3:                     # Fan Mode 
        GPIO.output(24,False)
    if sel==4:                     # Compressor mode 
        GPIO.output(24,True)

#function for starting ACs
def acstart(aclist):
    for i in aclist:
        onoff(int(onlist[str(i)]))

#function for stopping ACs
def acstop(aclist):
    for i in aclist:
        onoff(int(offlist[str(i)]))

#stopping all the ACs before starting the code
acstop([1,2,3,4])

while True:
    #POWERSAVER MODE lets only two ACs to run
    #USERDEFINED MODE lets user select temperature, but no of ACs that will run is based upon the interval 
    #in which the minimum temperature falls. This interval is to be decided using the Machine Learning Data
    #currently the data used is based on the observations which we made 
    mode=raw_input("POWERSAVER or USERDEFINED : ") #TODO add MACHINELEARN option
    #TL stores lower temperature allowed
    #TU stores upper temperature allowed
    #N stored no of ACs to be switched on
    #TODO to set the TL automatically from the data from mintemp for two ACs from config.csv 
    #else can set best comfort temperature via some other technique using data and emperical algorithms
    if mode == "POWERSAVER":
        TL=28
        TU=30
        N=2
        break
    elif mode == "USERDEFINED":
											
        mintemp=float(raw_input("Input minimum temperature required (in Celcius):"))
	
	#TODO implement code for reading the config.csv to get the intervals and their combinations and no of ACs to be on	

        if (mintemp >= 28):
	    print "Two ACs will be switched on"
	    N=2
	    TL=mintemp
	    TU=mintemp+3.0
	    break
	elif (mintemp < 28) and (mintemp>24):
            print "Three ACs will be switched on"
            N=3
            TL=mintemp
            TU=mintemp+3.0
            break
        else:
            print "Four ACs will be switched on"
            N=4
            TL=mintemp
            TU=mintemp+3
            break
							#TODO implement MACHINELEARN if check and code call
    else:
        print "Invalid mode"

if N == 2:
    while True:
        if (temper > TL ):   #just checking whether TL < temper to prevent unwanted switch on
            
            acstart([1,3])
	#once the ACs are started, the temperature is checked in every one minute
	
        while (temper > TL):
            slowchecktemp()
	#once the temperature goes below TL, ACs are switched off        
	acstop([1,3])
	#keep checking for temperature crossing TU
        while (temper < TU):
            slowchecktemp()
	#ACs start once TU is crossed. Here the AC combination is changed. 
	#This process is repeated for every combination present for 2 ACs here
        acstart([2,4])
        while (temper > TL):
            slowchecktemp()
        acstop([2,4])        
        while (temper<TU):
            slowchecktemp()
elif N==3:
    while True:
        if (temper > TL):	#just checking whether TL < temper to prevent unwanted switch on
            acstart([1,2,3])
        while (temper > TL):
            slowchecktemp()
        acstop([1,2,3])
        while (temper < TU):
            slowchecktemp()
        acstart([2,3,4])
        while (temper > TL):
            slowchecktemp
        acstop([2,3,4])
        while (temper < TU):
            slowchecktemp()
        acstart([3,4,1])
        while (temper > TL):
            slowchecktemp()
        acstop([3,4,1])
        while (temper < TU):
            slowchecktemp()
        acstart([4,1,2])
        while (temper > TL):
            slowchecktemp()
        acstop([4,1,2])
        while (temper < TU ):
            slowchecktemp()
else:
    while True:
        if (temper > TL):	#just checking whether TL < temper to prevent unwanted switch on
            acstart([1,2,3,4])
        while (temper >TL):
            slowchecktemp()
        acstop([1,2,3,4])
        while (temper < TU):
            slowchecktemp()
        
GPIO.cleanup()

# Autonomous-Driving-Using-intelligent-robot-EV3
Implementation of simulated autonomous driving experiments using EV3


## Summary
<img src=https://user-images.githubusercontent.com/83410590/207788875-bfee59a5-9c5e-414b-9684-3c4520bbadfd.PNG width='440' height='250'/> <img src=https://user-images.githubusercontent.com/83410590/207792641-37cbe897-92c5-426b-9f6a-d40394698d3d.PNG width="440" height="250"/>


Artificial intelligence, which has become a social issue starting with AlphaGo, is being applied to various fields with excellent development potential today.
Among them, autonomous driving is a vehicle that is controlled by a computer rather than the existing engine technology, and is capable of driving to the destination by itself.
Autonomous driving is no longer the domain of complete vehicle manufacturers. Accordingly, we conducted a simulation experiment on autonomous driving technology using a robot called EV3 in a small city map.

## Purpose
![safety_survey](https://user-images.githubusercontent.com/83410590/207794528-b50feccb-99a8-4932-912a-d7fe2eaa703b.PNG)
In 2017, Many people do not fully trust the self-driving system because of the danger caused by 'program malfunction'.
Therefore, we designed an autonomous driving simulation experiment that mimics the autonomous driving process of 'cognition-judgment-control' without human intervention.
By examining and improving various problems encountered in the process of completing the simulation, it helps in-depth understanding of current autonomous driving technology.


## Agent & Environment
![agent_envrionment](https://user-images.githubusercontent.com/83410590/207796748-c11823d1-1c4a-4154-be2d-69cd1a7d0ffc.PNG)


## What We used

* H/W
  - EV3 : The role of self-driving cars
  - WebCam : Used to provide image data to Google Cloud Vision.
  - wifi dongle : Building a wireless environment 
  - Color Sensor : A sensor that distinguishes 8 different colors (can measure light intensity, reflected light, ambient light, etc.)
  - Ultra Sonic Sensor : A sensor that measures the distance to an object and can measure a distance of about 250 cm
  
  
  
* S/W
  - OpenCV : Use for webcam control
  - ev3dev : Adopted for control compatibility in the existing 'Robot.c'.
  - Rpyc Package : Used for development of linux and window os integrated environment
  - Google Cloud Vision : Using open source neural networks provided by Google for image recognition


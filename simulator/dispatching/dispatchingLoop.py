# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 12:44:32 2020

@author: bastien velitchkine
"""
import numpy as np
from dispatchingStrategy import dispatchingStrategy

def dispatchingLoop(timeStep, netLoad, batteryInitialStorage,
                    specifications, strategy):
    """
    INPUT:
        - timeStep : float, the time step used to compute the net load in hours
        - netLoadVector : numpy array, the net load at each time step
        - batteryInitialStorage : float, the amount of energy in the battery at the beginning in kWh
        - specifications : list of:
            - battMaxStorage : float, the storage capacity of the battery on kWh
            - genMaxPow : float, the maximum power the dg can deliver in kW
            - battMaxInputPow : float, the maximum input power of the battery in kW
            - battMaxOutputPow : float, the maximum output power of the battery in kW
            - SOC_min : the minimum storage of the battery in kWh
        - strategy : string, whether it's load following or cycle charging. Accepted values are "LF" and "CC".
    OUTPUT:
        list :
            - batteryStorageVector : numpy array, the energy stored in the battery at each timeStep
            - generatorPowerVector : numpy array, the functionning power of the dg at each timeStep
    """
    batteryStorageVector = [batteryInitialStorage]
    generatorPowerVector = []
    simulationRepetitions = len(netLoad)
    newStrat = "1" if strategy == "LF" else "2"
    for i in range(simulationRepetitions):
        temp = dispatchingStrategy([netLoad[i], timeStep],
                                   [batteryStorageVector[-1]], specifications,
                                   newStrat)
        generatorPowerVector.append(temp[0])
        batteryStorageVector.append(temp[1])
    return [np.array(batteryStorageVector)[1:], np.array(generatorPowerVector)]


# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 12:24:20 2020

@author: bastien velitchkine
"""
import time

#def batteryManagement(batteryInputPower, battMaxInputPow, battMaxOutputPow, battMaxStorage, batteryStorage, timeStep):
#    """
#    The function returns the amount of energy stored in the battery by the end of the time period given charge/discharge
#    """
#    # batteryInputPower Positive (inwards flow into battery)
#    if batteryInputPower <= battMaxInputPow and batteryInputPower >= 0:
#        chargingPower = batteryInputPower
#        if (battMaxStorage - batteryStorage) >= chargingPower * timeStep:
#            newBattStorage = batteryStorage + chargingPower * timeStep
#        else:
#            newBattStorage = battMaxStorage
#
#    # batteryInputPower Positive (inwards flow into battery)
#    if batteryInputPower > battMaxInputPow and batteryInputPower >= 0:
#        chargingPower = battMaxInputPow
#        if (battMaxStorage - batteryStorage) >= chargingPower * timeStep:
#            newBattStorage = batteryStorage + chargingPower * timeStep
#        else:
#            newBattStorage = battMaxStorage
#
#    # batteryInputPower Positive (outwards flow into battery)
#    if batteryInputPower < 0 and abs(batteryInputPower) <= battMaxOutputPow:
#        dischargingPower = batteryInputPower
#        if (batteryStorage + dischargingPower*timeStep) < 0:
#            newBattStorage = 0
#        else:
#          newBattStorage = batteryStorage + dischargingPower*timeStep
#          
#    # batteryInputPower Positive (outwards flow into battery)
#    if batteryInputPower < 0 and abs(batteryInputPower) > battMaxOutputPow:
#        dischargingPower = -battMaxInputPow
#        if (batteryStorage + dischargingPower*timeStep) < 0:
#            newBattStorage = 0
#        else:
#          newBattStorage = batteryStorage + dischargingPower*timeStep
#
#    return newBattStorage
#
#def generatorManagement(powerNeeded, newBattStorage, genMaxPow, battMaxInputPow, battMaxStorage, timeStep, strategy):
#    """
#    The function tells us the power at which the generator should work as well as the energy stored in the battery by the end of the 
#    time period
#    """
#    if strategy == "1":
#        generatorPow = round(min(genMaxPow, powerNeeded), 3)
#        return [generatorPow, newBattStorage]
#    if strategy == "2":
#        chargingPow = min(battMaxInputPow, (battMaxStorage - newBattStorage)/timeStep)
#        generatorPow = round(
#            min(powerNeeded + chargingPow, genMaxPow), 3)
#        newBattStorage += chargingPow * timeStep
#        return [generatorPow, newBattStorage]

def dispatchingStrategy(powerVariables, energyVariables,
                        componentSpecifications, strategy):
    """
    INPUT :
        powerVariables : 
            list:
                - netLoad (the power demand on the grid, float)
                - timeStep (the timeStep considered, float) --> it will help us switching from power to energyVariablesVariablesVariablesVariables
        energyVariables : 
            list:
                - batteryStorage (the energy stored in the battery, float)
        componentSpecifications : 
            list :
                - battMaxStorage (the energy storage capacity of the battery, float), 
                - genMaxPow (the maximum power output of the generator, float), 
                - battMaxInputPow (the maximum power admissible to charge the battery, float),
                - battMaxOutputPow (the maximum power yielded by the battery)
                - SOC_min (the minimum admissible charge for the battery, float)
        - strategy (the chosen dispatching strategy, string)
    
    OUPUT :
        list :
            - genPower (the power at which the generator functioned, float)  
            - newBattStorage (the new amount of energy stored in the battery, float)              
    
    Given a load, the energy stored in the battery and the specifications of the different components of the grid as well as the dispatching
    strategy, the function yields the power at which the generator had to function to meet the requirements of the load, as well 
    as the new battery storage. Ultimately, this function will be called after each step forward in time.
    """
    debut = time.time()
    
    def batteryManagement(batteryInputPower):
        """
        The function returns the amount of energy stored in the battery by the end of the time period given charge/discharge
        """
        # batteryInputPower Positive (inwards flow into battery)
        if batteryInputPower <= battMaxInputPow and batteryInputPower >= 0:
            chargingPower = batteryInputPower
            if (battMaxStorage - batteryStorage) >= chargingPower * timeStep:
                newBattStorage = batteryStorage + chargingPower * timeStep
            else:
                newBattStorage = battMaxStorage

        # batteryInputPower Positive (inwards flow into battery)
        if batteryInputPower > battMaxInputPow and batteryInputPower >= 0:
            chargingPower = battMaxInputPow
            if (battMaxStorage - batteryStorage) >= chargingPower * timeStep:
                newBattStorage = batteryStorage + chargingPower * timeStep
            else:
                newBattStorage = battMaxStorage

        # batteryInputPower Positive (outwards flow into battery)
        if batteryInputPower < 0 and abs(batteryInputPower) <= battMaxOutputPow:
            dischargingPower = batteryInputPower
            if (batteryStorage + dischargingPower*timeStep) < 0:
                newBattStorage = 0
            else:
              newBattStorage = batteryStorage + dischargingPower*timeStep
              
        # batteryInputPower Positive (outwards flow into battery)
        if batteryInputPower < 0 and abs(batteryInputPower) > battMaxOutputPow:
            dischargingPower = -battMaxInputPow
            if (batteryStorage + dischargingPower*timeStep) < 0:
                newBattStorage = 0
            else:
              newBattStorage = batteryStorage + dischargingPower*timeStep

        return newBattStorage

    def generatorManagement(powerNeeded, newBattStorage):
        """
        The function tells us the power at which the generator should work as well as the energy stored in the battery by the end of the 
        time period
        """
        if strategy == "1":
            generatorPow = round(min(genMaxPow, powerNeeded), 3)
            return [generatorPow, newBattStorage]
        if strategy == "2":
            chargingPow = min(battMaxInputPow, (battMaxStorage - newBattStorage)/timeStep)
            generatorPow = round(
                min(powerNeeded + chargingPow, genMaxPow), 3)
            newBattStorage += chargingPow * timeStep
            return [generatorPow, newBattStorage]

    # We need to define a few variables first
    netLoad, timeStep = powerVariables[0], powerVariables[1]
    batteryStorage = energyVariables[0]
    battMaxStorage, genMaxPow, battMaxInputPow, battMaxOutputPow, SOC_min = componentSpecifications[
        0], componentSpecifications[1], componentSpecifications[
            2], componentSpecifications[3], componentSpecifications[4]

    # We check whether we produce more than needed or not
    if netLoad <= 0:
        newBattStorage = batteryManagement(abs(netLoad))
#        newBattStorage = batteryManagement(abs(netLoad), battMaxInputPow, battMaxOutputPow, battMaxStorage, batteryStorage, timeStep)
        generatorPower = 0
#        print(time.time() - debut)
        return [generatorPower, round(newBattStorage, 3)]
    else:
        dischargingPow = min(netLoad, (batteryStorage - SOC_min) / timeStep, battMaxOutputPow)
        newBattStorage = round(batteryStorage - dischargingPow * timeStep, 3)
        # If the battery can cover the power needs of the grid
        if dischargingPow >= netLoad:  # Output power battery depends on the amount of energy left in it
            res = [0, newBattStorage]
        # If we don't meet either of the previous conditions, we fall back in the case where we have to turn the generator on
        else:
            powerNeeded = netLoad - dischargingPow
            res = generatorManagement(powerNeeded, newBattStorage)
#            res = generatorManagement(powerNeeded, newBattStorage, genMaxPow, battMaxInputPow, battMaxStorage, timeStep, strategy)
            
#        print(time.time() - debut)
        return res


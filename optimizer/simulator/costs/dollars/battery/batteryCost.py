# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 14:53:02 2020

@author: bastien velitchkine
"""

from simulator.costs.dollars.battery.auxilliaryCostFunctions import batteryLifeTime, totalReplacementCost, operatingCost, remainingHours, salvageCost

def batteryCost(powerTimeVector, discountRate, timeVariables, costVariables,
                batteryVariables):
    """
    INPUT :
        - powerTimeVector : np.array of the power input/output of the battery at each time step of the simulation
        - discountRate : float
        - timeVariables : list of
           - timeStep : float, the time step of the simulation in hours
           - lifespan : int, the lifespan of the project in hours
        - costVariables : list of
           - replacementCost : float, the cost in €/kW to replace the battery
           - costPerHour : float, how much it costs to operate the battery per kW and per hour
           - investmentCost : float, investment cost of the battery
        - batteryVariables : list of 
           - battMaxThroughput : int, the maximum throughput of the battery over its lifetime in kWh
           - batteryMaxLife : int, the lifespan of the battery in hours
    OUTPUT :
        - totalCost : float, the total discounted cost of the dg during the whole project
    
    """
#    print("début")
    timeStep, lifespan = timeVariables[0], timeVariables[1]
    replacementCost, costPerHour, investmentCost = costVariables[
        0], costVariables[1], costVariables[2]
    battMaxThroughput, batteryMaxLife = batteryVariables[0], batteryVariables[
        1]

    capitalCost = investmentCost

    replacementTime = batteryLifeTime(powerTimeVector, timeStep,
                                      battMaxThroughput, batteryMaxLife)
    totReplacementCost = totalReplacementCost(replacementTime, lifespan,
                                              replacementCost, discountRate)

    operCost = operatingCost(costPerHour, discountRate, lifespan)

    hoursLeft = remainingHours(replacementTime, lifespan)
    salvCost = salvageCost(hoursLeft, replacementCost, lifespan,
                           replacementTime, discountRate)

    totalCost = capitalCost + (totReplacementCost - salvCost) + operCost
#    print("The battery cost is : {}$\n".format(totalCost))
    return totalCost


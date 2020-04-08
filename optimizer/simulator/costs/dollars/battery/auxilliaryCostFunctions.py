# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 14:51:52 2020

@author: bastien velitchkine
"""

import numpy as np

def operatingCost(costPerHour, discountRate, lifespan):
    """The function takes the cost to operate the battery for one kW and for one hour, the discount
    rate and the lifespan of the whole project. It returns the total operating cost (discounted). We suppose that the battery is working
    at all times"""
    nbWorkHoursYear = 24 * 365
    # we suppose that the number of working hours is uniformously scattered on the whole lifespan of the project, on a year scale
    discountedCost = np.sum([
        (costPerHour * nbWorkHoursYear) / ((1 + discountRate)**i)
        for i in range(lifespan//(365 * 24))
    ])
    return discountedCost

def batteryThroughput(powerTimeVector, timeStep):
    """The function takes the vector of power coming in or out of the battery at each time step in kW as well as the timeStep of the 
    simulation in hours"""
    throughput = 0
    for power in powerTimeVector:
        throughput += abs(power) * timeStep
    return throughput

def batteryLifeTime(powerTimeVector, timeStep, maxThroughput, batteryMaxLife):
    """The function takes the vector of power running through the battery at each time step, the time step, 
    the maximum amount of energy allowed to run through the battery as well as the expected life time of the battery. 
    The function returns the actual time span after which we must replace the battery """
    throughput = batteryThroughput(powerTimeVector, timeStep)
    simulationDuration = len(powerTimeVector) * timeStep
    throughputExpectancy = (maxThroughput / throughput) * simulationDuration
    replacementTime = min(throughputExpectancy, batteryMaxLife)
    return replacementTime

def totalReplacementCost(replacementTime, lifespan, replacementCost,
                         discountRate):
    """The function takes the time after which we must replace the battery, the lifespan of the project,
    the replacementCost of the machine in €/kW 
    and the discount Rate. 
    It returns the total and discounted replacement cost
    of the machine during the project (we might have to replace
    it several times)"""
    machineLifeTimeYear = replacementTime / (24 * 365)
    numberReplacements = int(lifespan / replacementTime) #If lifespan = 20y and machineLifeTimeYears = 6y then numberReplacements = 3
    temp = [
        replacementCost / ((1 + discountRate) ** (i * machineLifeTimeYear))
        for i in range(1, numberReplacements + 1)
    ]
    totalCost = np.sum(temp)
    return totalCost

def remainingHours(replacementTime, lifespan):
    """The function takes the time after which we must replace the battery and the lifespan of the project, both in hours.
    Then it returns the number hours
    the machine could still have worked starting from the end of the project"""
    remainingHours = replacementTime - (lifespan % replacementTime)
    return remainingHours

def salvageCost(hoursLeft, replacementCost, lifespan, replacementTime, discountRate):
    """The function takes the number of remaining hours the machine has, the replacement cost (€/kW), the lifespan of the project, the lifetime of the machine and the
    discount rate. It returns the discounted salvage cost"""
    salvageCost = (hoursLeft/replacementTime) * replacementCost / ((1 + discountRate)**(lifespan // (24 * 365)))
    return salvageCost    
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 15:45:58 2020

@author: bastien velitchkine
"""
import numpy as np

def workingHours(powerTimeVector, timeStep, lifespan):
    """The function takes the numpy array of the power output of 
    the machine at each time step as well as the time step for 
    the simulation and the life span of the entire project. 
    It returns the number of working hours of the machine during
    the whole project time span"""
    wholePeriod = len(powerTimeVector) * timeStep
    numberTimeUnits = len([x for x in powerTimeVector if x != 0.])
    numberHours = numberTimeUnits * timeStep
    workingHours = numberHours * (lifespan/wholePeriod)
    return workingHours

def totalReplacementCost(nbWorkingHours, machineLifeTime, replacementCost,
                         discountRate):
    """The function takes the total amount of working hours, 
    the life time of the machine, the replacementCost of the machine in €/kW 
    and the discount Rate. 
    It returns the total and discounted replacement cost
    of the machine during the project (we might have to replace
    it several times)"""
    machineLifeTimeYear = machineLifeTime / (24 * 365)
    numberReplacements = int(nbWorkingHours / machineLifeTime) #If lifespan = 20y and machineLifeTimeYears = 6y then numberReplacements = 3
    totalCost = np.sum([
        replacementCost / ((1 + discountRate) ** (i * machineLifeTimeYear))
        for i in range(1, numberReplacements + 1)
    ])
    return totalCost

def operatingCost(numberWorkingHours, costPerHour, discountRate, lifespan):
    """The function takes the number of working hours of the machine, the cost to operate it for one kW and for one hour, the discount
    rate and the lifespan of the whole project. It returns the total operating cost (discounted)"""
    nbWorkHoursYear = (numberWorkingHours / lifespan) * 24 * 365
    # we suppose that the number of working hours is uniformously scattered on the whole lifespan of the project, on a year scale
    discountedCost = np.sum([
        (costPerHour * nbWorkHoursYear) / ((1 + discountRate)**i)
        for i in range(lifespan//(365 * 24))
    ])
    return discountedCost

def fuelCost(powerTimeVector, fuelCurve, fuelPrice, discountRate, lifespan, timeStep):
    """
    INPUT :
         - powerTimeVector : np.array of the power output of the machine
         - fuelCurve : function that returns the fuel consumption of the machine (in liters of fuel) for a given functionning power and a given time
         - fuelPrice : float giving the price of one liter of fuel
         - discountRate : float
         - lifespan : int giving the lifespan of the project in hours
         - timeStep : float, time step of the simulation in hours
     OUTPUT :
         - fuelCost : float giving the discounted cost of the fuel during the whole project
    """
    simulationDuration = len(powerTimeVector) * timeStep
    costVector = [fuelCurve(power, timeStep) * fuelPrice for power in powerTimeVector]
    # Now we still need to discount the prices
    # First, we need the cost vector for the whole project
    newVector = []
    time = 0
    while time < lifespan:
        newVector += costVector
        time += simulationDuration * timeStep
    # Then, we discount the prices considering the number of years spent since the launch of the project
    discountedCostVect = [newVector[i]/((1 + discountRate)**((i * timeStep)//(24 * 365))) for i in range(len(newVector))]
    discountedCost = 0
    i = 0
    while i * timeStep < lifespan:
        discountedCost += discountedCostVect[i] 
        i += 1
    return discountedCost

def remainingHours(nbWorkingHours, machineLifeTime):
    """The function takes the number of working hours of the project and the machineLifeTime, both in hours, and then returns the number hours
    the machine could still have worked starting from the end of the project"""
    remainingHours = machineLifeTime - (nbWorkingHours % machineLifeTime)
    return remainingHours

def salvageCost(hoursLeft, replacementCost, lifespan, machineLifeTime, discountRate):
    """The function takes the number of remaining hours the machine has, the replacement cost (€/kW) the lifespan of the project, the lifetime of the machine and the
    discount rate. It returns the discounted salvage cost"""
#    print(replacementCost, hoursLeft, lifespan, machineLifeTime, discountRate)
    salvageCost = (hoursLeft/machineLifeTime) * replacementCost / ((1 + discountRate)**(lifespan // (24 * 365)))
    return salvageCost    

def totalInvestmentCost(investmentCost, dgMaxPower):
    """
    INPUT:
        - investmentCost: float, the investment cost for a 1kW dg in $
        - dgMaxPower: float, the maximum power output of the dg in kW
    OUTPUT:
        - totalCost: float, the total investment cost of the dg
    """
    totalCost = investmentCost * dgMaxPower
    return totalCost
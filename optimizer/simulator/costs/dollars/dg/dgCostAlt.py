# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 15:47:36 2020

@author: bastien velitchkine
"""

from simulator.costs.dollars.dg.auxilliaryCostFunctions import totalReplacementCost, workingHours, operatingCost, fuelCost, remainingHours, salvageCost

def dgCost(powerTimeVector, discountRate, timeVariables, costVariables, fuelVariables):
    """
    INPUT :
        - powerTimeVector : np.array of the power output of the DG at each time step of the simulation
        -discountRate : float
        - timeVariables : list of
           - timeStep : float, the time step of the simulation in hours
           - dgLifeSpan : int, the lifespan of the diesel generator in hours
           - lifespan : int, the lifespan of the project in hours
        - costVariables : list of
           - replacementCost : float, the cost in €/kW to replace the DG
           - costPerHour : float, how much it costs to operate the DG per kW and per hour
           - investmentCost : float, investment cost of the dg
        - fuelVariables : list of
           - fuelPrice : float, the price of one liter of fuel
           - fuelCurve : a function which given a power and working duration gives the amount of fuel consumed
    OUTPUT :
        - totalCost : float, the total discounted cost of the dg during the whole project
    
    """
    timeStep, dgLifeTime, lifespan = timeVariables[0], timeVariables[1], timeVariables[2]
    replacementCost, costPerHour, investmentCost = costVariables[0], costVariables[1], costVariables[2]
    fuelPrice, fuelCurve = fuelVariables[0], fuelVariables[1]
    
    capitalCost = investmentCost
    replacementCost = totalReplacementCost(lifespan, dgLifeTime, replacementCost, discountRate)
    nbWorkingHours = workingHours(powerTimeVector, timeStep, lifespan)
    operCost = operatingCost(nbWorkingHours, costPerHour, discountRate, lifespan)
    oilCost = fuelCost(powerTimeVector, fuelCurve, fuelPrice, discountRate, lifespan, timeStep)
    hoursLeft = remainingHours(nbWorkingHours, dgLifeTime)
    salvCost = salvageCost(hoursLeft, replacementCost, lifespan, dgLifeTime, discountRate)
    
    totalCost = capitalCost + (replacementCost - salvCost) + operCost + oilCost
    return totalCost
    


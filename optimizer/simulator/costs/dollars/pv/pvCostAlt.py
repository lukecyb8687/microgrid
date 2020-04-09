# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 17:24:17 2020

@author: bastien velitchkine
"""

from simulator.costs.dollars.pv.auxilliaryCostFunctions import totalInvestmentCost, totalReplacementCost, workingHours, operatingCost, remainingHours, salvageCost

def pvCost(powerTimeVector, pvMaxPower, discountRate, timeVariables, costVariables):
    """
    INPUT :
        - powerTimeVector : np.array of the power output of the pv at each time step of the simulation
        - pvMaxPower: float, the power of pv installed (kWp)
        - discountRate : float
        - timeVariables : list of
           - timeStep : float, the time step of the simulation in hours
           - pvLifeSpan : int, the lifespan of the pvs in hours
           - lifespan : int, the lifespan of the project in hours
        - costVariables : list of
           - replacementCost : float, the cost in €/kW to replace the pvs
           - costPerHour : float, how much it costs to operate the pv per kWp and per hour
           - investmentCost : float, investment cost of a 1 kWp pv
    OUTPUT :
        - totalCost : float, the total discounted cost of the dg during the whole project
    
    """
    timeStep, pvLifeTime, lifespan = timeVariables[0], timeVariables[1], timeVariables[2]
    replacementCost, costPerHour, investmentCost = costVariables[0], costVariables[1], costVariables[2]
    
    capitalCost = totalInvestmentCost(investmentCost, pvMaxPower)
    replacementCost = totalReplacementCost(lifespan, pvLifeTime, replacementCost, discountRate)
    nbWorkingHours = workingHours(powerTimeVector, timeStep, lifespan)
    operCost = operatingCost(nbWorkingHours, costPerHour, discountRate, lifespan)
    hoursLeft = remainingHours(nbWorkingHours, pvLifeTime)
    salvCost = salvageCost(hoursLeft, replacementCost, lifespan, pvLifeTime, discountRate)
    
    totalCost = capitalCost + (replacementCost - salvCost) + operCost
    return totalCost
    

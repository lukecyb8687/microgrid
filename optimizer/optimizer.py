# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 12:58:54 2020

@author: bastien velitchkine
"""
import numpy as np

from simulator.dispatching.dispatchingLoop import dispatchingLoop
from simulator.costs.dollars.dollarCost import dollarCost
from simulator.costs.carbon.carbonCost import carbonCost

from platypus import NSGAII, Problem, Real
import time

def optimizer(fixedParameters, constraints):
    """
            - fixedParameters: {gridComponents : {
                                                        "battery" : {
                                                                        "initialStorage": float between 0 and 1, the battery initial energy storage as a percentage of its maximum capacity,
                                                                        "maxInputPow": float, the maximum charging power of the battery in kW for a 1kWh battery. The real value will be obtained by multiplying by the maximum storage capacity,
                                                                        "maxOutputPow": float, the maximum discharging power of the battery in kW for a 1kWh battery. The real value will be obtained by multiplying by the maximum storage capacity,
                                                                        "SOC_min": float, the minimum amount of energy that can be stored in the battery as a percentage of the maximum storage capacity,
                                                                        "maxThroughput": float, the number by which we multiply the max storage to get the maximum amount of energy that can flow in and out of the battery during its lifetime (kWh),
                                                                        "lifetime": int, the nominal lifetime of the battery in hours. It's the time after which we must replace it if we did not exceed the maximum throughput,
                                                                        "capitalCost": float, the cost of a 1kWh battery in $,
                                                                        "replacementCost": float, the cost to replace 1kWh of batteries in $,
                                                                        "operationalCost": float, the cost PER HOUR, to operate and maintain the battery ($)
                                                                    },
                                                        "diesel" : {
                                                                        "fuelCost": float, the cost of 1l of fuel ($),
                                                                        "fuelCostGrad": float, there is a fuel curve modeling the relationship between the functionning power of the dg and it's consumption of liters fuel per kW. This parameter is the slope of the model curve,
                                                                        "fuelCostIntercept": float, there is a fuel curve modeling the relationship between the functionning power of the dg and it's consumption of liters fuel per kW. This parameter is the intercept of the model curve,
                                                                        "lifetime": int, the nominal lifetime of the dg in hours,
                                                                        "capitalCost": float, the cost of the dg in $,
                                                                        "replacementCost": float, the cost to replace the dg in $,
                                                                        "operationalCost": float, the cost PER HOUR, to operate and maintain the dg,
                                                                    },
                                                        "photovoltaic" : {
                                                                            "lifetime": int, the nominal lifetime of a pannel in hours,
                                                                            "capitalCost": float, the cost of a pannel in $,
                                                                            "replacementCost": float, the cost to replace a pannel in $,
                                                                            "operationalCost": float, the cost PER HOUR, to operate and maintain the pannel ($),
                                                                            "powerTimeVector": numpy array, the power output of the pannel at each time step (kW)
                                                                        }
                                                    },
                                    
                               timeStep : float, the time step of the simulation that generated the load in hours,
                               loadVector : numpy array of floats, the power demand on the grid (kW),
                               projectDuration : int, the duration of the whole project in hours (e.g 25 * 365 * 24),
                               discountRate: float, the discount ratio,
                               strategy : "LF" or "CC", respectively for "Load Following" or "Cycle Charging"
                - constraints : {
                                    "diesel":
                                                {
                                                        "upperBound": float, the upper Bound for the value of the generatorMaximumPower (kW),
                                                        "lowerBound": float, the lower Bound for the value of the generatorMaximumPower (kW),
                                                },
                                     "battery":
                                                {
                                                        "upperBound": float, the upper Bound for the value of the battery maximum storage capacity (kWh),
                                                        "lowerBound": float, the lower Bound for the value of the battery maximum storage capacity (kWh),
                                                },
                                     "photovoltaic":
                                                    {
                                                            "upperBound": float, the upper Bound for the value of the pvMaximumPower (kW),
                                                            "lowerBound": float, the upperlower Bound for the value of the pvMaximumPower (kW),
                                                    },           
                                }
                                                    
    OUTPUT:
        {
                "parameters":
                            {
                                    "battery": float, the battery storage capacity (kWh),
                                    "diesel": float, the generator maximum power (kW),
                                    "photovoltaic": float, the pv maximum power (kW)                                                
                            },
                "costs":
                        {
                                "dollars": float, the cost of the project in dollars,
                                "carbon": float, the carbon emissions generated by the project (kg)
                        }
                            
        }                                                    
    """        
    
    gridComponents = fixedParameters["gridComponents"]
    timeStep = fixedParameters["timeStep"]
    loadVector = fixedParameters["loadVector"]
    projectDuration = fixedParameters["projectDuration"]
    discountRate = fixedParameters["discountRate"]
    strategy = fixedParameters["strategy"]
    pvPowerTimeVector = gridComponents["photovoltaic"]["powerTimeVector"]
    normalizingFactor = 52
    maxInputPowMulti = gridComponents["battery"]["maxInputPow"] 
    maxOutputPowMulti = gridComponents["battery"]["maxOutputPow"] 
    SOC_min_multi = gridComponents["battery"]["SOC_min"] 
    
    def costFunction(x):
        gridComponents["battery"]["maxStorage"] = x[0]
        gridComponents["diesel"]["maxPower"] = x[1]
        gridComponents["photovoltaic"]["maxPower"] = x[2]
        
        batteryInitialStorage = gridComponents["battery"]["initialStorage"] * x[0]
        battMaxInputPow = maxInputPowMulti * x[0]
        battMaxOutputPow = maxOutputPowMulti * x[0]
        SOC_min = SOC_min_multi * x[0]
        specifications = [x[0], x[1], battMaxInputPow, battMaxOutputPow, SOC_min]
        
        pvPowerVector = ((pvPowerTimeVector)/normalizingFactor)*(x[2])
        netLoadVector = loadVector - pvPowerVector
        dispatchingResult = dispatchingLoop(timeStep, netLoadVector, batteryInitialStorage, specifications, strategy)

        return [dollarCost(gridComponents, timeStep, loadVector, projectDuration, discountRate, strategy, dispatchingResult),
                carbonCost(gridComponents, timeStep, loadVector, projectDuration, discountRate, strategy, dispatchingResult)]
    
    problem = Problem(3, 2)
    problem.types[:] = [Real(constraints["battery"]["lowerBound"], constraints["battery"]["upperBound"]), Real(constraints["diesel"]["lowerBound"], constraints["diesel"]["upperBound"]), Real(constraints["photovoltaic"]["lowerBound"], constraints["photovoltaic"]["upperBound"])]
    problem.function = costFunction # lambda x: [sum(x), sum([val**2 for val in x])] #The function helped us see that the computational time of our cost functions was a problem
    
    algorithm = NSGAII(problem)
    algorithm.run(1)
    
    # display the results
    for solution in algorithm.result:
        print(solution.objectives)
        
def optimizerTest():
    """
    A simple function to test the function `optimizer`
    """
    debut = time.time()    
    fixedParameters = {
                            "gridComponents": {
                                                        "battery" : {
                                                                        "initialStorage": 1.,
                                                                        "maxInputPow": 6 * 157,
                                                                        "maxOutputPow": 6 * 500,
                                                                        "SOC_min": 0.,
                                                                        "maxThroughput": 3000.,
                                                                        "lifetime": 5 * 365 * 24,
                                                                        "capitalCost": 200,
                                                                        "replacementCost": 200,
                                                                        "operationalCost": 0.03
                                                                    },
                                                        "diesel" : {
                                                                        "fuelCost": 1.2,
                                                                        "fuelCostGrad": 1.,
                                                                        "fuelCostIntercept": 0.,
                                                                        "lifetime": 10 * 365 * 24,
                                                                        "capitalCost": 1000,
                                                                        "replacementCost": 1000,
                                                                        "operationalCost": 0.03,
                                                                    },
                                                        "photovoltaic" : {
                                                                            "lifetime": 25 * 365 * 24,
                                                                            "capitalCost": 500,
                                                                            "replacementCost": 500,
                                                                            "operationalCost": 0.03,
                                                                            "powerTimeVector": np.array([abs(np.sin((2 * np.pi * hour/ 48))) for hour in np.arange(0, 24 * 365)]) # We suppose that the irradiance of the pannels is a sinusoide
                                                                        }
                                                    },
                                    
                               "timeStep" : 1,
                               "loadVector" : np.array([abs(np.sin((2 * np.pi * hour/ 24 - (np.pi/2)))) for hour in np.arange(0, 24 * 365)]), # We model the load by a sinusoide with max demand at 6 am and 6pm
                               "projectDuration" : 25 * 365 * 24,
                               "discountRate": 0.0588,
                               "strategy" : "LF"
                       }
                                                        
    constraints = {
                                    "diesel":
                                                {
                                                        "upperBound": 100,
                                                        "lowerBound": 0,
                                                },
                                     "battery":
                                                {
                                                        "upperBound": 100,
                                                        "lowerBound": 0,
                                                },
                                     "photovoltaic":
                                                    {
                                                            "upperBound": 100,
                                                            "lowerBound": 0,
                                                    },           
                                }
                                                    
    optimizer(fixedParameters, constraints)    
    print("The total computation took {}s".format(time.time() - debut))
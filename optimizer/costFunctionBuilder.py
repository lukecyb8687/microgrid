# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 11:09:27 2020

@author: bastien velitchkine
"""

from simulator.dollarCost import dollarCost

def costFunctionBuilder(gridComponents, timeStep, loadVector, projectDuration, discountRate, strategy):
    """
    INPUTS :
        - gridComponents : 
                            {
                                "battery" : {
                                                "initialStorage": float, the battery initial energy storage (kWh),
                                                "maxInputPow": float, the maximum charging power of the battery (kW),
                                                "maxOutputPow": float, the maximum discharging power of the battery (kW),
                                                "SOC_min": float, the minimum amount of energy that can be stored in the battery (kWh),
                                                "maxThroughput": float, the maximum amount of energy that can flow in and out of the battery during its lifetime (kWh),
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
                            }
       - timeStep : float, the time step of the simulation that generated the load in hours
       - loadVector : numpy array of floats, the power demand on the grid (kW)
       - projectDuration : int, the duration of the whole project in hours (e.g 25 * 365 * 24)
       - discountRate: float, the discount ratio
       - strategy : "LF" or "CC", respectively for "Load Following" or "Cycle Charging"
   OUTPUT:
       - lambda function
       
   It returns the lambda function whose parameters are the one to optimize, like the size of the generator, of the batteries or the pvs.
           
    """
    
    newFunction = lambda battMaxStorage, genMaxPower, pvMaxPower: [
                                                                    dollarCost(
                                                                        {
                                                                            "battery": {
                                                                                **gridComponents["battery"], "maxStorage": battMaxStorage
                                                                            },
                                                                            "diesel": {
                                                                                **gridComponents["diesel"], "maxPower": genMaxPower
                                                                            },
                                                                            "photovoltaic": {
                                                                                **gridComponents["photovoltaic"], "maxPower": pvMaxPower
                                                                            }
                                                                        }, timeStep, loadVector, projectDuration, discountRate, strategy)
                                                                ]
      

    return newFunction
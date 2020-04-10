# -*- coding: utf-8 -*-
"""
Created on Fri Apr  10 13:37:42 2020

@author: bastien velitchkine
"""

import os
os.chdir("./optimizer")

from optimizer import optimizer
import time
import numpy as np

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
                                                                            ## PV VECTOR TO MODIFY
                                                                            "powerTimeVector": np.array([abs(np.sin((2 * np.pi * hour/ 48))) for hour in np.arange(0, 24 * 365)]) # We suppose that the irradiance of the pannels is a sinusoide
                                                                        }
                                                    },
                                    
                               "timeStep" : 1,
                               ## LOAD VECTOR TO MODIFY
                               "loadVector" : np.array([abs(np.sin((2 * np.pi * hour/ 24 - (np.pi/2)))) for hour in np.arange(0, 24 * 365)]), # We model the load by a sinusoide with max demand at 6 am and 6pm
                               "projectDuration" : 25 * 365 * 24,
                               "discountRate": 0.0588,
                               "strategy" : "LF"
                       }
                                                        
    constraints = {
                                    "diesel":
                                                {
                                                        "upperBound": 2000,
                                                        "lowerBound": 0,
                                                },
                                     "battery":
                                                {
                                                        "upperBound": 1000,
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
    
optimizerTest()
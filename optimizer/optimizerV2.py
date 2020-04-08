# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 12:58:54 2020

@author: bastien velitchkine

Edited on Wed Apr 8 10:46:23 2020

@author: yun bin choh
"""

from platypus import NSGAII, Problem, Real
import matplotlib.pyplot as plt
from simulator.costs.dollars.dollarCost import dollarCost
from simulator.costs.carbon.carbonCost import carbonCost

def optimizer(gridComponents,constraints,timeStep,loadVector ,projectDuration ,discountRate ,strategy ):
    """
            - gridComponents : {
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
                                },
                  
              - timeStep : float, the time step of the simulation that generated the load in hours,
              - loadVector : numpy array of floats, the power demand on the grid (kW),
              - projectDuration : int, the duration of the whole project in hours (e.g 25 * 365 * 24),
              - discountRate: float, the discount ratio,
              - strategy : "LF" or "CC", respectively for "Load Following" or "Cycle Charging"
              
     
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

        
    def optimizerBuilder(x):
        from dollarCost import dollarCost
        from costCarbon import emissionCO2
        gridComponents["battery"]["maxStorage"] = x[0]
        gridComponents["diesel"]["maxPower"] = x[1]
        gridComponents["photovoltaic"]["maxPower"] = x[2]


        return [dollarCost(gridComponents, timeStep, loadVector, projectDuration, discountRate, strategy),
                emissionCO2(gridComponents, timeStep, loadVector, projectDuration, discountRate, strategy)]

    problem = Problem(3, 2)
    problem.types[:] = [Real(constraints["battery"]["lowerBound"], constraints["battery"]["upperBound"]), Real(constraints["diesel"]["lowerBound"], constraints["diesel"]["upperBound"]), Real(constraints["photovoltaic"]["lowerBound"], constraints["photovoltaic"]["upperBound"])]

    problem.function = optimizerBuilder
    algorithm = NSGAII(problem)
    algorithm.run(100)
    feasible_solutions = [s for s in algorithm.result if s.feasible]

    # Storing the results
    f1 = []
    f2 = []
    for solution in algorithm.result:
        print(solution.objectives)
        f1.append(solution.objectives[0])
        f2.append(solution.objectives[1])

    # Display results in a scatter plot
    plt.scatter(f1,
                f2)
    plt.xlim([1e5, 3e7])
    plt.ylim([0, 15])
    plt.xlabel("$f_1(x)$: NPC function (euros)")
    plt.ylabel("$f_2(x)$: Carbon emission function (kgCO2e/h)")
    plt.show()

    return f1,f2,feasible_solutions

# To test (Input variables to be modified. This section can be ignored after successful test run):
gridComponents = {
                    "battery" : {
                                    "initialStorage": 892,
                                    "maxInputPow": 6 * 167 * 892,
                                    "maxOutputPow": 6 * 500 * 892,
                                    "SOC_min": 0,
                                    "maxThroughput": 3000,
                                    "lifetime": 15*8760,
                                    "capitalCost": 550,
                                    "replacementCost": 550,
                                    "operationalCost": 10
                                },
                    "diesel" : {
                                    "fuelCost": 1,
                                    "fuelCostGrad": 0.2359760012,
                                    "fuelCostIntercept": 28.5,
                                    "lifetime": 162060,
                                    "capitalCost": 500,
                                    "replacementCost": 500,
                                    "operationalCost": 0.030,
                                },
                    "photovoltaic" : {
                                        "lifetime": 25*8760,
                                        "capitalCost": 2500,
                                        "replacementCost": 2500,
                                        "operationalCost": 10,
                                        "powerTimeVector": LFdf['Pv_Output']
                                    }
                }
                 
timeStep = 1
loadVector = LFdf['Demand']
projectDuration = 25*8760
discountRate = 5/100
strategy = "LF" 

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
                                        "upperBound": 10,
                                        "lowerBound": 0,
                                },           
              }
#     %%time 
results = optimizer(gridComponents,constraints,timeStep,loadVector ,projectDuration ,discountRate ,strategy)[2]


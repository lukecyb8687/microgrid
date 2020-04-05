# Introduction

In most places (in developped countries at least), people get their energy from the national grid. The energy comes from different power plants such as nuclear power plants or hydro power plants. But in many other isolated places, like islands (for instance the Ouessant Island in France), it is more relevant to implemant **a new smaller grid** to meet the power needs of the island's inhabitants. It is more cost-efficient to build a new grid than to connect the island to the national grid with submarine cables.

The power needs of a small island are obviously not that of a whole region, so nuclear power plants can be discarded from the beginning, water dams as well. It usually boils down to **a few renewable energy production sites and a diesel generator** to ensure steady energy production (when the sun sets, and the wind stops to blow, mainly).

However, before picking your hammer and your screw driver, you must precisely know the dimensions of your micro grid : _What is the power demand on the grid?_, _How much sun and wind ressources can we reckon with?_, _How many PVs and windmills should we build?_, _How big should our batteries be?_, etc.
All these questions are subject to **optimization** : there are multile costs to optimize but mainly the **regular cost** 💸 and the **environmental cost** ⛽ captured inside the carbon dioxyde emissions.

Unfailingly, this leads to a [multi-objective optimization problem](#https://en.wikipedia.org/wiki/Multi-objective_optimization) where variables are merely the sizes of each installation (how much power supplied by each of the energy production sites).

Therefore, the aim of the project is to give an end-to-end program that optimizes the grid specifications for its needs. The inputs should be the _load_ (during a year, what is the power demand hour after hour), and a few _constraints_ (no more than 3 windmills, no more than one acre of PVs, you name it). The outputs of this program are mainly the values of the multiple cost-functions that have been optimized and most importantly, the **size of each power plant facility**.

# Prerequisites

What packages does the user need ? (e.g numpy, pymo, ...)

# Architecture

Below is the architecture of our project. it is subdivided in multiple packages and modules that all lead one main function, the one that will help the end user in his task of properly designing the micro-grid.

- 📁 simulator
  - 📑 dollarCost.py
  - 📁 dispatching
    - 📑 dispatchingStrategyFunction.py
  - 📁 costs
    - 📁 dollars
      - 📁 battery
        - 📑 auxilliaryCostFunctions.py
        - 📑 batteryCost.py
      - 📁 pv
        - 📑 costpv.py
        - 📑
      - 📁 diesel
        - 📑 costdg.py
        - 📑
      - 📁 windmill
        - 📑
        - 📑
    - 📁 carbon (afterwards)
- 📁 optimizer
- 📑 README.md

## Simulator

The simulator is a simplified package that yields the various costs of the micro-grid, given the sizes of each component of the grid. For instance :

> The lifespan of the project is 25 years. I know the load profile of the place over a whole year. How much would it cost (💸 and ⛽) if I had a 5 kWh battery, 2 wind turbines of 2kW each, 3kW worth of PVs and a diesel generator (dg) of 3kW ?

`dollarCost.py` and `carbonCost.py` are the two Python files in which functions compute the global cost and the global carbon dioxyde emissions during the whole project. Those are the _cost functions that the optimizer will aim at minimizing_.

### Dispatching

Over a year, depending on the **sun irradiation**, or the **windspeed**, you might alternatively switch on and off the diesel generator, or even store energy in the battery to meet future demand. For instance, during summer, there is a much higher sun irradiation, more than needed to meet the power demand during the day. So thanks to the PVs and the battery, one part of the energy can be directly consumed, and the extra amount of energy can be stored in the battery. The battery will discharge at night, after the sun set.

With regard to the dispatch, we can adopt _two different dispatching strategies_ : **cycle charging** and **load following**.

| Load following                                                                                                                                                                                                                                                                                                            | Cycle charging |
| :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :------------- |
| When renewable energies don't suffice to provide enough energy to the grid, we might want to turn on the dg. If we follow a load following strategy, we first check if there's enough energy in the battery to complete the energy supply. If not, we turn on the dg at a pace such that it **precisely meets the load**. | The case-study is exactly the same as the previous one, but this time, instead of turning on the dg at a lower pace, we turn it on at rate such that it both meets the load and the power needed to fully charge the battery. |

<!--
#### Load following

When renewable energies don't suffice to provide enough energy to the grid, we might want to turn on the dg. If we follow a load following strategy, we first check if there's enough energy in the battery to complete the energy supply. If not, we turn on the dg at a pace such that it **precisely meets the load**.

#### Cycle charging

The case-study is exactly the same as the previous one, but this time, instead of turning on the dg at a lower pace, we turn it on at rate such that it both meets the load and the power needed to fully charge the battery. -->

Whether we chose one strategy or the other, the dispatching algorithm will compute the amount of **energy stored in the battery** at each time step as well as the **functionning power of the dg** at each time step. It directly impacts the amount of _fuel consumed\_\_ as well as the \_lifetime of the battery_ for instance.

### Costs

#### Battery

The cost of the battery is calculated with the following formula :

```latex
total cost = investment cost + (replacement cost - salvage cost) + operating cost
```

where :

- The investment cost is basically the price of your batteries
- The replacement cost is the price of the batteries multiplied by the number of times you should replace them over the whole project's lifespan
- The salvage cost is the price at which you could expect to sell your batteries at the end of the project, considering their remaining lifetime
- The operating cost is the price you pay for your workforce to operate and maintain the batteries

The battery cost relies on the dispatch described above. Indeed, the dispatch heavily impacts the battery throughput (how much energy flows through the battery) and therefore its **lifetime** and consequently the number of replacements and therefore : **the cost**.

#### Diesel generator

#### Photo Voltaic Pannels

#### Wind turbines

## Optimizer

The optimizer is based on pre-existing python modules. Given a set of cost functions to minimize, the optimizer returns the sizes of each component in order to minimize the cost functions in the mean time. For instance :

> I want to minimize the cost and the carbon dioxyde emissions. I have a limited number of disposable pVs and windmills, my dg cannot be bigger than x, but I have no limits regarding my battery. The optimizer will return the power specifications of each of the components so as to minimize the cost and the carbon dioxyde emissions

## Simulator and optimizer

Both sides of the project work hand in hand. Basically, _the simulator provides the optimizer with the right cost functions to minimize._

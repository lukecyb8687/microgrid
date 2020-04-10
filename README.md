# Outline

- I. Introduction
- II. Quickstart
  - II.A. Packages
  - II.B. Code execution
- III. Architecture
- IV. Simulator
  - IV.A. Dispatching
  - IV.B. Costs
    - IV.B.1. Battery
    - IV.B.2. Diesel generator
    - IV.B.3. Photovoltaic pannels
    - IV.B.4. Wind turbines
    - IV.B.a) Dollar cost
    - IV.B.b) Carbon cost
- V. Optimizer
  - V.A. Cost functions
  - V.B. Bounds and parameters
- VI. Limits and extensions
  - VI.A. Efficience
  - VI.B. Solver
  - VI.C. User interface
- VII. Acknowledgements
- VIII. License
- IX. Contributors

# I. Introduction

In most places (in developped countries at least), people get their energy from the national grid. The energy comes from different power plants such as nuclear power plants or hydro power plants. But in many other isolated places, like islands (for instance the Ouessant Island in France), it is more relevant to implemant **a new smaller grid** to meet the power needs of the island's inhabitants. It is more cost-efficient to build a new grid than to connect the island to the national grid with submarine cables.

The power needs of a small island are obviously not that of a whole region, so nuclear power plants can be discarded from the beginning, water dams as well. It usually boils down to **a few renewable energy production sites and a diesel generator** to ensure steady energy production (when the sun sets, and the wind stops to blow, mainly).

However, before picking your hammer and your screw driver, you must precisely know the dimensions of your micro grid : _What is the power demand on the grid?_, _How much sun and wind ressources can we reckon with?_, _How many PVs and windmills should we build?_, _How big should our batteries be?_, etc.
All these questions are subject to **optimization** : there are multile costs to optimize but mainly the **regular cost** 💸 and the **environmental cost** ⛽ captured inside the carbon dioxyde emissions.

Unfailingly, this leads to a [multi-objective optimization problem](#https://en.wikipedia.org/wiki/Multi-objective_optimization) where variables are merely the sizes of each installation (how much power supplied by each of the energy production sites).

Therefore, the aim of the project is to give an end-to-end program that optimizes the grid specifications for its needs. The inputs should be the _load_ (during a year, what is the power demand hour after hour), and a few _constraints_ (no more than 3 windmills, no more than one acre of PVs, you name it). The outputs of this program are mainly the values of the multiple cost-functions that have been optimized and most importantly, the **size of each power plant facility**.

# II. Quickstart

Start by git **cloning** the repository on your machine and then download the following packages if they are or not already in your environment.

## II.A. Packages

- **numpy** 👉 the basic scientific library of Python with built-in math functions and easy array handling
- **time** 👉 for the sole purpose of printing the computational times
- **platypus** 👉 the multi-objective optimization library with [It's library](#https://platypus.readthedocs.io/en/latest/getting-started.html)
- **matplotlib.pyplot** 👉 for graph plotting
- **pandas** 👉 to manipulate dataframes, a Python object that comes in handy when we manipulate large datasets

## II.B. Code execution

Too make sure everything works all right, open `main.py` in your favorite _compiler_ (Pyzo, Spyder, ...) and execute the file. You should see plots popping. They display the results of the optimization process.

Then, if you want to go further and run the optimizer _with your own data_, you are more than encouraged to modify the parameters inside the `optimizerTest()` function. You should look for these variables in the code, and modify them accordingly :

```python
fixedParameters =
{
  "gridComponents": {
    .
    .
    .
  "strategy" : "LF"
}

constraints =
{
  "diesel": {
    "upperBound": 2000,
    .
    .
    .                                                       "lowerBound": 0
}
```

# III. Architecture

Below is the architecture of our project. it is subdivided in multiple packages and modules that all lead one main function, the one that will help the end user in his task of properly designing the micro-grid.

- 📑 README.md
- 📑 .gitignore
- 📑 main.py
- 📁 optimizer
  - 📑 optimizer.py
  - 📑 optimizerV2.py
  - 📁 simulator
    - 📁 dispatching
      - 📑 dispatchingLoop.py
      - 📑 dispatchingStrategy.py
    - 📁 costs
      - 📁 dollars
        - 📑 dollarCost.py
        - 📁 battery
          - 📑 auxilliaryCostFunctions.py
          - 📑 batteryCost.py
        - 📁 pv
          - 📑 auxilliaryCostFunctions.py
          - 📑 pvCostAlt.py
          - 📑 pvCost.py
        - 📁 diesel
          - 📑 auxilliaryCostFunctions.py
          - 📑 dgCostAlt.py
          - 📑 dgCost.py
        - 📁 windmill
          - 📑 windCost.py
      - 📁 carbon
        - 📑 carbonCost.py

# IV. Simulator

The simulator is a simplified package that yields the various costs of the micro-grid, given the sizes of each component of the grid. For instance :

> The lifespan of the project is 25 years. I know the load profile of the place over a whole year. How much would it cost (💸 and ⛽) if I had a 5 kWh battery, 2 wind turbines of 2kW each, 3kW worth of PVs and a diesel generator (dg) of 3kW ?

`dollarCost.py` and `carbonCost.py` are the two Python files in which functions compute the global cost and the global carbon dioxyde emissions during the whole project. Those are the _cost functions that the optimizer will aim at minimizing_.

## IV.A. Dispatching

Over a year, depending on the **sun irradiation**, or the **windspeed**, you might alternatively switch on and off the diesel generator, or even store energy in the battery to meet future demand. For instance, during summer, there is a much higher sun irradiation, more than needed to meet the power demand during the day. So thanks to the PVs and the battery, one part of the energy can be directly consumed, and the extra amount of energy can be stored in the battery. The battery will discharge at night, after the sun set.

With regard to the dispatch, we can adopt _two different dispatching strategies_ : **cycle charging** and **load following**.

| Load following                                                                                                                                                                                                                                                                                                            | Cycle charging                                                                                                                                                                                                                |
| :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| When renewable energies don't suffice to provide enough energy to the grid, we might want to turn on the dg. If we follow a load following strategy, we first check if there's enough energy in the battery to complete the energy supply. If not, we turn on the dg at a pace such that it **precisely meets the load**. | The case-study is exactly the same as the previous one, but this time, instead of turning on the dg at a lower pace, we turn it on at rate such that it both meets the load and the power needed to fully charge the battery. |

Whether we chose one strategy or the other, the dispatching algorithm will compute the amount of **energy stored in the battery** at each time step as well as the **functioning power of the dg** at each time step. It directly impacts the amount of _fuel consumed_ as well as the _lifetime of the battery_ for instance.

## IV.B. Costs

#### IV.B.1. Battery

The cost of the battery is calculated with the following formula :

```latex
total cost = investment cost + (replacement cost - salvage cost) + operating cost
```

where :

- The investment cost is basically the price of your batteries
- The replacement cost is the price of the batteries multiplied by the number of times you should replace them over the whole project's lifespan
  where :
- The salvage cost is the price at which you could expect to sell your batteries at the end of the project, considering their remaining lifetime
- The operating cost is the price you pay for your workforce to operate and maintain the batteries

The battery cost relies on the dispatch described above. Indeed, the dispatch heavily impacts the battery throughput (how much energy flows through the battery) and therefore its **lifetime** and consequently the number of replacements and therefore : **the cost**.

#### IV.B.2. Diesel generator

The cost of the Diesel generator is calculated with the following formula :

```latex
total cost = capital cost + (replacement cost - salvage cost) + operation & maintenance cost + fuel cost
```

where :

- The capital cost is the inital purchase price of the diesel generator
- The replacement cost is the cost of replacing the generator at the end of its lifetime
- The operational and maintenance cost is the annual cost of operating and maintaining the generator
- The salvage cost is the price at which you could expect to sell your diesel generator at the end of the project, considering their remaining lifetime
- The fuel cost is the price of fuel consumption according to the market price of diesel fuel.

Just like for the battery, the diesel generator cost is **heavily impacted by the dispatch**. Indeed, depending on the strategy and the dispatching result, we can't reckon with the same number of **working hours** for the dg for instance. If the number of working hours is not the same, the lifetime is not the same and therefore the number of replacements is not the same. _The more replacements, the more expensive_.

#### IV.B.3. Photo Voltaic Panels

The cost of the PV is calculated with the following formula :

```latex
total cost = capital cost + (replacement cost - salvage cost) + operation & maintenance cost
```

where :

- The capital cost is the inital purchase price of the PV
- The replacement cost is the cost of replacing the PV at the end of its lifetime
- The operational and maintenance cost is the annual cost of operating and maintaining the PV
- The salvage cost is the price at which you could expect to sell your PV at the end of the project, considering their remaining lifetime

#### IV.B.4. Wind turbines

The cost of the Wind Turbine is calculated with the following formula :

```latex
total cost = capital cost + (replacement cost - salvage cost) + operation & maintenance cost
```

where :

- The capital cost is the inital purchase price of the Wind Turbine
- The replacement cost is the cost of replacing the Wind Turbine at the end of its lifetime
- The operational and maintenance cost is the annual cost of operating and maintaining the Wind Turbine
- The salvage cost is the price at which you could expect to sell your Wind Turbine at the end of the project, considering their remaining lifetime

### IV.B.a) Total cost 💸

Ultimately, thanks to the 4 previous cost functions, we can compute the total cost of the project in dollars. This will be the first cost function that the optimizer will try to minimize.

### IV.B.b) CO2 emissions ♻️

The inputs into `costCarbon.py` module would be the same as the inputs into `dollarsCost.py` module. The output of the costCarbon.emissionCO2() function would be the average emission of CO2 (kgCO2e/h) across the entire project lifespan.

The value of the output (kgCO2e/h) depends on:

- The size of the generator
- The storage capacity of the battery
- The nominal power rating of the PV
- The dispatch strategy being used

The fixed parameters used in the function are:

- CO2 emission per litre of diesel fuel consumed = 2.65 kgCO2e/L
- Upstream factor for diesel generator = 1.2 (The upstream factor is taken into account for the entire lifecyle carbon footprint of the diesel generator)
- CO2 emission per manufacturing capacity of battery = 0.72 kgCO₂e/kWh
- CO2 emission footprint of PV = 6gCO2e/kWh

The carbon cost function will be the second function that our optimizer will aim at minimizing.

# V. Optimizer

The optimizer is based on pre-existing python modules. Given a set of cost functions to minimize, the optimizer returns the sizes of each component in order to minimize the cost functions in the mean time. For instance :

> I want to minimize the cost and the carbon dioxyde emissions. I have a limited number of disposable pVs and windmills, my dg cannot be bigger than x, but I have no limits regarding my battery. The optimizer will return the power specifications of each of the components so as to minimize the cost and the carbon dioxyde emissions.

We used the **plapytus** module. It's user friendly and does not need a lot of parameters. It was the perfect "black box" for this project.

The specific algorithm being used is the **NSGA-II** algorithm. It is a non-dominated sorted genetic algorithm. We tried this algorithm with different population sizes to compare the results. A graph is generated to show the set of feasible solutions resulting from the optimized variables (with both axis being the 2 objective functions to be minimized). From the graph, we are able to determine the pareto frontier, to show the possible trade-offs between the 2 objective functions.

## V.A. Cost functions

The two cost functions to minimize were `dollarCost` and `carbonCost` implemented in the simulator. These functions were passed as arguments to the platypus optimizer.

## V.B. Bounds and parameters

The parameters the optimizer iterated over were the **battery maximum storage capacity**, the **generator maximum output power** and the **solar pannels installed power**. Simply put: after each iteration, the optimizer changed these three values just a bit to see how it affected both the `dollarCost` and the `carbonCost`, in order to find the three values that could minimize both functions in the meantime. The optimimum is called a _Paretto Optimum_ (cf. Wikipedia on top of this document).

However, as we don't have unlimited ressources, we had to add lower and upper bounds to each of three variables (we can't have negative values nor infinite values).

Finally, here is how the problem definition looks :

```python
problem = Problem(3, 2)
problem.types[:] = [Real(constraints["battery"]["lowerBound"], constraints["battery"]["upperBound"]), Real(constraints["diesel"]["lowerBound"], constraints["diesel"]["upperBound"]), Real(constraints["photovoltaic"]["lowerBound"], constraints["photovoltaic"]["upperBound"])]
problem.function = costFunction # the function returns [dollarCost, carbonCost]

algorithm = NSGAII(problem) # NSGAII is the solver used to solve the optimization problem
algorithm.run(1)
```

# VI. Limits and extensions

## VI.A. Efficience

Unfortunately, the whole optimization process is **computationally expensive**. Indeed, after each iteration of the plytapus optimizer, the program has to compute the result of the _dispatching strategy_ (power output of the dg and battery storage during the whole) and then to iterate over multiple and long lists to compute the various costs (`dollarCost` and `carbonCost`).

With this configuration, for a 1-year simulation and a 25-year project, with 1 run of the optimizer, it takes **more than 1 minute** to compute and display the results.

## VI.B. One solver only

We only used the **NSGAII** solver provided by plytapus whereas the library offers many more solvers. We ought to try different solvers to compare their efficience.

## VI.C. User Interface

One possible extension for this project would be to code a friendly user interface with a web page served by a local server ran by Python (**Django** or **Flask** for instance). More precisely, there could be a web page coded with _html_, _css_ and _js_ where the user can enter and set the parameters for his simulation. The parameters could be sent to the local server running the Python code and would then dynamically render the results of the optimization in the web page.

# VII. Acknowledgements

Our work was frequently reviewed and guided by both our teachers **@CentraleSupélec**: _Nabil Sadou_ and _Pierre Haessig_.

# VIII. License

_This project is licensed under the terms of the CentraleSupélec license_.

Reproduction and modifications are allowed as long as there is a **mention** of either of the contributors or of this repository.

# IX. Contributors

- **Yun Bin Choh** - _Student @ CentraleSupélec_ - [lukecyb8687](https://github.com/lukecyb8687)
- **Paula Rayol** - _Student @ CentraleSupélec_ - [paularayol](https://github.com/paularayol)
- **Bastien Velitchkine** - _Student @ CentraleSupélec_ - [Bassvelitchkine](https://github.com/Bassvelitchkine)

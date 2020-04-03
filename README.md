Compiling of functions together, and running them under the simulator. Feed inputs and simulator function into the optimization function

The aim is to 1) Minimize the cost function (Total cost of PV+Battery+Generator)
              2) 2nd Objective Here
              
# Architecture
  - 📁 simulator
      - 📁 dispatching
          - 📑 dispatchingStrategyFunction.py
      - 📁 costs
          - 📑 totalCost.py (THE cost function that the optimizer will try to minimize)
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

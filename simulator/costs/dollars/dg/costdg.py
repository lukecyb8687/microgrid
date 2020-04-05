# -*- coding: utf-8 -*-

import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math
import requests

def costAnalysisDG(Pg,
                 N_years,
                 genNomPower,
                 fuelCost,
                 dgCapitalCost,
                 dgReplacementCost,
                 dgOMcost,
                 dgLifetime,
                 discountFactor,
                 fuelCostGrad,
                 fuelCostIntercept):
    
    N = N_years*8760 # Project Lifetime in hours

    def dg_lifetime(): 
        """
        Output:
        Number of operational hours of DG across entire project lifespan
        Number of operational hours per year: Array
        """
        #  Number of operational hours of DG across entire project lifespan

        countTotal = 0
        for i in range(len(Pg)): # Assuming res has (8760*N) elements (Total number of hours in a year * Number of years)
          if Pg[i] > 0:
            countTotal += 1
        dgLifetimeTotal = (countTotal)

        #  Number of operational hours per year: Array

        yearlyOpHour = []
        for elem in range(1,N_years+1):
          countYear = 0
          for i in range(8760*(elem-1),8760*elem):
            if Pg[i] > 0:
              countYear += 1
          yearlyOpHour.append(countYear)


        return dgLifetimeTotal, yearlyOpHour

    #print("The DG Lifetime would be:", (dg_lifetime()[0]/len(Pg))*N_years, "years when the Project lifetime would be", N_years,"years.")
    ##print("The DG Lifetime would be:", dg_lifetime()[0], "hours when the Project lifetime would be", N,"hours.")
    #print("The DG Replacement number would be: ", math.ceil(N/dgLifetime)-1)
    dgReplacementNumber = math.ceil(N/dgLifetime)-1


    def discount_factor(discountFactor,N):
      """
      Inputs:

      i: Real Discount Rate (%) Float
      N: Total Number of Project Hours

      Outputs:
      discountFactor : Array of discount factor wrt. year starting from year 0 to year N
      """
      discount = []
      for n in range(N+1):
        df = 1/((1+discountFactor/100)**n)
        discount.append(df)
      return discount

    def fuel_cost(Pg):
      """
      Input:
      Generator Output Power for the entire project lifespan (kW)

      Output:
      Total nominal fuel cost for each respective year of operation
      """

      yearlyFuelCost = []
      for elem in range(1,N_years+1):
        fuelConsumptionResult = [] #L/hr 
        for i in range(8760*(elem-1) , 8760*elem):
            if Pg[i] > 0.25*genNomPower:
                fCon = fuelCostGrad*Pg[i] + fuelCostIntercept
                fuelConsumptionResult.append(fCon)
        total_fuel_consumption = sum(fuelConsumptionResult)
        total_fuel_cost = fuelCost * total_fuel_consumption
        yearlyFuelCost.append(total_fuel_cost)
      
      return yearlyFuelCost

    def dg_replacement_cost_nominal():
        nomcost = []
        for n in range(1,1+dgReplacementNumber):
          nomcost.append(dgReplacementCost)
        return nomcost
        
    def dg_replacement_cost_discountfactor():
        dgReplacementCostDF = []
        dgLifetime_year = dgLifetime/8760

        for elem in range(1,dgReplacementNumber+1):
          dis = 1/((1+(discountFactor/100))**(dgLifetime_year*elem))
          dgReplacementCostDF.append(dis)

        return dgReplacementCostDF

    def dg_replacement_cost_discount(nomReplacementCost,replacementCostDF):
        costDiscount = np.multiply(nomReplacementCost, replacementCostDF)
        return costDiscount

    def dg_capital_cost():
        cost = dgCapitalCost*genNomPower
        return cost 

    def dg_OM_cost():
      yearlyOpHour = dg_lifetime()[1]
      omCostYearly = []
      for i in range(len(yearlyOpHour)):
          cost = yearlyOpHour[i]*genNomPower*dgOMcost
          omCostYearly.append(cost)
      return omCostYearly
          
    # Only appears at the end of the project cycle
    def dg_salvage_cost_nominal():
        replacementCostDuration = math.floor(N/dgLifetime) * dgLifetime
        remaining_lifetime = dgLifetime - (N -replacementCostDuration)
        salvageValueNominal = dgReplacementCost*(remaining_lifetime/dgLifetime)
        return salvageValueNominal

    def dg_salvage_cost_discount():
        dis = 1/((1+(discountFactor/100))**N_years)
        dgSalvageValueDiscount = dg_salvage_cost_nominal() * dis
        return dgSalvageValueDiscount

    # CAPITAL COST
    capitalCost = np.zeros(N_years+1)

    # OM COST
    omCost = np.zeros(N_years+1)
    replacementCost = np.zeros(N_years+1)

    # SALVAGE COST
    salvageCost = np.zeros(N_years+1)

    # FUEL COST
    fuelCostnom = np.zeros(N_years+1)

    # Yearly Generation kWh
    annualEnergy = np.ones(N_years+1)*8760*genNomPower

    # CONSTRUCTING DATA TABLE
    data = {'Year of Operation': list(range(0,N_years+1)),
            'Discount Factor': discount_factor(discountFactor,N_years),

            'Capital Cost Nominal':list(capitalCost),
            'Replacement Cost Nominal':np.zeros(N_years+1),
            'OM Cost Nominal':list(omCost),
            'Salvage Cost Nominal':list(salvageCost),
            'Fuel Cost Nominal':list(fuelCostnom),
            'Annual Electricity kWh': list(annualEnergy),
            'Total Nominal Cost':list(fuelCostnom)}

    cashFlowTable = pd.DataFrame.from_dict(data)

    column_list = list(cashFlowTable)
    column_list = column_list[2:7]
    column_list

    capitalCost[0] = -dg_capital_cost()
    omCost[1:N_years+1] = np.multiply(dg_OM_cost(),-1)
    salvageCost[N_years] = dg_salvage_cost_nominal()
    fuelCostnom[1:N_years+1] = np.multiply(fuel_cost(Pg),-1)


    cashFlowTable['Year of Operation'] =  list(range(0,N_years+1))
    cashFlowTable['Discount Factor'] =  discount_factor(discountFactor,N_years)
    cashFlowTable['Capital Cost Nominal'] =list(capitalCost)
    cashFlowTable['Replacement Cost Nominal'] = np.zeros(N_years+1)
    cashFlowTable['OM Cost Nominal'] = list(omCost)
    cashFlowTable['Salvage Cost Nominal'] = list(salvageCost)
    cashFlowTable['Fuel Cost Nominal'] = list(fuelCostnom)
    cashFlowTable['Annual Electricity kWh'] = list(annualEnergy)
    cashFlowTable['Total Nominal Cost'] = cashFlowTable[column_list].sum(axis=1)

    # REPLACEMENT COST
    yearOfReplacement = []

    for i in range(1,dgReplacementNumber+1):
      fac = dgLifetime/8760
      yr = math.floor(fac*i)
      yearOfReplacement.append(yr)
      
    a = dg_replacement_cost_nominal()
    b = dg_replacement_cost_discountfactor()
    replacementCosts = dg_replacement_cost_discount(a,b)

    for i in range(len(yearOfReplacement)):
      cashFlowTable['Replacement Cost Nominal'][yearOfReplacement[i]] = -replacementCosts[i]/cashFlowTable['Discount Factor'][i]

    # ADDING IN DISCOUNTED VALUES
    cashFlowTable['Capital Cost Discount'] = cashFlowTable['Capital Cost Nominal'] * cashFlowTable['Discount Factor']
    cashFlowTable['Replacement Cost Discount'] = cashFlowTable['Replacement Cost Nominal']* cashFlowTable['Discount Factor']
    cashFlowTable['OM Cost Discount'] = cashFlowTable['OM Cost Nominal'] * cashFlowTable['Discount Factor']
    cashFlowTable['Salvage Cost Discount'] = cashFlowTable['Salvage Cost Nominal'] * cashFlowTable['Discount Factor']
    cashFlowTable['Fuel Cost Discount'] = cashFlowTable['Fuel Cost Nominal'] * cashFlowTable['Discount Factor']
    cashFlowTable['Annual Electricity kWh Discount'] = cashFlowTable['Annual Electricity kWh'] * cashFlowTable['Discount Factor']
    cashFlowTable['Total Discounted Cost'] = cashFlowTable['Total Nominal Cost'] * cashFlowTable['Discount Factor']
    cashFlowTable['LCOE Annual'] = abs(cashFlowTable['Total Discounted Cost']) / cashFlowTable['Annual Electricity kWh Discount']
    for i in range(N_years+1):
       cashFlowTable['LCOE Annual'][i] = abs(sum(cashFlowTable['Total Discounted Cost'][0:i+1])) / sum(cashFlowTable['Annual Electricity kWh Discount'][0:i+1])




    return abs(sum(cashFlowTable['Total Discounted Cost']))


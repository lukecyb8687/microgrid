# -*- coding: utf-8 -*-

import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math
import requests

def pvCost(Ppv,
                 N_years,
                 pvNomPower,
                 pvCapitalCost,
                 pvReplacementCost,
                 pvOMcost,
                 pvLifetime,
                 discountFactor):
    
    N = N_years*8760 # Project Lifetime in hours

    def pv_lifetime(): 
        """
        Output:
        Number of operational hours of pv across entire project lifespan
        Number of operational hours per year: Array
        """
        #  Number of operational hours of pv across entire project lifespan

        countTotal = 0
        for i in range(len(Ppv)): # Assuming res has (8760*N) elements (Total number of hours in a year * Number of years)
          if Ppv[i] > 0:
            countTotal += 1
        pvLifetimeTotal = (countTotal)

        #  Number of operational hours per year: Array

        yearlyOpHour = []
        for elem in range(1,N_years+1):
          countYear = 0
          for i in range(8760*(elem-1),8760*elem):
            if Ppv[i] > 0:
              countYear += 1
          yearlyOpHour.append(countYear)


        return pvLifetimeTotal, yearlyOpHour

    #print("The pv Lifetime would be:", (pv_lifetime()[0]/len(Ppv))*N_years, "years when the Project lifetime would be", N_years,"years.")
    #print("The pv Lifetime would be:", pv_lifetime()[0], "hours when the Project lifetime would be", N,"hours.")
    #print("The pv Replacement number would be: ", math.ceil(N/pvLifetime)-1)
    pvReplacementNumber = math.ceil(N/pvLifetime)-1


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


    def pv_replacement_cost_nominal():
        nomcost = []
        for n in range(1,1+pvReplacementNumber):
          nomcost.append(pvReplacementCost)
        return nomcost
        
    def pv_replacement_cost_discountfactor():
        pvReplacementCostDF = []
        pvLifetime_year = pvLifetime/8760

        for elem in range(1,pvReplacementNumber+1):
          dis = 1/((1+(discountFactor/100))**(pvLifetime_year*elem))
          pvReplacementCostDF.append(dis)

        return pvReplacementCostDF

    def pv_replacement_cost_discount(nomReplacementCost,replacementCostDF):
        costDiscount = np.multiply(nomReplacementCost, replacementCostDF)
        return costDiscount

    def pv_capital_cost():
        cost = pvCapitalCost*pvNomPower
        return cost 

    def pv_OM_cost():
      yearlyOpHour = pv_lifetime()[1]
      omCostYearly = []
      for i in range(len(yearlyOpHour)):
          cost = yearlyOpHour[i]*pvNomPower*pvOMcost
          omCostYearly.append(cost)
      return omCostYearly
          
    # Only appears at the end of the project cycle
    def pv_salvage_cost_nominal():
        replacementCostDuration = math.floor(N/pvLifetime) * pvLifetime
        remaining_lifetime = pvLifetime - (N -replacementCostDuration)
        salvageValueNominal = pvReplacementCost*(remaining_lifetime/pvLifetime)
        return salvageValueNominal

    def pv_salvage_cost_discount():
        dis = 1/((1+(discountFactor/100))**N_years)
        pvSalvageValueDiscount = pv_salvage_cost_nominal() * dis
        return pvSalvageValueDiscount

    # CAPITAL COST
    capitalCost = np.zeros(N_years+1)

    # OM COST
    omCost = np.zeros(N_years+1)
    replacementCost = np.zeros(N_years+1)

    # SALVAGE COST
    salvageCost = np.zeros(N_years+1)


    # Yearly generation kWh
    annualEnergy = np.ones(N_years+1)*8760*pvNomPower

    # CONSTRUCTING DATA TABLE
    data = {'Year of Operation': list(range(0,N_years+1)),
            'Discount Factor': discount_factor(discountFactor,N_years),

            'Capital Cost Nominal':list(capitalCost),
            'Replacement Cost Nominal':np.zeros(N_years+1),
            'OM Cost Nominal':list(omCost),
            'Salvage Cost Nominal':list(salvageCost),
            'Annual Electricity kWh': list(annualEnergy),
            'Total Nominal Cost':list(salvageCost)}

    cashFlowTable = pd.DataFrame.from_dict(data)

    column_list = list(cashFlowTable)
    column_list = column_list[2:6]
    column_list

    capitalCost[0] = -pv_capital_cost()
    omCost[1:N_years+1] = np.multiply(pv_OM_cost(),-1)
    salvageCost[N_years] = pv_salvage_cost_nominal()


    cashFlowTable['Year of Operation'] =  list(range(0,N_years+1))
    cashFlowTable['Discount Factor'] =  discount_factor(discountFactor,N_years)
    cashFlowTable['Capital Cost Nominal'] =list(capitalCost)
    cashFlowTable['Replacement Cost Nominal'] = np.zeros(N_years+1)
    cashFlowTable['OM Cost Nominal'] = list(omCost)
    cashFlowTable['Salvage Cost Nominal'] = list(salvageCost)
    cashFlowTable['Annual Electricity kWh'] = list(annualEnergy)
    cashFlowTable['Total Nominal Cost'] = cashFlowTable[column_list].sum(axis=1)

    # REPLACEMENT COST
    yearOfReplacement = []

    for i in range(1,pvReplacementNumber+1):
      fac = pvLifetime/8760
      yr = math.floor(fac*i)
      yearOfReplacement.append(yr)
      
    a = pv_replacement_cost_nominal()
    b = pv_replacement_cost_discountfactor()
    replacementCosts = pv_replacement_cost_discount(a,b)

    for i in range(len(yearOfReplacement)):
      cashFlowTable['Replacement Cost Nominal'][yearOfReplacement[i]] = -replacementCosts[i]/cashFlowTable['Discount Factor'][i]

    # ADDING IN DISCOUNTED VALUES
    cashFlowTable['Capital Cost Discount'] = cashFlowTable['Capital Cost Nominal'] * cashFlowTable['Discount Factor']
    cashFlowTable['Replacement Cost Discount'] = cashFlowTable['Replacement Cost Nominal']* cashFlowTable['Discount Factor']
    cashFlowTable['OM Cost Discount'] = cashFlowTable['OM Cost Nominal'] * cashFlowTable['Discount Factor']
    cashFlowTable['Salvage Cost Discount'] = cashFlowTable['Salvage Cost Nominal'] * cashFlowTable['Discount Factor']
    cashFlowTable['Annual Electricity kWh Discount'] = cashFlowTable['Annual Electricity kWh'] * cashFlowTable['Discount Factor']
    cashFlowTable['Total Discounted Cost'] = cashFlowTable['Total Nominal Cost'] * cashFlowTable['Discount Factor']
    cashFlowTable['LCOE Annual'] = abs(cashFlowTable['Total Discounted Cost']) / cashFlowTable['Annual Electricity kWh Discount']
    for i in range(N_years+1):
       cashFlowTable['LCOE Annual'][i] = abs(sum(cashFlowTable['Total Discounted Cost'][0:i+1])) / sum(cashFlowTable['Annual Electricity kWh Discount'][0:i+1])




    return abs(sum(cashFlowTable['Total Discounted Cost']))


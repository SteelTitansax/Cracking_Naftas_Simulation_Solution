#Libraries
import logging
import azure.functions as func
import json
import numpy as np
from scipy.integrate import solve_ivp


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Reactor designing Begins...')
        
    try:
        req_body = req.get_json()
    except ValueError:
        pass
    else:
        production = req_body.get('production') # petrol barrels per day
        production = float(production)
        V0 = production * 0.006624470622 # m3/h
        density = 0.715 #g/cm3

        massic_flow_0 = V0  * density * 100**3 #g/h
        D = req_body.get('D') #m

        #      res , vgo , des , naf , gas
        y1 = req_body.get('y1') # initial non-processed petrol composition
        y2 = req_body.get('y2') # initial non-processed petrol composition
        y3 = req_body.get('y3') # initial non-processed petrol composition
        y4 = req_body.get('y4') # initial non-processed petrol composition
        y5 = req_body.get('y5') # initial non-processed petrol composition

        # Parsing input data

        D = float(D)
        y1 = float(y1)
        y2 = float(y2)
        y3 = float(y3)
        y4 = float(y4)
        y5 = float(y5)        


        y0 = [y1,y2,y3,y4,y5] # initial non-processed petrol composition


        k1 = 0.147
        k2 = 0.022
        k3 = 0.020
        k4 = 0.098
        k5 = 0.057
        k6 = 0.007
        k7 = 0
        k8 = 0.003
        k9 = 0
        k10 = 0

        V_init = 0
        V_final = 500

        def reactionSystem(V,y):
            y1 = y[0]
            y2 = y[1]
            y3 = y[2]
            y4 = y[3]

            dyWastes = (-k1*y1-k2*y1-k3*y1-k4*y1)/V0
            dyVGO = (k1*y1-k5*y2-k6*y2-k7*y2)/V0
            dyDistilled = (k2*y1+k5*y2-k8*y3-k9*y3)/V0
            dyNaftas = (k3*y1+k6*y2-k8*y3-k10*y4)/V0
            dyGases = (k4*y1+k7*y2+k9*y3+k10*y4)/V0

            return np.array([dyWastes, dyVGO,dyDistilled,dyNaftas,dyGases])


        sol = solve_ivp(reactionSystem, (V_init,V_final),y0)

        # Consolidating outputs: 
        dyWastes = sol.y[0]
        dyVGO = sol.y[1]
        dyDistilled = sol.y[2]
        dyNaftas = sol.y[3]
        dyGases = sol.y[4]
        t = sol.t

        sol_json = []

        for item in range(5):

            sol_details = {
                        "dyWastes": dyWastes[item],
                        "dyVGO": dyVGO[item],
                        "dyDistilled": dyDistilled[item],
                        "dyNaftas": dyNaftas[item],
                        "dyGases": dyGases[item],
                        "t": t[item]
                    }

            sol_json.append(sol_details)

        logging.info(sol_json)

        return json.dumps(sol_json)
    
    return func.HttpResponse("Reactor design succesfully...",status_code=200)


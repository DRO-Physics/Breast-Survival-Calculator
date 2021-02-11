import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sksurv.linear_model import CoxPHSurvivalAnalysis, CoxnetSurvivalAnalysis
from scipy import interpolate
from pysurvival.utils import load_model
import time

def ErrorMessage(msg):
    return msg

class Survival_Calculator:
    def __init__(self, age, T, N, M1, grade, ER, PR, Her2, Invasion, size, nodes):
        self.params = [age, T, N, M1, grade, ER, PR, Her2, Invasion, size, nodes]
        size_mean  = 2.508002588438309
        size_std   = 1.9174335908941977
        nodes_mean = 2.073339085418464
        nodes_std  = 4.974504989897188
        age_mean   = 55.09167385677308
        age_std    = 11.580932517493356

        age  = (age - age_mean) / age_std
        size = (size - size_mean) / size_std
        nodes = (nodes - nodes_mean) / nodes_std

        T1, T2, T3, T4 = 0, 0, 0, 0
        N1, N2, N3 = 0, 0, 0
        grade1, grade2, grade3 = 0, 0, 0

        if T == 1:
            T1 = 1
        elif T == 2:
            T2 = 1
        elif T == 3:
            T3 =1
        elif T== 4:
            T4 = 1
        elif T == 0:
            pass
        else:
            ErrorMessage('Invalid T Stage')

        if N == 1:
            N1 = 1
        elif N == 2:
            N2 = 1
        elif N == 3:
            N3 =1
        elif N == 0:
            pass
        else:
            ErrorMessage('Invalid N Stage')

        if grade == 2:
            grade2 = 1
        elif grade == 3:
            grade3 =1
        elif grade == 1:
            pass
        else:
            ErrorMessage('Invalid N Stage')

        x = np.array([[age, T1, T2, T3, T4, N1, N2, N3, M1, grade2, grade3, ER, PR, Her2,
             Invasion, size, nodes]]) ## Full Variables
        x = np.array([[age, T1, T2, T3, T4, N1, N2, N3, M1, grade2, grade3, ER, PR, Her2,
             Invasion]])
        self.results = self._CalculateSurvivalFunction_pysurvival(x)

    def _CalculateSurvivalFunction_sksurv(self, x):
        ## Read in models
        models = []
        with open("models_CSS.pckl", "rb") as f:
            while True:
                try:
                    models.append(pickle.load(f))
                except EOFError:
                    break
        ## Calculate Survival functions
        time = np.linspace(12,120, 120)
        s_arr = []
        for model in models:
            s = model.predict_survival_function(x)[0]
            f = interpolate.interp1d(s.x, s.y)
            s_arr.append(f(time))
        s_arr_mean = np.mean(s_arr, axis=0)
        s_arr_std = np.std(s_arr, axis=0)
        self._PlotFigure(s_arr_mean, s_arr_std, x, time)
        return {'time': time, 's_mean':s_arr_mean, 's_std':s_arr_std}

    def _CalculateSurvivalFunction_pysurvival(self, x):
        ## Read in models
        startTime = time.time()
        models = [load_model('./OS_Final_model/DeepSurv' + str(k+1) + '.zip') for k in range(50)]

        ## Calculate Survival functions
        t = np.linspace(12,120, 240)
        s_arr = []
        for model in models:
            s = model.predict_survival(x)[0]
            f = interpolate.interp1d(model.times, s)
            s_arr.append(f(t))
        s_arr_mean = np.mean(s_arr, axis=0)
        s_arr_std = np.std(s_arr, axis=0)
        endTime = time.time()
        print('Total Time = %f seconds' %(endTime-startTime))
        # self._PlotFigure(s_arr_mean, s_arr_std, x, t)
        return {'time': t, 's_mean':s_arr_mean, 's_std':s_arr_std, 'runtime': endTime-startTime}

    def _PlotFigure(self, s_mean, s_std, x, time):
        ## Plot KM curve
        from lifelines import CoxPHFitter, KaplanMeierFitter
        fname = 'Data_Clinical_Encoded.csv'
        df = pd.read_csv(fname)
        df.dropna(axis=0, inplace=True)
        df['event'] = 1-(df['Count_as_OS'] == 'N')
        print(df.head(5))
        age_bool = (df['Age_@_Dx'] > self.params[0]-7) & (df['Age_@_Dx'] < self.params[0]+7)
        T_bool = (df['T' + str(self.params[1])] == 1)
        N_bool = (df['N' + str(self.params[2])] == 1)
        M_bool = (df['M' + str(self.params[3])] == 1)
        grade_bool = (df['Grade' + str(self.params[4])] == 1)
        ER_bool = (df['ER'] == self.params[5])
        PR_bool = (df['PR'] == self.params[6])
        HER2_bool = (df['Her2'] == self.params[7])
        invade_bool = (df['Invasion'] == self.params[8])
        size_bool = (df['size_precise'] > self.params[9]-5) & (df['size_precise'] < self.params[9]+5)
        nodes_bool = (df['nodespos'] > self.params[10]-5) & (df['nodespos'] < self.params[10]+5)
        df_subset = df[age_bool & T_bool & N_bool & M_bool & grade_bool
                    & ER_bool & PR_bool & HER2_bool & invade_bool]
        print(len(df_subset), len(df))
        kmf = KaplanMeierFitter()
        kmf.fit(df_subset['Time_OS'], df_subset['event'], label="Train")
        kmf.plot_survival_function(show_censors=False, ci_show=True, at_risk_counts=True)
        titleString ='Age=' + str(self.params[0]) + ', T' + str(self.params[1]) + ', N'\
            + str(self.params[2]) + ', M' + str(self.params[3]) + ', Grade' +  str(self.params[4])\
            + ', ER=' + str(self.params[5]) + ', PR=' + str(self.params[6]) + ', Her2=' + str(self.params[7])\
            + ', Invasion=' + str(self.params[8])
        plt.title(titleString)
        plt.plot(time, s_mean, 'r-', label='DeepSurv')
        plt.fill_between(time, s_mean-s_std,  s_mean+s_std, alpha=0.4)
        plt.legend()
        plt.tight_layout()
        plt.savefig('survival_comparison')
        plt.show()


if __name__ == '__main__':
    Survival_Calculator(55, 2, 0, 0, 3, 1, 1, 0, 0, 2.0, 0)

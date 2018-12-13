import pandas as pd
import numpy as np
import datetime as dt
from scipy.linalg import expm
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pdb

data = pd.read_excel(io = 'Вариант4.xls', sheet_name='ratings')
data['date'] = pd.to_datetime(data['date'], format='yyyy-dd-mm')

 #['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'D']

def build_migration_matrix(start_date, end_date):
    """
    Функция строит матрицу переходов когортным методов для данных типа data, начиная с start_date и заканчивая end_date
    """
    
    transition_matrix = pd.DataFrame(data=np.zeros([9, 9]),
                                     columns = ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'D'],
                                     index = ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'D'])
    starts = pd.DataFrame(data=np.zeros([1, 9]),
                          columns = ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'D'],
                          index = ['starts'])
    data_slice = data[(data.date >= start_date) & (data.date <= end_date + dt.timedelta(1))]
    

    objects = list(set(data_slice.object))
    
    for object_id in objects:
 
        object_data = data_slice[data_slice.object == object_id].sort_values('date')
            
        if object_data.iloc[0].date != start_date:
            continue
    
        if len(set([3, 4]).intersection(object_data.type)) != 0:
            continue

        if object_data.iloc[0].rating == 'D':
            continue
        
        if (object_data.iloc[0].rating == 'WD') | (object_data.iloc[-1].rating == 'WD'):
            continue
  
        starts[object_data.iloc[0].rating] += 1
 
        if len(set(object_data.rating)) == 1:
            transition_matrix[object_data.iloc[0].rating][object_data.iloc[0].rating] += 1
            continue
 
        if set(['D']).issubset(set(object_data.rating)) == True:
            transition_matrix['D'][object_data.iloc[0].rating] += 1
            continue
 
        start_rating = object_data.iloc[0].rating
        end_rating = object_data.iloc[-1].rating
 
        transition_matrix[end_rating][start_rating] += 1
    
    transition_matrix.columns = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'D']
    transition_matrix.index = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'D']
        
    return transition_matrix

def build_transition_probability_matrix(migration_matrix):
    """Функция строит вероятностную матрицу из матрицы миграций и стартового вектора"""
    
    matrix = (np.matrix(migration_matrix).T / np.array(migration_matrix.sum(axis = 1))).T
    matrix[-1] = np.zeros(9)
    
    return pd.DataFrame(data=matrix,
                        columns = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'D'],
                        index = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'D'])

def build_duration_migration_matrix(start_date, end_date):
    '''Функция строит матрицу миграций методом дюраций для указанного периода'''
    
    frequencies_matrix = pd.DataFrame(data=np.zeros([9, 9]),
                                      columns = ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'D'],
                                      index = ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'D'])
        
    data_slice = data[(data.date >= start_date) & (data.date <= end_date + dt.timedelta(1))]
    
    objects = data_slice.object.unique()
    
    window = end_date + dt.timedelta(1) - start_date
    
    for object_id in objects:
        
        object_data = data_slice[data_slice.object == object_id].sort_values('date')
    
        for i in range(1, object_data.shape[0]):
            
            old_rating = object_data.rating.iloc[i - 1]
            new_rating = object_data.rating.iloc[i]
        
            old_date = object_data.date.iloc[i - 1]
            new_date = object_data.date.iloc[i]
            
            if (old_rating == 'D') | (old_rating == 'WD'):
                continue
                    
            if (new_rating == 'WD'):
                frequencies_matrix[old_rating][old_rating] += ((new_date - old_date) / window)
                continue
                            
            if old_rating == new_rating:
                frequencies_matrix[old_rating][old_rating] += ((new_date - old_date) / window)
                continue
                                    
            frequencies_matrix[new_rating][old_rating] += 1
            frequencies_matrix[old_rating][old_rating] += ((new_date - old_date) / window)
            
    frequencies_matrix.columns = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'D']
    frequencies_matrix.index = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'D']

    return frequencies_matrix

def build_generator_matrix(duration_migration_matrix):
    """Функция строит genrator matrix для матрицы миграций, полученной методом дюраций"""
    generator_matrix = (duration_migration_matrix.T / np.diag(duration_migration_matrix).T).T
    
    for i in range(generator_matrix.shape[0]):
        generator_matrix.iloc[i, i] = 0
    
    sums = generator_matrix.sum(axis = 1)
    
    for i in range(generator_matrix.shape[0]):
        generator_matrix.iloc[i, i] = - sums.iloc[i]
    
    generator_matrix.iloc[-1] = 0
    
    return generator_matrix

def build_matrix_exponential(generator_matrix):
    """Функция строит matrix exponential для generator_matrix"""
    matrix_exp = pd.DataFrame(data = expm(np.matrix(generator_matrix)),
                              columns = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'D'],
                              index = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'D'])
    matrix_exp['D']['D'] = 0
    return matrix_exp

class CAP_curve:
    
    def __init__(self, migration_matrix):
        self.migration_matrix = migration_matrix
        self.default_rates = migration_matrix['D'][::-1].cumsum()/migration_matrix['D'].sum()
        self.observation_rates = migration_matrix.sum(axis=1)[::-1].cumsum()/migration_matrix.sum(axis=1).sum()
        
    def AUC(self):
        sums_of_bases = np.array(self.default_rates)[:-1] + np.array(self.default_rates)[1:]
        heights = np.diff(np.array(self.observation_rates))
        return ((sums_of_bases / 2) * heights).sum()
    
    def __str__(self):
        return 'AUC-CAP: %s' % np.round(self.AUC(), 3)
    
    def ideal_AUC(self):
        return (1 - self.migration_matrix['D'].sum()/self.migration_matrix.sum().sum() + 1)/2 
    
    def AR(self):
        return (self.AUC()-0.5)/(self.ideal_AUC()-0.5)
        
def plot_CAP(CAP_curve):
    
    f = plt.figure(figsize=(10, 5))
    plt.title('CAP Curve')
    plt.xlabel('Observation Ratio') 
    plt.ylabel('Defaulters Ratio') 
    
    random_x = np.linspace(0,1,2)
    random_y = np.linspace(0,1,2)

    ideal_x = np.array([0, CAP_curve.migration_matrix['D'].sum()/CAP_curve.migration_matrix.sum().sum(), 1])
    ideal_y = np.array([0, 1, 1])
    
    plt.plot(random_x, random_y, color='b')
    plt.plot(ideal_x, ideal_y, color='r')
    plt.plot(CAP_curve.observation_rates, CAP_curve.default_rates, color='g')
           
    blue_patch = mpatches.Patch(color='blue', label='random model')
    red_patch = mpatches.Patch(color='red', label='best model')
    green_patch = mpatches.Patch(color='green', label='our model')
    
    plt.legend(handles=[red_patch, green_patch, blue_patch])
    
    plt.annotate(str(np.round(CAP_curve.migration_matrix['D'].sum()/CAP_curve.migration_matrix.sum().sum(), 3)), 
                 (CAP_curve.migration_matrix['D'].sum()/CAP_curve.migration_matrix.sum().sum(), 1),
                (CAP_curve.migration_matrix['D'].sum()/CAP_curve.migration_matrix.sum().sum()+0.05, 0.92), size=15);
    print(CAP_curve)
    print('AR: %s' % np.round(CAP_curve.AR(), 3))
    
class ROC_curve:
    
    def __init__(self, migration_matrix):
        
        self.migration_matrix = migration_matrix
        
        self.defaults = migration_matrix['D'][:-1]
        self.survived = migration_matrix.sum(axis=1)[:-1] - migration_matrix['D'][:-1]
        
        self.TP = np.array(self.survived.cumsum())
        self.FN = self.survived.sum() - self.TP
        self.TPR = np.append(0, self.TP / (self.TP + self.FN))
    
        self.FP = self.defaults.cumsum()
        self.TN = self.defaults.sum() - self.FP
        self.FPR = np.append(0, self.FP / (self.FP + self.TN)) 
        
    def AUC(self):
        sums_of_bases = np.array(self.TPR)[:-1] + np.array(self.TPR)[1:]
        heights = np.diff(np.array(self.FPR))
        return ((sums_of_bases / 2) * heights).sum()
    
    def __str__(self):
        return 'AUC-ROC: %s' % np.round(self.AUC(), 3)
    
    def AR(self):
        return (self.AUC()-0.5)/0.5
        
def plot_ROC(ROC_curve):
    
    import matplotlib.patches as mpatches
    
    f = plt.figure(figsize=(10, 5))
    plt.title('ROC Curve')
    plt.xlabel('FPR') 
    plt.ylabel('TPR') 
    
    random_x = np.linspace(0,1,10)
    random_y = np.linspace(0,1,10)
    
    ideal_x = np.array([0, 0, 1])
    ideal_y = np.array([0, 1, 1])
    
    plt.plot(random_x, random_y, color='b')
    plt.plot(ideal_x, ideal_y, color='r')
    plt.plot(ROC_curve.FPR, ROC_curve.TPR, color='g')
           
    blue_patch = mpatches.Patch(color='blue', label='random model')
    red_patch = mpatches.Patch(color='red', label='ideal model')
    green_patch = mpatches.Patch(color='green', label='our model')
    
    plt.legend(handles=[red_patch, green_patch, blue_patch]);
    print(ROC_curve)
    print('AR: %s' % np.round(ROC_curve.AR(), 3))

rates_data = pd.read_excel('Вариант4.xls', sheet_name='rf_rate')
rf_rates = np.array(rates_data.rf_rate)

bond_data = pd.read_excel('Вариант4.xls', sheet_name='bonds')
spread_data = pd.read_excel('Task_6_AV.xlsx', sheet_name='Rating-spread Data')

    
class bond():
    
    def __init__(self, bond_type, maturity, coupon_rate, frequency = 2):
        
        self.type = bond_type
        self.maturity = maturity
        self.coupon_rate = coupon_rate
        self.frequency = frequency
        
        self.dates = np.cumsum((np.ones(int(maturity*frequency)) * 0.5))
        
        if bond_type == 1:
            self.interest = np.zeros(int(maturity*frequency))
            self.principal = np.zeros(int(maturity*frequency))
            self.principal[-1] = 100
            self.face_value = np.ones(int(maturity*frequency)) * 100 - self.principal
            
            self.payments = self.interest + self.principal
            
        elif bond_type == 2:            
            self.interest = np.ones(int(maturity*frequency)) * coupon_rate
            self.principal = np.zeros(int(maturity*frequency))
            self.principal[-1] += 100
            self.face_value = np.ones(int(maturity*frequency)) * 100 - self.principal
            
            self.payments = self.interest + self.principal
            
        elif bond_type == 3:
            self.principal = np.ones(int(maturity*frequency)) * 100 / (maturity*frequency)
            self.face_value = np.cumsum(self.principal)[::-1]
            self.interest = self.face_value * coupon_rate / 100
            
            self.payments = self.interest + self.principal
                    
    def dcf(self, rates_curve, spread):
        
        rates = rates_curve + np.ones(len(rates_curve)) * spread
        rates = rates[:len(self.dates)]
        
        return self.payments * np.exp(-rates/100 * self.dates)
    
    def default_value(self, LGD = 0.4, horizon = False):
        
        if self.type == 3:
            return self.face_value[:horizon * self.frequency].mean() * LGD
        else:
            return LGD * self.face_value[-1]
            
            
class future_bond(bond):
    
    def __init__(self, bond, horizon):
        self.dates = bond.dates[:-horizon * bond.frequency]
        
        self.type = bond.type
        self.maturity = bond.maturity
        self.coupon_rate = bond.coupon_rate
        self.frequency = bond.frequency
        
        self.interest = bond.interest[horizon * bond.frequency:]
        self.principal = bond.principal[horizon * bond.frequency:]
        self.payments = bond.payments[horizon * bond.frequency:]
        self.face_value = bond.face_value[horizon * bond.frequency:]
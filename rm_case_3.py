import pandas as pd
import numpy as np
import datetime as dt
from scipy.linalg import expm
import pdb

data = pd.read_excel(io = 'Вариант4.xls', sheet_name='ratings')
data['date'] = pd.to_datetime(data['date'], format='yyyy-dd-mm')

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
    pdb.set_trace()

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

    return starts, transition_matrix

def build_transition_probability_matrix(migration_matrix, start_vector):
    """Функция строит вероятностную матрицу из матрицы миграций и стартового вектора"""
    
    matrix = (np.matrix(migration_matrix).T / np.array(start_vector)).T
    matrix[-1] = np.zeros(9)
    
    return pd.DataFrame(data=matrix,
                        columns = ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'D'],
                        index = ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'D'])

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
    return pd.DataFrame(data = expm(np.matrix(generator_matrix)),
                        columns = ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'D'],
                        index = ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'D'])

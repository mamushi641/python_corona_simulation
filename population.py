'''
this file contains functions that help initialize the population
parameters for the simulation
'''

from glob import glob
import os

import numpy as np

from motion import get_motion_parameters
from utils import check_folder

class population():
    def __init__(self,Config,mean_age=45, max_age=105,
                          xbounds=[0, 1], ybounds=[0, 1]):
        self.population = np.zeros((Config.pop_size, 15))
        # initalize unique IDs
        self.population[:, 0] = [x for x in range(Config.pop_size)]

        # initialize random coordinates
        self.population[:, 1] = np.random.uniform(low=xbounds[0] + 0.05, high=xbounds[1] - 0.05,
                                             size=(Config.pop_size,))
        self.population[:, 2] = np.random.uniform(low=ybounds[0] + 0.05, high=ybounds[1] - 0.05,
                                             size=(Config.pop_size,))

        # initialize random headings -1 to 1
        self.population[:, 3] = np.random.normal(loc=0, scale=1 / 3,
                                            size=(Config.pop_size,))
        self.population[:, 4] = np.random.normal(loc=0, scale=1 / 3,
                                            size=(Config.pop_size,))

        # initialize random speeds
        self.population[:, 5] = np.random.normal(Config.speed, Config.speed / 3)

        # initalize ages
        self.std_age = (max_age - mean_age) / 3
        self.population[:, 7] = np.int32(np.random.normal(loc=mean_age,
                                                     scale=self.std_age,
                                                     size=(Config.pop_size,)))

        self.population[:, 7] = np.clip(population[:, 7], a_min=0,
                                   a_max=max_age)  # clip those younger than 0 years

        # build recovery_vector
        self.population[:, 9] = np.random.normal(loc=0.5, scale=0.5 / 3, size=(Config.pop_size,))



def initialize_destination_matrix(pop_size, total_destinations):
    '''intializes the destination matrix

    function that initializes the destination matrix used to
    define individual location and roam zones for population members

    Keyword arguments
    -----------------
    pop_size : int
        the size of the population

    total_destinations : int
        the number of destinations to maintain in the matrix. Set to more than
        one if for example people can go to work, supermarket, home, etc.
    '''

    destinations = np.zeros((pop_size, total_destinations * 2))

    return destinations


def set_destination_bounds(population, destinations, xmin, ymin, 
                           xmax, ymax, dest_no=1, teleport=True):
    '''teleports all persons within limits

    Function that takes the population and coordinates,
    teleports everyone there, sets destination active and
    destination as reached

    Keyword arguments
    -----------------
    population : ndarray
        the array containing all the population information

    destinations : ndarray
        the array containing all the destination information

    xmin, ymin, xmax, ymax : int or float
        define the bounds on both axes where the individual can roam within
        after reaching the defined area

    dest_no : int
        the destination number to set as active (if more than one)

    teleport : bool
        whether to instantly teleport individuals to the defined locations
    '''

    #teleport
    if teleport:
        population[:,1] = np.random.uniform(low = xmin, high = xmax, size = len(population))
        population[:,2] = np.random.uniform(low = ymin, high = ymax, size = len(population))

    #get parameters
    x_center, y_center, x_wander, y_wander = get_motion_parameters(xmin, ymin, 
                                                                   xmax, ymax)

    #set destination centers
    destinations[:,(dest_no - 1) * 2] = x_center
    destinations[:,((dest_no - 1) * 2) + 1] = y_center

    #set wander bounds
    population[:,13] = x_wander
    population[:,14] = y_wander

    population[:,11] = dest_no #set destination active
    population[:,12] = 1 #set destination reached

    return population, destinations


def save_data(population, pop_tracker):
    '''dumps simulation data to disk

    Function that dumps the simulation data to specific files on the disk.
    Saves final state of the population matrix, the array of infected over time,
    and the array of fatalities over time

    Keyword arguments
    -----------------
    population : ndarray
        the array containing all the population information

    infected : list or ndarray
        the array containing data of infections over time

    fatalities : list or ndarray
        the array containing data of fatalities over time
    ''' 
    num_files = len(glob('data/*'))
    check_folder('data/%i' %num_files)
    np.save('data/%i/population.npy' %num_files, population)
    np.save('data/%i/infected.npy' %num_files, pop_tracker.infectious)
    np.save('data/%i/recovered.npy' %num_files, pop_tracker.recovered)
    np.save('data/%i/fatalities.npy' %num_files, pop_tracker.fatalities)


def save_population(population, tstep=0, folder='data_tstep'):
    '''dumps population data at given timestep to disk

    Function that dumps the simulation data to specific files on the disk.
    Saves final state of the population matrix, the array of infected over time,
    and the array of fatalities over time

    Keyword arguments
    -----------------
    population : ndarray
        the array containing all the population information

    tstep : int
        the timestep that will be saved
    ''' 
    check_folder('%s/' %(folder))
    np.save('%s/population_%i.npy' %(folder, tstep), population)


class Population_trackers():
    '''class used to track population parameters

    Can track population parameters over time that can then be used
    to compute statistics or to visualise. 

    TODO: track age cohorts here as well
    '''
    def __init__(self):
        self.susceptible = []
        self.infectious = []
        self.recovered = []
        self.fatalities = []

        #PLACEHOLDER - whether recovered individual can be reinfected
        self.reinfect = False 

    def update_counts(self, population):
        '''docstring
        '''
        pop_size = population.shape[0]
        self.infectious.append(len(population[population[:,6] == 1]))
        self.recovered.append(len(population[population[:,6] == 2]))
        self.fatalities.append(len(population[population[:,6] == 3]))

        if self.reinfect:
            self.susceptible.append(pop_size - (self.infectious[-1] +
                                                self.fatalities[-1]))
        else:
            self.susceptible.append(pop_size - (self.infectious[-1] +
                                                self.recovered[-1] +
                                                self.fatalities[-1]))

import numpy as np
import scipy as sp
from scipy.optimize import fsolve, minimize, root_scalar
import matplotlib.pyplot as plt

# Constants
e0 = 8.85e-12
u0 = np.pi * 4e-7

class CPW:
    def __init__ (self, w, s, h, er):
        self.w, self.s, self.h = w, s, h
        self.er = er
        self.width = w + 2*s
        self.k = w / (w + 2*s)
        self.k_prime = np.sqrt(1 - self.k**2)

        self.er_eff = self.effective_permittivity(w, s)
        self.Cl = self.capacitance_per_length(w,s)
        self.Ll = self.inductance_per_length()
    
    def get_k(self, w, s):
        return w / (w + 2*s)
    
    def get_k_prime(self, w, s):
        return np.sqrt(1 - self.get_k(w,s)**2)
    
    def effective_permittivity(self, w, s):
        self.er_eff = (self.er + 1)/2 * (np.tanh(1.785*np.log(self.h/s) + 1.75) + self.get_k(w,s) * s / self.h *(0.04 - 0.7*self.get_k(w,s) + 0.01*(1-self.er/10)*(0.25 + self.get_k(w,s))))
        return self.er_eff
    
    def K(self, k):
        K = sp.integrate.quad(lambda t: 1 / np.sqrt( (1 - t**2) * (1 - (k*t)**2) ), 0, 1)
        if (K[1] > 0.01*K[0]):
            print("Integration Failed")
            return
        return sp.integrate.quad(lambda t: 1 / np.sqrt( (1 - t**2) * (1 - (k*t)**2) ), 0, 1)[0]

    def impedance(self, w=None, s=None):
        if w or s:
            return 30 * np.pi / np.sqrt(self.effective_permittivity(w,s)) * self.K(self.get_k_prime(w, s)) / self.K(self.get_k(w,s))
        else:
            return 30 * np.pi / np.sqrt(self.effective_permittivity(self.w,self.s)) * self.K(self.get_k_prime(self.w, self.s)) / self.K(self.get_k(self.w,self.s))
    
    def phase_velocity(self, w=None, s=None):
        if w or s:
            return 1 / np.sqrt(self.capacitance_per_length(w,s) * self.inductance_per_length(w,s))
        else:
            return 1 / np.sqrt(self.Cl * self.Ll)
    
    def capacitance_per_length(self, w=None, s=None):
        if w or s:
            return 4 * e0 * self.effective_permittivity(w,s) * self.K(self.get_k(w,s)) / self.K(self.get_k_prime(w,s))
        else:
            return 4 * e0 * self.er_eff * self.K(self.k) / self.K(self.k_prime)
    
    def inductance_per_length(self, w=None, s=None):
        if w or s:
            return u0 / 4 * self.K(self.get_k_prime(w,s)) / self.K(self.get_k(w,s))
        else:
            return u0 / 4 * self.K(self.k_prime) / self.K(self.k)
    
    def solve_for_impedance(self, target = 50, test_param = None, p0=1, bounds=(1e-3, 200)):
        if test_param == 's':
            return root_scalar(lambda s: self.impedance(self.w, s)-target, x0=p0, bracket=bounds)['root']
        elif test_param == 'w':
            return root_scalar(lambda w: self.impedance(w, self.s)-target, x0=p0, bracket=bounds)['root']
        else:
            return f'test_param must be a valid parameter but is \'{test_param}\''
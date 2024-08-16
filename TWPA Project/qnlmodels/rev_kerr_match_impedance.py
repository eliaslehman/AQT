import numpy as np
import scipy as sp
import scipy.integrate
import scipy.special
import matplotlib.pyplot as plt
from scipy.optimize import fsolve, minimize

h = 6.626e-34
e = 1.6e-19
Phi0 = h / (2 * e)

class MatchImpedance:
    """Class of utils to exctract impedance data for matching with transmission lines."""
    
    def __init__(self, J0, A, r_range, Cg_range):
        self.I0 = J0 * A
        self.r_range = r_range
        self.Cg_range = Cg_range
        self.Z_map = None
        self.R = None
        self.Cg = None
        self.phi_ext = np.pi

    def optimize_applied_flux(self):
        result = minimize(lambda flux: self.g4(flux), Phi0 / 2, bounds=[(Phi0 / 4, 3 * Phi0 / 4)])
        optimal_flux = result.x[0]
        return optimal_flux
    
    def I(self, r, phi):
        return r * self.I0 * np.sin(phi) + self.I0 * np.sin(phi / 3 - self.phi_ext / 3)

    def alpha(self, r, phi_star):
        return r * np.cos(phi_star) + np.cos((phi_star - self.phi_ext) / 3) / 3

    def L(self, a):
        return abs(Phi0 / (2 * np.pi * self.I0 * a))

    def Z0(self, L, Cg):
        return np.sqrt(L / Cg)

    def find_r_for_Z0(self, target_Z0, Cg):
        if self.Z_map is None:
            phi_s_values = [fsolve(lambda phi: self.I(r, phi), 0)[0] for r in self.r_range]
            a_values = [self.alpha(r, phi_s) for r, phi_s in zip(self.r_range, phi_s_values)]
            L_values = [self.L(a) for a in a_values]
            self.Z_map = [self.Z0(L, Cg) for L in L_values]

        closest_Z0_indices = np.abs([zm - zt for zm, zt in zip(self.Z_map, [target_Z0]*len(self.Z_map))]).argmin(axis=0)
        closest_r_values = self.r_range[closest_Z0_indices]
        return closest_r_values

    def plot_heatmap(self, r_mark=None, Cg_mark=None):
        if self.Z_map is None:
            self.R, self.Cg = np.meshgrid(self.r_range, self.Cg_range)
            phi_s_values = [fsolve(lambda phi: self.I(r, phi), 0)[0] for r in self.r_range]
            a_values = [self.alpha(r, phi_s) for r, phi_s in zip(self.r_range, phi_s_values)]
            L_values = [self.L(a) for a in a_values]
            self.Z_map = self.Z0(L_values, self.Cg)
        
        plt.figure(figsize=(10, 8))
        plt.contourf(self.Cg * 1e15, self.R, self.Z_map, levels=50, cmap='viridis')
        cbar = plt.colorbar()
        cbar.set_label('Impedance (Ohms)')
        
        contour = plt.contour(self.Cg * 1e15, self.R, self.Z_map, levels=[50], colors='red', linewidths=2)
        plt.clabel(contour, inline=True, fontsize=12, fmt='50 Ohms')

        if r_mark : plt.hlines(r_mark, self.Cg_range[0] * 1e15, self.Cg_range[-1] * 1e15, colors="orange", linestyles="--")
        if Cg_mark : plt.vlines(Cg_mark, self.r_range[0], self.r_range[-1], colors="orange", linestyles="--")
        
        plt.xlabel('Cg (fF)')
        plt.ylabel('r')
        plt.title('Impedance Heat Map with 50 Ohms Contour Line')
        plt.show()
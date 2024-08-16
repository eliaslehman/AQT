import math
import numpy as np
import scipy as sp
import scipy.integrate
import scipy.special
import matplotlib.pyplot as plt

class KlopfensteinTaper:
    """
    Simulation of Klopfenstein Taper used for Reverse Kerr TWPA impedance design.

    Parameters:
        A = arccosh(amplitude ratio) -- sets maximum oscillation amplitude of reflection coefficeint in passband
        
        Ex. for some initial reflection coefficient R(x=0) = r, oscillations occur with amplitude r/cosh(A).
            If we want to limit reflection coefficient in the passband to r/10, set A = arccosh(10)

    """
    def __init__(self, A):
        self.A = A

    def ln_Z0(self, Z1, Z2, l, x):
        return np.log(Z1 * Z2)/2 + (np.log(Z2 / Z1) / 2 / np.cosh(self.A)) * (self.A**2 * self.phi(2 * x / l, self.A) 
                                                                              + np.heaviside(x - l/2, 1) 
                                                                              + np.heaviside(x + l/2, 1) 
                                                                              - 1)
    
    def phi(self, z, A):
        result, _ = sp.integrate.quad(lambda y: sp.special.iv(1, A*np.sqrt(1-y**2)) / (A*np.sqrt(1-y**2)), 0, z)
        return result
    
    def reflection_coeff(self, Z1, Z2, l, B):
        
        return np.log(Z2 / Z1) / 2 / np.cosh(self.A) * np.cos(np.sqrt((B*l)**2-self.A**2))
    
    def plot_phi(self, A_values_db):
        A_values = [np.arccosh(10**(db/20)) for db in A_values_db]
        z_values = np.linspace(0, 1, 500)

        plt.figure(figsize=(10, 6))

        for A in A_values:
            phi_values = [self.phi(z, A) for z in z_values]
            plt.plot(z_values, phi_values, label=f'20 log10(cosh(A)) = {20*np.log10(np.cosh(A)):.1f}')

        plt.xlabel('z')
        plt.ylabel(r'$\phi(z, A)$')
        plt.title(r'$\phi(z, A)$ as a function of $z$ for different values of $20 \log_{10} (\cosh(A))$')
        plt.legend()
        plt.grid(True)
        plt.show()

    def get_impedance(self, Z1, Z2, x_values):
        return np.exp([self.ln_Z0(Z1, Z2, 1, x-1/2) for x in x_values])
    
    def get_all_impedances(self, Z1, Z2):
        x_values = np.linspace(0, 1, 500)
        return np.exp([self.ln_Z0(Z1, Z2, 1, x-1/2) for x in x_values])

    def plot_impedance(self, Z1, Z2, l):
        # Generate x values from -l/2 to l/2
        x_values = np.linspace(-l/2, l/2, 500)
        Z0_values = np.exp([self.ln_Z0(Z1, Z2, l, x) for x in x_values])

        # Plotting
        plt.figure(figsize=(10, 6))
        plt.plot(x_values, Z0_values, label='cosh(A) = {:.1f}'.format(np.cosh(self.A)))
        plt.xlabel('x')
        plt.ylabel(r'$Z_0$')
        plt.title(r'$Z_0$ as a function of $x$')
        plt.legend()
        plt.grid(True)
        plt.show()

        return Z0_values

    def plot_reflection_coef (self, Z1, Z2, A_values_db):
        A_values = [np.arccosh(10**(db/20)) for db in A_values_db]

        wavelength = 1  # Wavelength
        B = 2 * np.pi / wavelength

        # Generate lB values from 0.1 to 10
        lB_values = np.linspace(0.1*wavelength, 2*wavelength, 500)

        # Create the plot
        fig, ax1 = plt.subplots(figsize=(15, 10))

        for A in A_values:
            taper = KlopfensteinTaper(A)
            reflection_coeff_values = [abs(taper.reflection_coeff(Z1, Z2, lB, B) * 2 / np.log(Z2 / Z1)) for lB in lB_values]
            ax1.plot(lB_values / wavelength, reflection_coeff_values, label=f'{round(20 * np.log10(np.cosh(A)))}')

        ax1.set_xlabel(r'Elecrtical Length ($l/\lambda$)')
        ax1.set_ylabel(r'Relative Reflection Coefficient $|\rho/\rho_0|$')
        ax1.set_title(r'Reflection Coefficient vs. Electrical Length for various values of $A$')
        ax1.legend(loc='upper right', bbox_to_anchor=(1.15, 1), title="COSH(A) (dB)")
        ax1.grid(True)

        # Create a second y-axis
        ax2 = ax1.twinx()
        ax2.set_ylabel(r'Net Reflection Coefficient $|\rho|$')

        # Scale the second y-axis
        rho0 = 1  # Example value for rho0, adjust according to your needs
        ax2.set_ylim(np.array(ax1.get_ylim()) * np.log(Z2 / Z1) / 2)

        plt.show()
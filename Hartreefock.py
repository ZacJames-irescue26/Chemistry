import numpy as np
import matplotlib.pyplot as plt
from pyqint import pyqint, Molecule, HF, GeometryOptimization
from scipy.interpolate import interp1d

#
# Exercise 3.15
#

def main():
    # determine energies
    ens = []
    xx = [0.1,0.2,0.3,0.4, 0.5, 0.6,0.7,0.8,0.9, 1.0, 1.1,1.2,1.3,1.4,1.5,2,3,4,5,6,7,8,9, 10]
    for x in range(len(xx)):
        mol = Molecule('H2')
        mol.add_atom('H', 0.0, 0.0, -xx[x]/2, unit='angstrom')
        mol.add_atom('H', 0.0, 0.0, xx[x]/2, unit='angstrom')
        res = HF().rhf(mol, 'sto3g', use_diis=False)
        print(res['energy'])
        ens.append(res['energy'])
    
    # plot result
    plt.figure(dpi=144)
    plt.plot(xx, ens, 'o', label='Data points')
    # perform cubic interpolation
    f = interp1d(xx, ens, kind='cubic')
    xx2 = np.linspace(0.5, 1.1, 1000)
    plt.plot(xx2, f(xx2), '--', label='cubic interpolation')
    plt.grid(linestyle='--')
    plt.legend()
    plt.tight_layout()
   # plt.show()
    res = GeometryOptimization(verbose=False).run(mol, 'sto3g')
    print(res)    

main()

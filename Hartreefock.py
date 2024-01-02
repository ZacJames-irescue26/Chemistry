import numpy as np
import matplotlib.pyplot as plt
from pyqint import  Molecule, HF
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
    plt.show()
    
    # find index of minimum value for the energies
    index_min = min(range(len(f(xx2))), key=f(xx2).__getitem__)
    emin = f(xx2)[index_min]
    print('Minimum value (%f Ht) found at: r=%f' % (emin,xx2[index_min]))
    
    # calculate binding energy
    ebind = 2*-0.424413181578 - emin
    print('Binding energy: %f Ht' % ebind)
    
    # result using STO-3g basis set for H
    eh = optimize_hydrogen_atom()
    ebind = 2*eh - emin
    print('Binding energy (sto-3g): %f Ht' % ebind)

def optimize_hydrogen_atom():
    mol = Molecule('H')
    mol.add_atom('H', 0.0, 0.0, 0.0, unit='angstrom')
    cgfs, nuclei = mol.build_basis('sto3g')
    integrator = PyQInt()
    ekin = integrator.kinetic(cgfs[0], cgfs[0])
    enuc = integrator.nuclear(cgfs[0], cgfs[0], [0,0,0], 1)
    return ekin + enuc

main()
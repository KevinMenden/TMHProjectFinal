from PDBHelixParser import PDBParser, PDBHelixParser
import numpy as np
import matplotlib.pyplot as plt
import argparse
import sys
from Helix import Helix
from matplotlib.colors import colorConverter
from ModuleMethods import *
from Membrane import MembranePlacer
from mpl_toolkits.mplot3d import axes3d

__author__ = "Kevin Menden"
__date__ = '02.06.2016'
"""
This program takes a PDB file, reads it and predicts
which of its helices are transmembrane helices and which are not
Using this helices the program tries to find the most likely
orientation of the membrane and returns this membrane
as two planes: one for each ende of the membrane
"""


# Define the argparser



if __name__== "__main__":
    # parser = argparse.ArgumentParser(description="Membrane Plane Finder")
    # parser.add_argument('pdb')
    file="test/7prc.pdb"
    pdbParser = PDBHelixParser(file)
    pdbParser.parse_pdb_file()
    structure = pdbParser.structure         # The whole structure of the PDB file
    print("Parsed PDB file succesfully")
    raw_helices = pdbParser.proteinHelixSequences

    # Convert raw helices into Helix objects
    helix_set = []
    for h in raw_helices:
        if len(h) > 0:
            helix_set.append(Helix(h))
    print("Found " + str(len(helix_set)) + " helices")

    # Predict transmembrane helices
    tmh_set = []
    for h in helix_set:
        if is_transmembrane_helix(h) == 'tm':
            tmh_set.append(h)
    print(len(tmh_set) / len(helix_set))
    if len(tmh_set) < 3 or len(tmh_set)/len(helix_set) < 0.1:
        print("No transmembrane protein!")
        sys.exit(0)
    else:
        print("Transmembrane protein")

    print("Predicted transmembrane helices: " + str(len(tmh_set)))

    # Calculate the normal vector of the transmembrane plane
    normal = calculate_normal_vector(tmh_set)
    print("Membrane normal vector: " + str(normal))

    # Choose the helix closest to the normal for width of the membrane
    # Create a plot
    placer=MembranePlacer(tmh_set,structure,normal,file)
    membranes=placer.placeMembrane()
    lower_membrane = membranes[0]
    upper_membrane = membranes[1]

    null_point = np.array([0, 0, 0])
    # Calculate membrane thickness
    d11 = -lower_membrane.dot(normal)
    thickness = ((normal.dot(upper_membrane) - normal.dot(lower_membrane))) / 1
    print("Thicknes of membrane: " + str(thickness) + " A")
    print(lower_membrane)
    print(upper_membrane)


    fig = plt.figure()
    ax = fig.gca(projection='3d')
    for tmh in tmh_set:
        add_quiver(ax, tmh)

    # 3D presentation of helix vectors and membrane planes
    ax.quiver(lower_membrane[0], lower_membrane[1], lower_membrane[2], normal[0], normal[1], normal[2],
              colors=colorConverter.to_rgb('g'), lw=8, length=50, pivot='tail')
    d1 = -lower_membrane.dot(normal)
    d2 = -upper_membrane.dot(normal)
    xx1, yy1 = np.meshgrid(range(-100, 100), range(-100, 100))
    xx2, yy2 = np.meshgrid(range(-100, 100), range(-100, 100))
    z1 = (-normal[0] * xx1 - normal[1] * yy1 - d1) * 1. / normal[2]
    z2 = (-normal[0] * xx2 - normal[1] * yy2 - d2) * 1. / normal[2]
    ax.plot_surface(xx1, yy1, z1, color="blue", lw=4, alpha=.2)
    ax.plot_surface(xx2, yy2, z2, color="red", lw=4, alpha=.2)
    ax.set_xlim(-100, 100)
    ax.set_ylim(-100, 100)
    ax.set_zlim(-100, 100)

    # Include atoms (bad performance)
    # for res in structure.get_residues():
    #     if res.has_id('N'):
    #         coord = res['N'].get_coord()
    #         ax.scatter(coord[0], coord[1], coord[2], color="black")

    plt.show()
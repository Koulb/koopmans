import numpy as np
import math
import re
import sys
from read_data import *
from write_data import *
from modules import *


###################### BEGIN INPUT ######################

dir_wann_pc = '/scratch/degennar/wannier_interpolation/1D_chain/pcell_411/wannier-occ'		# path to the wannier input file of the PC
dir_wann_sc = '/scratch/degennar/wannier_interpolation/1D_chain/scell_411/wannier-occ'		# path to the wannier output file of the SC
seedname = '1Dchain'				# seedname as in wannier input file
cutoff = 1E-4				# cutoff on the calculation of WFs distances
interpolation = True			# if True the bands are interpolated along the following path

# If interpolation = True, k-path in PC crystal coordinates
#k_path = np.array(((0,0,0),(0.125,0,0),(0.25,0,0),(0.375,0,0),(0.5,0,0),(0.5,0,0.125),(0.5,0,0.25),(0.5,0,0.375),(0.5,0,0.5),(0.375,0,0.375),(0.25,0,0.25),(0.125,0,0.125),(0,0,0)))
k_path = np.array(((0.00000000,0.00000000,0.00000000),(0.06250000,0.00000000,0.00000000),(0.12500000,0.00000000,0.00000000),(0.18750000,0.00000000,0.00000000),(0.25000000,0.00000000,0.00000000),(0.31250000,0.00000000,0.00000000),(0.37500000,0.00000000,0.00000000),(0.43750000,0.00000000,0.00000000),(0.50000000,0.00000000,0.00000000),(0.56250000,0.00000000,0.00000000),(0.62500000,0.00000000,0.00000000),(0.68750000,0.00000000,0.00000000),(0.75000000,0.00000000,0.00000000),(0.81250000,0.00000000,0.00000000),(0.87500000,0.00000000,0.00000000),(0.93750000,0.00000000,0.00000000)))

####################### END INPUT #######################


nk1,nk2,nk3,k_mesh = read_wannier_pcell(dir_wann_pc,seedname)	# TO REMOVE!!! WE WANT TO READ ONLY FROM THE SC FILES
nktot = nk1*nk2*nk3

num_wann,latt_vec_sc,centers = read_wannier_scell(dir_wann_sc,seedname)

latt_vec_pc = (latt_vec_sc.transpose()/np.array((nk1,nk2,nk3))).transpose()


if num_wann%nktot!=0:	sys.exit('\nSomething wrong !\nnum_wann must be a multiple of nktot\n')

# Shift the WFs inside the SC if they are outside
for n in range(num_wann):
	x = np.linalg.solve(latt_vec_sc,centers[n])
	for i in range(3):
		if x[i] >= 0:	x[i] = x[i] - int(x[i])
		if x[i] < 0:	x[i] = x[i] - int(x[i]) + 1
	centers[n] = np.dot(x,latt_vec_sc)


# Building the map |m> --> |Rn>.
# The variable wann_pc will contain all the WFs of the SC, but reordered following the PC indexing |Rn>.
# In the following loop we find the WFs in the PC only, that is |0m>. Further we find also the other WFs.
wann_pc = np.zeros((nktot,num_wann/nktot,4))
index = 0
for n in range(num_wann):
	x = np.linalg.solve(latt_vec_pc,centers[n])
	y = np.array((1,1,1)) - x
	if (y>cutoff*np.array((1,1,1))).all() and (y<=np.array((1,1,1))).all():
		wann_pc[0,index,0] = n + 1
		wann_pc[0,index,1:] = centers[n,:]
		index = index + 1


# Here we find all the other WFs
R = Rvec(nk1,nk2,nk3)
for m in range(num_wann):
	for n in range(num_wann/nktot):
		if wann_match(centers[m],wann_pc[0,n,1:],latt_vec_pc,cutoff):
			dist = centers[m] - wann_pc[0,n,1:]
			x = np.linalg.solve(latt_vec_pc,dist)
			for i in range(nktot):
				if (np.round(x) == R[i]).all():
					wann_pc[i,n,0] = m + 1
					wann_pc[i,n,1:] = centers[m,:]
					break
			break

#for i in range(nktot):
#	for n in range(num_wann/nktot):
#		print ' X  %.6f  %.6f  %.6f' %(wann_pc[i,n,1]/10.8618, wann_pc[i,n,2]/10.8618, wann_pc[i,n,3]/10.8618)

# Read wannier Hamiltonian and rewrite it in terms of the mapped WFs: <i|H|j> --> <Rm|H|R'n> (the translational symmetry is not exploited and all the matrix elements are calculated explicitly!)
hr_old = read_hr(dir_wann_sc,seedname,num_wann)
hr_new = np.zeros((nktot,nktot,num_wann/nktot,num_wann/nktot),dtype=complex)
for r1 in range(nktot):
	for r2 in range(nktot):
		for m in range(num_wann/nktot):
			for n in range(num_wann/nktot):
				i = int(wann_pc[r1,m,0]) - 1
				j = int(wann_pc[r2,n,0]) - 1
				hr_new[r1,r2,m,n] = hr_old[i,j]


# Calculate H(k) and its eigenvalues
eig_k = []

if interpolation:
	hk = np.zeros((k_path.shape[0],num_wann/nktot,num_wann/nktot),dtype=complex)
	for kn in range(k_path.shape[0]):
		k = k_path[kn]
		if kn==1:	print '\nk = ',k
		for m in range(num_wann/nktot):
			for n in range(num_wann/nktot):
				for i in range(nktot):
					phase_factor,Tnn = ws_distance(nk1,nk2,nk3,latt_vec_sc,k,cutoff,wann_pc[i,n,1:],wann_pc[0,m,1:])
					hk[kn,m,n] = hk[kn,m,n] + np.exp(1j*2*np.pi*np.dot(k,R[i])) * phase_factor * hr_new[0,i,m,n]	# Hmn(k) = sum_R e^(-ikR) * ( sum_Tnn e^(-ikTnn) ) * <0m|H|Rn>
					if kn==1:
						print '\nFor <R0,%d|H|R%d,%d> :' %(m,i,n)
						print 'R = ',R[i],'\tT = ',Tnn
						print 'R + T = ',R[i]+Tnn
						print 'exp(ikR) = ',np.exp(1j*2*np.pi*np.dot(k,R[i]))
						print 'phase_factor = ',phase_factor
						print 'exp(ikR)*phase_factor = ',np.exp(1j*2*np.pi*np.dot(k,R[i]))*phase_factor
						print 'Hmn(R) = ',hr_new[0,i,m,n]
						print 'hk(partial) = ',hk[kn,:,:]
		eig_k.append(np.linalg.eigvalsh(hk[kn,:,:]))

else:	# else the Hamiltonian is calculated over the k-mesh
	hk = np.zeros((k_mesh.shape[0],num_wann/nktot,num_wann/nktot),dtype=complex)
	for kn in range(k_mesh.shape[0]):
		k = k_mesh[kn]
		for m in range(num_wann/nktot):
			for n in range(num_wann/nktot):
				for i in range(nktot):
					hk[kn,m,n] = hk[kn,m,n] + np.exp(1j*2*np.pi*np.dot(k,R[i])) * hr_new[0,i,m,n]			# Hmn(k) = sum_R e^(-ikR) * <0m|H|Rn>
		eig_k.append(np.linalg.eigvalsh(hk[kn,:,:]))


eig_k = np.array(eig_k)

# Write eigenvalues in file 'bands_interpolated.dat' or 'eigk.dat'
if interpolation:	write_output_eigk(eig_k,'band',dir_wann_sc,k_path)
else:			write_output_eigk(eig_k,'kvec',dir_wann_sc)


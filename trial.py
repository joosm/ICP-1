import numpy as np
import os
import pickle
from datetime import datetime as dt, timedelta
from read_data import readFile

def distance(p1, p2):
	return np.sqrt(np.sum(np.square(p1-p2),axis=-1))

if __name__ == '__main__':
	dir = 'point_cloud_registration'
	filenames = ['pointcloud1.fuse', 'pointcloud2.fuse']
	names = ['pointcloud1','pointcloud2']
	pointcloud1 = readFile('{}/{}'.format(dir, filenames[0]), names[0])
	pointcloud2 = readFile('{}/{}'.format(dir, filenames[1]), names[1])
	
	print(pointcloud1.shape)
	print(pointcloud2.shape)

	ind = np.where(np.equal(pointcloud1[:,3],pointcloud2[:,3]))[0]

	print(ind.shape)

	# d1 = distance(pointcloud1[0,:3], pointcloud1[:,:3])
	# d2 = distance(pointcloud2[0,:3], pointcloud2[:,:3])

	com_p1 = np.mean(pointcloud1[:,:3],axis=0).reshape((3,1))
	com_p2 = np.mean(pointcloud2[:,:3],axis=0).reshape((3,1))

	# print(com_p1.shape, com_p2.T.shape)
	com_p1p2 = com_p1.dot(com_p2.T)
	points1 = pointcloud1[:,:3].reshape((pointcloud1.shape[0],3,1))
	# print(pointcloud1[:10])
	# print(points1[:10])
	points2 = pointcloud2[:,:3].reshape((pointcloud2.shape[0],3,1))

	p1p2 = np.zeros((points1.shape[0],3,3),dtype=points1.dtype)
	for i in range(points1.shape[0]):
		p1p2[i,:,:] = points1[i].dot(points2[i].T)[:,:]

	# print(p1p2[:10])
	sigma_p1p2 = np.mean(p1p2, axis=0) - com_p1p2
	del p1p2
	del points1
	del points2

	A = sigma_p1p2 - sigma_p1p2.T
	# print(A.shape)

	delta = np.array([[A[1,2]],[A[2,0]],[A[0,1]]],dtype=A.dtype)

	Q_sigma_p1p2 = np.zeros((4,4),dtype=A.dtype)

	Q_sigma_p1p2[0,0] = np.trace(sigma_p1p2)
	Q_sigma_p1p2[1:,0] = delta[:,0]
	Q_sigma_p1p2[0,1:] = delta.T[0,:]
	temp = sigma_p1p2 + sigma_p1p2.T - np.trace(sigma_p1p2)*np.eye(3)
	Q_sigma_p1p2[1:,1:] = temp[:,:]

	u,s,v = np.linalg.svd(Q_sigma_p1p2)
	# print(u.shape)
	# print(s.shape)
	# print(v.shape)
	# print(np.argmax(s))
	ind = np.argmax(s)

	q_r = u[:,ind]
	# print(np.sum(np.square(q_r)))
	# print(q_r.shape)

	R = np.zeros((3,3),dtype=A.dtype)

	sq_q_r = np.square(q_r)
	R[0,0] = sq_q_r[0] + sq_q_r[1] - sq_q_r[2] - sq_q_r[3]
	R[1,1] = sq_q_r[0] + sq_q_r[2] - sq_q_r[1] - sq_q_r[3]
	R[2,2] = sq_q_r[0] + sq_q_r[3] - sq_q_r[1] - sq_q_r[2]

	R[0,1] = 2*(q_r[1]*q_r[2] + q_r[0]*q_r[3])
	R[1,0] = 2*(q_r[1]*q_r[2] - q_r[0]*q_r[3])

	R[0,2] = 2*(q_r[1]*q_r[3] - q_r[0]*q_r[2])
	R[0,2] = 2*(q_r[1]*q_r[3] + q_r[0]*q_r[2])

	R[1,2] = 2*(q_r[2]*q_r[3] - q_r[0]*q_r[1])
	R[2,1] = 2*(q_r[2]*q_r[3] + q_r[0]*q_r[1])

	q_t = com_p2 - R.dot(com_p1)

	print(q_t)



	# print(delta.shape)
	
	# print(sigma_p1p2)

	# print(d1)
	# print(d2)

	# d1.sort()
	# d2.sort()

	# ind = np.where(np.equal(d1[:1000],d2[:1000]))
	# print(ind[0].shape)
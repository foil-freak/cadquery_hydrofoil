from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
from scipy import interpolate
from scipy.ndimage.filters import uniform_filter1d
import pickle
plt.ion()


class ReadWingShape(object):
	'''reads wing silhouette from png file'''
	def __init__(self, png_name, half_wing_span):
		self.png_name = png_name
		self.half_wing_span = half_wing_span #mm for a half wing

		self.y1 = None #function for lower silhouette of wing
		self.y2 = None #function for upper silhouette of wing

		self.analyzeSilhouetteImage(draw=False)

	def smoothen(self, x, y):
		'''goal of this funtion is to remove duplicate datapoints 
			with the same y-coordinate'''
		u = np.unique(y)
		res = []
		for yp in u:
			idxs = np.where(y==yp)[0]
			xps = list(x[idxs])
			xmean = np.mean(xps)
			res.append([xmean, yp])

		res = np.array(res)

		xr = res[:,0]
		yr = res[:,1]

		if xr[0] > xr[-1]:
			xr = xr[::-1]
			yr = yr[::-1]

		return [xr, yr]


	def analyzeSilhouetteImage(self, draw=False):
		img = Image.open(self.png_name).convert('1')
		arr = np.array(img)
		arr = np.rot90(arr)

		res = []
		for idx, col in enumerate(arr):
			tmp = np.where(col==False)
			if len(tmp[0])>2:
				res.append([idx, tmp[0][0], tmp[0][-1]])

		half_wing_span = 600 #mm
		pixels = len(res)
		self.x = np.linspace(-1,self.half_wing_span+1, int(pixels/4))
		norm = self.half_wing_span/pixels

		res = np.array(res)*norm
		x = res[:,0]
		y1p = res[:,1]
		y2p = res[:,2]

		#plt.plot(x, y1p, 'r.', ms=0.5)
		#plt.plot(x, y2p, 'b.', ms=0.5)

		[xs1, ys1] = self.smoothen(x, y1p)
		[xs2, ys2] = self.smoothen(x, y2p)


		self.y1 = interpolate.interp1d(xs1, ys1, fill_value='extrapolate')
		self.y2 = interpolate.interp1d(xs2, ys2, fill_value='extrapolate')

		if draw:
			#original data points
			plt.plot(xs1, ys1, 'r+', ms=1)
			plt.plot(xs2, ys2, 'b+', ms=1)

			#plines
			y1_spline = self.y1(self.x)
			y2_spline = self.y2(self.x)

			plt.plot(self.x, y1_spline, 'k-')
			plt.plot(self.x, y2_spline, 'k-')
			plt.show()

	def getSilhouettePoints(self, x):
		x = self.half_wing_span-x

		y1 = self.y1(x)
		y2 = self.y2(x)
		l = abs(y2 - y1) #length for scaling wing profile
		
		return [float(y1), l]

'''
if __name__ == '__main__':
	rws = ReadWingShape('Drawing1.png')
	rws.analyzeSilhouetteImage(draw=True)


	print(rws.getSilhouettePoints(0))
'''


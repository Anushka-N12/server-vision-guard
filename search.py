from scipy.io import loadmat
import numpy as np

def find_n(m,n):
    c = np.where(m==n)
    x,y = c[0][0], c[1][0]
    return x,y
    
def circle_n(m, start_c, end_c, limits):
    m_s  = m.shape
    print('Matrix shape = ', m_s)

    top_range = np.array([], dtype=int)
    right_range = np.array([], dtype=int)
    bottom_range = np.array([], dtype=int)
    left_range = np.array([], dtype=int)

    if limits[0] == 1:
        if start_c[0] > 0:
            top_range = m[start_c[0]-1, start_c[1]:end_c[1]+1]
            if start_c[1] > 0:
                top_range = np.insert(top_range, 0, m[start_c[0]-1, start_c[1]-1], axis=0)
            else:
                limits[3] = 0
        else:
            limits[0] = 0
    print('top_range = ', top_range)
    
    if limits[1] == 1:
        if end_c[1] < m_s[1]-1:
            right_range = np.append(right_range, m[start_c[0]:end_c[0]+1, end_c[1]+1], axis=0)
            if start_c[0] > 0:
                right_range = np.insert(right_range, 0, m[start_c[0]-1, end_c[1]+1], axis=0)
        else: 
            limits[1] = 0
    print('right_range = ', right_range)
    
    if limits[2] == 1:
        if end_c[0] < m_s[0]-1:
            bottom_range = np.append(bottom_range, m[end_c[0]+1, start_c[1]:end_c[1]+1], axis=0)
            if end_c[1] < m_s[1]-1:
                bottom_range = np.insert(bottom_range, bottom_range.size, m[end_c[0]+1, end_c[1]+1], axis=0)
        else:
            limits[2] = 0
    print('bottom_range = ', bottom_range)

    if limits[3] == 1:
        if start_c[1] > 0:
            left_range = np.append(left_range, m[start_c[0]:end_c[0]+1, start_c[1]-1], axis=0)
            if end_c[0] < m_s[0]-1:
                left_range = np.insert(left_range, left_range.size, m[end_c[0]+1, start_c[1]+1], axis=0)
        else:
            limits[3] = 0
    print('left_range = ', left_range)

    return top_range, right_range, bottom_range, left_range, limits

def cams(id, increment=0, limits=[1,1,1,1]):
    m = loadmat('map.mat')['map']
    x,y = find_n(m,id)
    x_i, y_i = (x-increment, y-increment), (x+increment,y+increment)
    print('Searching w range ', x_i, y_i)
    top, right, bottom, left, limits = circle_n(m, x_i, y_i, limits)

    return top, right, bottom, left, limits


if __name__ == '__main__':
    print(cams(4, 3, [0,1,0,1]))

    # m = loadmat('map.mat')['map']
    # circle_n(m, (1,1), (3,3))
    # circle_n(m, (1,1), (4,4))
    # circle_n(m, (1,3), (3,5))
    # circle_n(m, (2,4), (2,4))
    # circle_n(m, (-1,3), (3,7))

from scipy import *
from scipy.special import *

from scipy import optimize

from math import sqrt, log, log10, floor

import numpy as np


def find_ev_position(data, ev, lb=0, ub=-1):
    # find the position in data[] where the found ae lies
    
    if ub == -1:
        ub = len(data)
    
    e_pos = -1
    for energy in data[:, 0]:
        if energy <= ev:
            e_pos += 1
        else:
            break
    
    if data[e_pos, 0] < lb or data[e_pos, 0] > ub or e_pos == len(data):
        e_pos = -1
    
    return e_pos

def fit_function_to_data(data, p, fwhm, lbs, ubs, std_errs = None):
    # tighten sigma on the go (lasso sigma)
    
    base_func = eval_fit_function(fwhm)

    res = optimize.curve_fit(base_func,
                             data[:, 0],
                             data[:, 1],
                             p[:],
                             sigma=std_errs,
                             method='trf',
                             absolute_sigma=False,
                             bounds=(lbs, ubs),
                             check_finite=True)
    
    # return initial_parameters and stddev for the parameters
    return res[0], np.sqrt(np.diag(res[1])), base_func

def find_fwhm(starting_fwhm, ending_fwhm, iteration, n):
    a = starting_fwhm
    b = ending_fwhm
    c = n - 1
    x = iteration
    
    if c > 0:
        
        # with the lasso-sigma method, one question is, how (fast) sigma (= f(fwhm)) tightens. For this several progressions have been
        # tested over several datasets, with different sigmas, although not very extensive. So far concave functions, where
        # the difference is smaller at the beginning and then bigger towards the end, have worked out best so far. All of
        # the functions below start at 'starting_fwhm' and end at 'ending_fwhm' over 'iteration' steps
    
        #problems with possible divisions by 0:
        
        # return (b - a) / (c**2) * (x**2) + a #quadratic, nonconvs 74, 3, 0, 0, 0, 0, 0
        # return (b - a) / c * x + a #linear, nonconvs 63, 6, 0, 0, 0, 0, 0
        # return (a - b) * log(-x + c + 1) / log(c + 1) + b  # logarithmic, nonconvs 33, 4, 0, 0, 0, 0, 0
        # return (a - b) / sqrt(c) * sqrt(-x + c) + b  # sqrt, nonconvs 50, 4, 0, 0, 0, 0, 0
        return (a - b)*(1 - exp(x - c)) + b #exponential,nonconvs: 31, 3, 0, 0, 0, 0, 0
    
    else:
        #e = 1/0
        
        return ending_fwhm

def find_cut_numbers(data_length, data_length_ev, minspan):
    n = 1
    cutpercent = 0
    
    steps = float64(data_length - 1)
    
    if minspan > 0:
        # set a minimum of datapoints that are needed to do a decent fit (experimental value)
        # not pretty but seems to be working well so far with tested data
        min_data_points = int64(25)
        
        energy_step = float64(data_length_ev) / steps
        
        min_data_points_energy = int64(minspan / energy_step)
        
        if min_data_points < min_data_points_energy:
            min_data_points = min_data_points_energy
        
        a = 9  # number of datapoints to be cut, at last cut, experimental value
        
        n = int64((log(min_data_points) - log(data_length)) / (log(min_data_points) - log(a + min_data_points)))
        
        # n is equal to the number of iterations that it will take to get the data points down to its minimum, when it is
        # cut by cutpercent*100 % every iteration.
        # the int() cast will floor the number, which will most likely lead to having more than min_data_points
        # data points left to fit.
        
        cutpercent = pow(min_data_points / data_length, 1.0 / float64(n - 1))
        # (n-1)st root, because the data won't be cut for the first iteration, and therefore only n-1 times
        
        if cutpercent > 1.0:
            cutpercent = 1.0
            n = 1
    
    return n, cutpercent

def min_above_x(np_array, x):
    min = np.inf
    
    for value in np_array:
        if x < value < min:
            min = value
    
    return min

def fix_std_errs(std_errs):
    # a problem in the reduced chi squared fit are the variances = 0, which do happen at smaller energies.
    #min_err = 10**-2
    fit_std_errs = np.array([])

    if std_errs is not None:
        min_err = 10 ** np.floor(np.log10(min_above_x(std_errs, 0)))
        for std_err in std_errs:
            if std_err == 0:
                fit_std_errs = np.append(fit_std_errs, min_err)
            else:
                fit_std_errs = np.append(fit_std_errs, std_err)
    else:
        fit_std_errs = None
    
    return fit_std_errs

def find_best_fit(data, std_errs, ip, fwhm, minspan, lower_bounds, upper_bounds, update_function=None):
    # data has to be a numpy array
    # fits the function to data[:,0] (as x) and data[:,1] (as y) using the initial_parameters
    # returns an array of parameters of the same size as initial_parameters in case of success
    # returns None if data couldn't be fitted
    
    p = np.array([0] * 4)
    c_p = np.array(ip)
    c_stddev = -1
    c_fit_function = None
    fit_weights = fix_std_errs(std_errs)

    # find number of iterations to take place where the data is cut down by x %
    n, cutpercent = find_cut_numbers(len(data), data[len(data) - 1][0] - data[0][0], minspan)
    
    cutdata = data
    cutweights = fit_weights

    message = 'fit did not converge at any iteration.'
    
    
    starting_fwhm = fwhm * 3
    ending_fwhm = fwhm
    
    # fit another n times while closing in on the EA
    # The following conditions apply:
    # a) there have to be less than n iterations, to guarantee enough data points to fit AND
    # b) the energy span of the cut data has to be enough to guarantee a sensible fit
    
    iteration = 0
    stddev = -1
    fit_function = None
    r_fwhm = -1
    
    while iteration < n:
        
        fwhm = find_fwhm(starting_fwhm, ending_fwhm, iteration, n)
        
        # try to fit
        try:
            # c_p, c_stddev,  c_fit_function = fit_function_to_data(cutdata, c_p, fwhm, cutdata[0][0], cutdata[len(cutdata)-1, 0])
            c_p, c_stddev, c_fit_function = fit_function_to_data(cutdata, c_p, fwhm, lower_bounds, upper_bounds, cutweights)
            message = 'fit succeeded.'
        except Exception as error:
            if type(error) is ValueError:
                if error.args[0] == 'Residuals are not finite in the initial point.':
                    message = 'fit doesn\'t converge.'
                else:
                    message = "unhandled error: " + error.args[0] + ' iteration ' + str(iteration/n)
            elif type(error) is RuntimeError:
                if error.args[
                    0] == 'Optimal parameters not found: The maximum number of function evaluations is exceeded.':
                    message = 'fit doesn\'t converge'
            else:
                message = "unhandled error: " + error.args[0] + ' iteration ' + str(iteration/n)
        
        # get the position of EA in the data
        ae_pos = find_ev_position(data, c_p[1], cutdata[0, 0], cutdata[-1, 0])
        
        if ae_pos == -1:
            ae_pos = find_ev_position(data, p[1], cutdata[0, 0], cutdata[-1, 0])
            
            # set ae_pos to the center since it wasn't in the data
            # this will lead to cutting data nevertheless and could lead to a ae_pos in the center,
            # if the fit never works.
            
            # n += 1
            # increment n by one in order to ensure another run with a different fwhm to try to get a sensible ae
            # would probably bear problems with the accuracy in the play of minspan, cutpercent, and n
        else:
            # values are only saved as long as the ae lies in the cut down area
            
            r_fwhm = fwhm
            p = c_p
            stddev = c_stddev
            fit_function = c_fit_function
        
        # ae_pos has to be valid to cut the data.
        # At the end of the last run, it is not needed to cut again, and would even falsify data
        if iteration < n - 1:
            # use that position, to cut the data down to cutpercent*100% of its size
            cutdata = cut_relatively_equal(data, ae_pos, cutpercent ** (iteration + 1))
            if fit_weights is not None:
                cutweights = cut_relatively_equal_1D(fit_weights, ae_pos, cutpercent ** (iteration + 1))
        iteration += 1
        
        if update_function is not None:
            update_function(float((iteration) / n), p)
    
    return p, stddev, cutdata[0][0], cutdata[len(cutdata) - 1][0], r_fwhm, fit_function, message

def cut_relatively_equal(cutdata, ae_pos, cutpercent):
    # cuts data down to cutpercent*100 % of its size, with EA in the middle
    # if however there are not enough data points on one of the sides to guarantee cutpercent*100 % of the data
    # more of the other side will be added.
    
    cdl = len(cutdata)
    buff_cutdata = []
    
    buff_cutdata.append(cutdata[ae_pos, :])
    
    # deviation from ae
    deviation = 1
    
    lc = 0
    rc = 0
    
    while len(buff_cutdata) / cdl <= cutpercent:
        
        current_pos = ae_pos - deviation
        
        if current_pos >= 0:
            buff_cutdata.insert(0, cutdata[current_pos, :])
            lc += 1
        
        current_pos = ae_pos + deviation
        
        if current_pos < cdl:
            buff_cutdata.append(cutdata[current_pos, :])
            rc += 1
        
        deviation += 1
    
    return np.array(buff_cutdata)


def cut_relatively_equal_1D(cutdata, ae_pos, cutpercent):
    # cuts data down to cutpercent*100 % of its size, with EA in the middle
    # if however there are not enough data points on one of the sides to guarantee cutpercent*100 % of the data
    # more of the other side will be added.
    
    cdl = len(cutdata)
    buff_cutdata = []
    
    buff_cutdata.append(cutdata[ae_pos])
    
    # deviation from ae
    deviation = 1
    
    lc = 0
    rc = 0
    
    while len(buff_cutdata) / cdl <= cutpercent:
        
        current_pos = ae_pos - deviation
        
        if current_pos >= 0:
            buff_cutdata.insert(0, cutdata[current_pos])
            lc += 1
        
        current_pos = ae_pos + deviation
        
        if current_pos < cdl:
            buff_cutdata.append(cutdata[current_pos])
            rc += 1
        
        deviation += 1
    
    return np.array(buff_cutdata)

def pbdv_fa(x, y):
    # we need this, because b is the derivative of a, which is not needed in fits and annoying when defining fit functions
    a, b = pbdv(x, y)
    
    return a

def difference_data_fit(data, fit_func, p, fwhm, nonnegative = False):
    fit_data = data_from_fit_and_parameters(data, fit_func, p, fwhm, True)
    
    return difference_data_from_fit_data(data, fit_data, p, fwhm, nonnegative)

def difference_data_from_fit_data(data, fit_data, p, fwhm, nonnegative):
    newdata = []
    i = 0
    
    for datapoint in fit_data:

        if data[i][1] is not None and fit_data[i][1] is not None:
            newpoint = [data[i][0], data[i][1] - fit_data[i][1]]
        #elif data[i] is not None and fit_data[i][1] is None:
        #    newpoint = [data[i][0], data[i][1]]
        else:
            newpoint = [data[i][0], None]


        
        if nonnegative and newpoint[1] < 0:
            newpoint[1] = 0  # -newpoint[1]
        
        newdata.append(newpoint)
        i += 1
    
    return np.array(newdata)

def data_from_fit_and_parameters(data, fit_func, p, fwhm, domain_indexes=None, continuation=False):
    # minimumpoints value is arbitrary, but very low. While testing, the amount of data never reached down to 20
    minimumpoints = 20

    continuation = True

    # check, whether there is a reasonable amount of points to plot:
    if len(data[:, 0]) > minimumpoints:
        # create empty float array in the size of data
        a = empty_like(data, dtype=float)
    else:
        a = empty((minimumpoints, 2), dtype=float)
    
    # created a problem, as x-points can slightly differ from the x-points in data, which is necessary for writing plot
    # to file and/or plotting the figures
    # Note: this also will make the check for minimumpoints not working for now, which might be left like this for now,
    # as data with less than 20 data-points seems rare
    # # create equidistant x points
    # a[:, 0] = linspace(data[:, 0].min(), data[:, 0].max(), len(a[:, 0]))
    
    a[:, 0] = data[:, 0]
    
    if fit_func is not None:
        # calculate corresponding y values
        a[:, 1] = fit_func(a[:, 0], p[0], p[1], p[2], p[3])
        
        if continuation:
            a = fit_continuation(a, p, fwhm)
    else:
        for point in a:
            point[1] = 0

    if domain_indexes is not None:
        for i in range(len(a)):
            if data[i][0] < data[domain_indexes[0]][0] or data[i][0] > data[domain_indexes[1]][0]:
                a[i][1] = None
    return a


def cutarray(data, lowerlim=None, upperlim=None):
    return cutarray2(data, lowerlim, upperlim)


def fwhm_to_sigma(fwhm):
    sigma = fwhm / (2 * sqrt(2 * np.log(2)))
    return sigma


def eval_fit_function(fwhm):
    # p[0] = y shift
    # p[1] = ae
    # p[2] = scale
    # p[3] = alpha
    
    sigma = fwhm_to_sigma(fwhm)

    base_func = f'lambda x, p0, p1, p2, p3: p2* ({sigma}**p3)*gamma(p3+1)*exp(-1.0/(4.0*{sigma}**2)*(p1-x)**2)*pbdv_fa(-(p3+1),(p1-x)/{sigma}) + p0'
    
    return eval(base_func)

def str_fit_func(p, fwhm):
    sigma = fwhm_to_sigma(fwhm)
    
    base_func = f'p2* ({sigma}^p3)*Gamma[p3+1]*Exp[-1.0/(4.0*{sigma}^2)*(p1-x)^2]*ParabolicCylinderD[-(p3+1),(p1-x)/{sigma}] + p0'
    
    for i in range(0, len(p)):
        base_func = base_func.replace('p'+str(i), str(p[i]))
        
    return base_func

def fit_continuation(data, p, fwhm):
    b = empty_like(data, dtype=float)
    
    for repeat in range(0, 10):
        fwhm += 0.1
        
        b_func = eval_fit_function(fwhm)
        
        b[:, 0] = data[:, 0]
        b[:, 1] = b_func(b[:, 0], p[0], p[1], p[2], p[3])
        
        nans = 0
        i = 0
        
        for point in data:
            if isnan(point[1]) or point[1] == np.inf:
                point[1] = b[i, 1]
                
                if isnan(point[1]) or point[1] == np.inf:
                    nans += 1
            i += 1
        
        if nans == 0:
            break
    
    return data

def magnitude(value):
    mag = 0

    if value != 0:
        mag = math.floor(log10(abs(value)))

    return mag


def roundToError(value, error, digits_of_error=1):
    m_val = magnitude(value)
    m_err = magnitude(error)

    r_val = round(value*10**(-m_err+digits_of_error-1))*10**(m_err-digits_of_error+1)
    r_err = round(error*10**(-m_err+digits_of_error-1))*10**(m_err-digits_of_error+1)

    return r_val, r_err, m_val, m_err

def roundToErrorStrings(value, error, digits_of_error=1):

    r_par, r_err, m_par, m_err = roundToError(value, error, digits_of_error)

    n_digits = -m_err + digits_of_error - 1
    if n_digits < 0:
        n_digits = 0

    par_str = '{0:.' + str(n_digits) + 'f}'
    par_str = par_str.format(r_par)
    err_str = '{0:.' + str(n_digits) + 'f}'
    err_str = err_str.format(r_err)

    return par_str, err_str


def cutarray2(data, lowerlim=None, upperlim=None, data2=None, returnIndexes=False):
    # this function cuts an array and returns it
    # if lowerlim or upperlim are not defined, the minimum and maximum is assumed
    # if returnIndexes is set to True, the indexes where the cuts were made - start and end - will be returned in a list

    i_from = -1
    i_to = -1

    if lowerlim is None:
        lowerlim = data[:, 0].min()
    
    if upperlim is None:
        upperlim = data[:, 0].max()
    
    lowerlim = float64(lowerlim)
    upperlim = float64(upperlim)
    
    newdata = []
    newdata2 = []
    
    for i in range(0, len(data)):
        point = data[i]
        
        if point[0] >= lowerlim and point[0] <= upperlim:
            newdata.append(point)

            if i_from == -1:
                i_from = i
            
            if data2 is not None:
                newdata2.append(data2[i])
        elif i_from != -1 and i_to == -1:
            i_to = i
    
    # data = array(newdata, dtype=float)
    
    if data2 is None:
        if returnIndexes:
            return array(newdata, dtype=float), (i_from, i_to)
        else:
            return array(newdata, dtype=float)
    else:
        if returnIndexes:
            return array(newdata, dtype=float), array(newdata2, dtype=float), (i_from, i_to)
        else:
            return array(newdata, dtype=float), array(newdata2, dtype=float)

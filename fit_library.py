# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import chisquare
from scipy.stats import chi2




class fitting(object):
    def __call__(self, data, bins, fit_func, guess):
        self.guess = guess
        self.bins  = bins
        self.data  = data
        self.fit_func = fit_func
        # Histogram
        self.hist, self.bin_edges = np.histogram(self.data, bins=self.bins)
        self.bin_centers = (self.bin_edges[:-1] + self.bin_edges[1:])/2

        # Fitting function call
        try:
            self.coeff, self.var_matrix = curve_fit(self.fit_func, self.bin_centers,
                                                    self.hist, p0=self.guess)
            self.perr = np.sqrt(np.absolute(np.diag(self.var_matrix)))
            # Error in parameter estimation
        except:
            print("Fitting Problems")
            self.coeff = np.array(self.guess)
            self.perr  = np.array(self.guess)
        #Gets fitted function and residues
        self.hist_fit = self.fit_func(self.bin_centers, *self.coeff)
        self.xi2, self.p = chisquare(f_obs=self.hist,f_exp=self.hist_fit)

    def evaluate(self,in_data):
        return self.fit_func(in_data,*self.coeff)


class fitting_nohist(object):
    def __call__(self, data, time, fit_func, guess):
        self.bins  = time
        self.data  = data
        self.fit_func = fit_func
        self.guess  = guess

        # Fitting function call
        try:
            self.coeff, self.var_matrix = curve_fit(self.fit_func, self.bins,
                                                    self.data, p0=self.guess,
                                                    method='lm')
            self.perr = np.sqrt(np.absolute(np.diag(self.var_matrix)))
            self.fit = self.fit_func(self.bins, *self.coeff)
            self.r_sqr = self.R_square()
            #Gets fitted function and R_square value for GOF
        # Error in parameter estimation
        except:
            print("Fitting Problems")
            self.coeff = np.zeros(len(self.guess))
            self.perr = np.ones(len(self.guess))*np.Inf
            self.r_sqr = 1E6


    def evaluate(self,in_data):
        return self.fit_func(in_data,*self.coeff)

    def R_square(self):
        ss_res = np.sum((self.data-self.fit)**2)
        ss_tot = np.sum((self.data-np.mean(self.data))**2)
        return 1-(ss_res / ss_tot)



class gompertz(fitting_nohist):

    def Gomp_n(self,x, n, *param):
        def Gomp(x, *param_inner):
            return (param_inner[0]/(1.0+np.exp(((x**2.0)-(param_inner[1]**2.0))*param_inner[2])))
        aux=np.zeros(len(x))
        for i in range(n):
            param_inner = [i for i in param[i*3+1:(i+1)*3+1]]
            aux = aux + Gomp(x,*param_inner)
        return aux + param[0]

    def __call__(self, data, time, n, p0):
        def G_aux(x,*param):
            return self.Gomp_n(x,n,*param)
        # lambda x,*param: self.Gompertz(x,n,*param)
        super(gompertz,self).__call__( data=data,
                                       time=time,
                                       fit_func= G_aux,
                                       guess=p0)

    def plot(self,axis,title,xlabel,ylabel,res=True,fit=True):
        axis.plot(self.data, self.bins, align='mid', facecolor='green', edgecolor='white', linewidth=0.5)
        # axis.set_xlabel(xlabel)
        # axis.set_ylabel(ylabel)
        # axis.set_title(title)
        # if (fit==True):
        #     axis.plot(self.bin_centers, self.hist_fit, 'r--', linewidth=1)
        #     if (res==True):
        #         axis.text(0.95,0.95, (('$\mu$=%0.3f (+/- %0.3f) \n'+\
        #                              '$\sigma$=%0.3f (+/- %0.3f) \n'+
        #                              'FWHM=%0.3f (+/- %0.3f) \n'+\
        #                              'Res=%0.3f%% (+/- %0.3f) \n'+\
        #                              'chi2=%0.3f \n'+'chi2inv_95=%0.3f \n'+\
        #                              'p=%0.3f') % \
        #                                 (self.coeff[1] , self.perr[1],
        #                                  np.absolute(self.coeff[2]) , self.perr[2],
        #                                  2.35*np.absolute(self.coeff[2]),
        #                                  2.35*np.absolute(self.perr[2]),
        #                                  2.35*np.absolute(self.coeff[2])*100/self.coeff[1],
        #                                  2.35*np.absolute(self.coeff[2])*100/self.coeff[1]*
        #                                  np.sqrt((self.perr[2]/self.coeff[2])**2+
        #                                          (self.perr[1]/self.coeff[1])**2),
        #                                  self.xi2,
        #                                  chi2.ppf(0.95,len(self.bin_centers)-2-1),
        #                                  self.p
        #                                 )
        #                               ),
        #                                  fontsize=8,
        #                                  verticalalignment='top',
        #                                  horizontalalignment='right',
        #                                  transform=axis.transAxes)
        #
        #
        #     else:
        #         # No resolution calculation
        #         axis.text(0.95,0.95, (('$\mu$=%0.3f (+/- %0.3f) \n'+\
        #                              '$\sigma$=%0.3f (+/- %0.3f) \n'+
        #                              'FWHM=%0.3f (+/- %0.3f) \n'+\
        #                              'chi2=%0.3f \n'+'chi2inv_95=%0.3f \n'+\
        #                              'p=%0.3f') % \
        #                                 (self.coeff[1], self.perr[1],
        #                                  np.absolute(self.coeff[2]), self.perr[2],
        #                                  2.35*np.absolute(self.coeff[2]),
        #                                  2.35*np.absolute(self.perr[2]),
        #                                  self.xi2,
        #                                  chi2.ppf(0.95,len(self.bin_centers)-2-1),
        #                                  self.p)),
        #                                  fontsize=8,
        #                                  verticalalignment='top',
        #                                  horizontalalignment='right',
        #                                  transform=axis.transAxes)


class double_exp_fit(fitting_nohist):

    def double_exp(x, *param):
        alfa = 1.0/param[1]
        beta = 1.0/param[0]
        t_p = np.log(beta/alfa)/(beta-alfa)
        K = (beta)*np.exp(alfa*t_p)/(beta-alfa)
        f = param[2]*K*(np.exp(-(x-param[3])*alfa)-np.exp(-(x-param[3])*beta))
        f[f<0] = 0
        return f

    def __call__(self, data, time, guess):
        # First guess
        super(double_exp_fit,self).__call__(data=data,
                                       time=time,
                                       fit_func=self.double_exp,
                                       guess=guess)

    def plot(self,axis,title,xlabel,ylabel,res=True,fit=True):
        #axis.hist(self.data, self.bins, align='mid', facecolor='green', edgecolor='white', linewidth=0.5)
        axis.set_xlabel(xlabel)
        axis.set_ylabel(ylabel)
        axis.set_title(title)
        if (fit==True):
            axis.plot(self.bins, self.fit, 'r--', linewidth=1)
            axis.text(0.95,0.95, (('tau2=%0.3f (+/- %0.3f) \n'+\
                                 'tau1=%0.3f (+/- %0.3f) \n'+
                                 'A=%0.3f (+/- %0.3f) \n'+\
                                 't0=%0.3f (+/- %0.3f)') % \
                                    (self.coeff[0] , self.perr[0],
                                     self.coeff[1] , self.perr[1],
                                     self.coeff[2] , self.perr[2],
                                     self.coeff[3] , self.perr[3]
                                    )
                                  ),
                                     fontsize=8,
                                     verticalalignment='top',
                                     horizontalalignment='right',
                                     transform=axis.transAxes)

class Ddouble_exp_fit(fitting_nohist):

    def Ddouble_exp(x, *param):
        alfa1 = 1.0/param[1]
        beta1 = 1.0/param[0]
        t_p1 = np.log(beta1/alfa1)/(beta1-alfa1)
        K1 = (beta1)*np.exp(alfa1*t_p1)/(beta1-alfa1)
        f1 = param[2]*K1*(np.exp(-(x-param[3])*alfa1)-np.exp(-(x-param[3])*beta1))
        f1[f1<0] = 0

        alfa2 = 1.0/param[5]
        beta2 = 1.0/param[4]
        t_p2 = np.log(beta2/alfa2)/(beta2-alfa2)
        K2 = (beta2)*np.exp(alfa2*t_p2)/(beta2-alfa2)
        f2 = param[6]*K2*(np.exp(-(x-param[7])*alfa2)-np.exp(-(x-param[7])*beta2))
        f2[f2<0] = 0

        return f1+f2

    def __call__(self, data, time, guess):
        # First guess
        super(Ddouble_exp_fit,self).__call__(data=data,
                                       time=time,
                                       fit_func=self.Ddouble_exp,
                                       guess=guess)

    def plot(self,axis,title,xlabel,ylabel,res=True,fit=True):
        #axis.hist(self.data, self.bins, align='mid', facecolor='green', edgecolor='white', linewidth=0.5)
        axis.set_xlabel(xlabel)
        axis.set_ylabel(ylabel)
        axis.set_title(title)
        if (fit==True):
            axis.plot(self.bins, self.fit, 'r--', linewidth=1)
            axis.text(0.95,0.95, (('tau2_a=%0.3f (+/- %0.3f) \n'+
                                 'tau1_a=%0.3f (+/- %0.3f) \n'+
                                 'A_a=%0.3f (+/- %0.3f) \n'+
                                 't0_a=%0.3f (+/- %0.3f) \n'+
                                 'tau2_b=%0.3f (+/- %0.3f) \n'+
                                 'tau1_b=%0.3f (+/- %0.3f) \n'+
                                 'A_b=%0.3f (+/- %0.3f) \n'+
                                 't0_b=%0.3f (+/- %0.3f)') % \
                                    (self.coeff[0] , self.perr[0],
                                     self.coeff[1] , self.perr[1],
                                     self.coeff[2] , self.perr[2],
                                     self.coeff[3] , self.perr[3],
                                     self.coeff[4] , self.perr[4],
                                     self.coeff[5] , self.perr[5],
                                     self.coeff[6] , self.perr[6],
                                     self.coeff[7] , self.perr[7]
                                    )
                                  ),
                                     fontsize=8,
                                     verticalalignment='top',
                                     horizontalalignment='right',
                                     transform=axis.transAxes)

class GND_fit(fitting):

    def GND(x, *param):
        # Generalized normal distribution
        # param[0]=ALFA | param[1]=BETA | param[2]=GAMMA | param[3]=MU
        return (param[1]/(2*param[0]*param[2]*(1/param[1]))) * \
               np.exp(-(np.abs(x-param[3])/param[0])**param[1])

    def __call__(self, data, bins):
        self.p0 = [np.std(data), 1, 1, np.mean(data)]
        # First guess
        if len(bins)>1:
            super(GND_fit,self).__call__(data=data,
                                         bins=bins,
                                         guess=self.p0,
                                         fit_func=self.GND)

    def plot(self,axis,title,xlabel,ylabel,res=True,fit=True):
        axis.hist(self.data, self.bins, align='mid', facecolor='green')
        axis.set_xlabel(xlabel)
        axis.set_ylabel(ylabel)
        axis.set_title(title)
        if (fit==True):
            axis.plot(self.bin_centers, self.hist_fit, 'r--', linewidth=1)
            if (res==True):
                mu = self.coeff[3]; mu_err = self.perr[3]
                sigma = self.coeff[0]*np.sqrt(3) ; sigma_err = np.sqrt(3)*self.perr[0]

                # Wikipedia
                # NOTE:Try to include CHI_SQUARE
                half_p_dx = self.bin_centers[np.abs(self.hist_fit.astype('float') - np.max(self.hist_fit).astype('float')/2).argmin()] \
                            - self.bin_centers[np.abs(self.hist_fit.astype('float') - np.max(self.hist_fit).astype('float')).argmin()]
                FWHM = 2*half_p_dx

                axis.text(0.95,0.95, (('$\mu$=%0.2f (+/- %0.2f) \n'+\
                                     '$\sigma$=%0.2f (+/- %0.2f) \n' +\
                                     'FWHM=%0.2f (+/- %0.2f)')  %
                                        (mu , mu_err,
                                         np.absolute(sigma) , sigma_err,
                                         FWHM, 2.35*sigma_err
                                        )
                                      ),
                                         fontsize=8,
                                         verticalalignment='top',
                                         horizontalalignment='right',
                                         transform=axis.transAxes)

class gauss_fit(fitting):

    def gauss(x, *param):
        return param[0] * np.exp(-(x-param[1])**2/(2.*param[2]**2))

    def __call__(self, data, bins):

        self.p0 = [1, np.mean(data), np.std(data)]
        # First guess
        xi2_vec=[]
        if isinstance(bins,list):
            bin_range = np.arange(bins[0],bins[1]+1)
            for i in bin_range:
                super(gauss_fit,self).__call__(data=data,
                                               bins=i,
                                               guess=self.p0,
                                               fit_func=self.gauss1)
                xi2_vec.append(self.xi2)
                argmin_xi2 = np.argmin(xi2_vec)

            super(gauss_fit,self).__call__(data=data,
                                           bins=bin_range[argmin_xi2],
                                           guess=self.p0,
                                           fit_func=self.gauss)
        else:
            super(gauss_fit,self).__call__(data=data,
                                           bins=bins,
                                           guess=self.p0,
                                           fit_func=self.gauss1)

    def plot(self,axis,title,xlabel,ylabel,res=True,fit=True):
        axis.hist(self.data, self.bins, align='mid', facecolor='green', edgecolor='white', linewidth=0.5)
        axis.set_xlabel(xlabel)
        axis.set_ylabel(ylabel)
        axis.set_title(title)
        if (fit==True):
            axis.plot(self.bin_centers, self.hist_fit, 'r--', linewidth=1)
            if (res==True):
                axis.text(0.95,0.95, (('$\mu$=%0.3f (+/- %0.3f) \n'+\
                                     '$\sigma$=%0.3f (+/- %0.3f) \n'+
                                     'FWHM=%0.3f (+/- %0.3f) \n'+\
                                     'Res=%0.3f%% (+/- %0.3f) \n'+\
                                     'chi2=%0.3f \n'+'chi2inv_95=%0.3f \n'+\
                                     'p=%0.3f') % \
                                        (self.coeff[1] , self.perr[1],
                                         np.absolute(self.coeff[2]) , self.perr[2],
                                         2.35*np.absolute(self.coeff[2]),
                                         2.35*np.absolute(self.perr[2]),
                                         2.35*np.absolute(self.coeff[2])*100/self.coeff[1],
                                         2.35*np.absolute(self.coeff[2])*100/self.coeff[1]*
                                         np.sqrt((self.perr[2]/self.coeff[2])**2+
                                                 (self.perr[1]/self.coeff[1])**2),
                                         self.xi2,
                                         chi2.ppf(0.95,len(self.bin_centers)-2-1),
                                         self.p
                                        )
                                      ),
                                         fontsize=8,
                                         verticalalignment='top',
                                         horizontalalignment='right',
                                         transform=axis.transAxes)


            else:
                # No resolution calculation
                axis.text(0.95,0.95, (('$\mu$=%0.3f (+/- %0.3f) \n'+\
                                     '$\sigma$=%0.3f (+/- %0.3f) \n'+
                                     'FWHM=%0.3f (+/- %0.3f) \n'+\
                                     'chi2=%0.3f \n'+'chi2inv_95=%0.3f \n'+\
                                     'p=%0.3f') % \
                                        (self.coeff[1], self.perr[1],
                                         np.absolute(self.coeff[2]), self.perr[2],
                                         2.35*np.absolute(self.coeff[2]),
                                         2.35*np.absolute(self.perr[2]),
                                         self.xi2,
                                         chi2.ppf(0.95,len(self.bin_centers)-2-1),
                                         self.p)),
                                         fontsize=8,
                                         verticalalignment='top',
                                         horizontalalignment='right',
                                         transform=axis.transAxes)

class gauss_fit2(fitting):

    def gauss2(x, *param):
        return param[0] * np.exp(-(x-param[1])**2/(2.*param[2]**2)) + \
               param[3] * np.exp(-(x-param[4])**2/(2.*param[5]**2))

    def __call__(self, data, mu_guess, bins):
        self.p0 = [100, mu_guess[0], mu_guess[2], 100, mu_guess[1], mu_guess[3]]
        # First guess
        super(gauss_fit2,self).__call__(data=data,
                                       bins=bins,
                                       guess=self.p0,
                                       fit_func=self.gauss2)

    def plot(self,axis,title,xlabel,ylabel,res=True):
        axis.hist(self.data, self.bins, facecolor='green')
        axis.plot(self.bin_centers, self.hist_fit, 'r--', linewidth=1)
        axis.set_xlabel(xlabel)
        axis.set_ylabel(ylabel)
        axis.set_title(title)
        if (res==True):
            axis.text(0.05,0.8, (('$\mu1$=%0.1f (+/- %0.1f) \n'+\
                                 '$\sigma1$=%0.1f (+/- %0.1f) \n'+
                                 'FWHM1=%0.1f (+/- %0.1f) \n'+\
                                 'Res1=%0.1f%% (+/- %0.1f)') % \
                                    (self.coeff[1] , self.perr[1],
                                     np.absolute(self.coeff[2]) , self.perr[2],
                                     2.35*np.absolute(self.coeff[2]),
                                     2.35*np.absolute(self.perr[2]),
                                     2.35*np.absolute(self.coeff[2])*100/self.coeff[1],
                                     2.35*np.absolute(self.coeff[2])*100/self.coeff[1]*
                                     np.sqrt((self.perr[2]/self.coeff[2])**2+
                                             (self.perr[1]/self.coeff[1])**2)
                                    )
                                  ),
                                     fontsize=6,
                                     verticalalignment='top',
                                     horizontalalignment='left',
                                     transform=axis.transAxes)

            axis.text(0.05,1.0, (('$\mu2$=%0.1f (+/- %0.1f) \n'+\
                                 '$\sigma2$=%0.1f (+/- %0.1f) \n'+
                                 'FWHM2=%0.1f (+/- %0.1f) \n'+\
                                 'Res2=%0.1f%% (+/- %0.1f)') % \
                                    (self.coeff[4] , self.perr[4],
                                     np.absolute(self.coeff[5]) , self.perr[5],
                                     2.35*np.absolute(self.coeff[5]),
                                     2.35*np.absolute(self.perr[5]),
                                     2.35*np.absolute(self.coeff[5])*100/self.coeff[4],
                                     2.35*np.absolute(self.coeff[5])*100/self.coeff[4]*
                                     np.sqrt((self.perr[5]/self.coeff[5])**2+
                                             (self.perr[4]/self.coeff[4])**2)
                                    )
                                  ),
                                     fontsize=6,
                                     verticalalignment='top',
                                     horizontalalignment='left',
                                     transform=axis.transAxes)

        else:
            pass


def line_fit(f,X,f_sigma,x_text,y_text,title_text,n_figure,graph_sw):

# Makes a linear fit for n points (X input vector).
# f is the mean of the measured data points
# f_sigma is the standard deviation (ddof=1) of the measured data points
# The rest are attributes for the plotting windows (graph_sw = 1 to plot)
# returns coeff (A,B), perr - error for the fit param,
#         XI2_r --> Squared CHI reduced (Goodness of fit)

    def line(x, A, B):
        return A*x + B

    p0 = [1,(f[1]-f[0])/(X[1]-X[0])]
    coeff, var_matrix = curve_fit(self.line, X, f,p0=p0)

    #Parameters error estimation (sigma). See numpy user guide
    perr = np.sqrt(np.diag(var_matrix))

    Y_fit = line(X,coeff[0],coeff[1])

    XI2 = np.sum(((Y_fit-f)**2.)/(f_sigma**2.))
    XI2_r = XI2/(len(X)-2)

    max_err = np.max(np.abs((Y_fit-f)/Y_fit))*100.0

    print ('Max Linearity Error = %0.3f%%' % max_err)

    if (graph_sw==1):
    # Draws figure with all the properties

        plt.figure(n_figure)
        plt.plot(X, Y_fit, 'r--', linewidth=1)
        plt.errorbar(X, f, fmt='b*', yerr=f_sigma)
        plt.xlabel(x_text)
        plt.ylabel(y_text)
        plt.title(title_text)
        plt.figtext(0.2,0.75, ('CHI2_r = %0.3f ' % (XI2_r)))
        plt.show(block=False)
        #Fit parameters
        print ('Fitted A = ', coeff[0], '( Error_std=', perr[0],')')
        print ('Fitted B = ', coeff[1], '( Error_std=', perr[1],')')

    return coeff, perr, XI2_r

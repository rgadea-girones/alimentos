
import numpy as np
import fit_library as fit
import pandas as pd



class DATA_VIEW(object):
    def __init__(self,shared_data,txt_browser,fit_browser):
        self.sd = shared_data
        self.tb = txt_browser
        self.fit_browser = fit_browser

    def switch(self,switcher,input):
        #Switch case function
         arg = switcher.get(input, "Error in Switch Operation")
         return arg

    def append_plus(self,message):
        for text_browser in self.tb:
            text_browser.append(message)

    def append_fit(self,message):
        self.fit_browser.append(message)


    def show_measurement(self,comboBox_trazaA,comboBox_trazaB):
        self.sd.axes['ax0'].clear()
        self.sd.axes['ax1'].clear()

        traza_A = self.switch({ 0:self.sd.Z_mod_data,
                                1:self.sd.Z_fase_data,
                                2:self.sd.Err_data,
                                3:self.sd.Eri_data,
                                4:self.sd.Er_mod_data,
                                5:self.sd.Er_fase_data}, comboBox_trazaA)

        traza_B = self.switch({ 0:self.sd.Z_fase_data,
                                1:self.sd.Z_mod_data,
                                2:self.sd.Err_data,
                                3:self.sd.Eri_data,
                                4:self.sd.Er_mod_data,
                                5:self.sd.Er_fase_data}, comboBox_trazaB)


        if (self.sd.def_cfg['tipo_barrido']['value']==0):
            string_A = self.switch({0:'plot', 1:'plot', 2:'plot',
                                    3:'plot', 4:'semilogy', 5:'plot'},
                                    comboBox_trazaA)
            string_B = self.switch({0:'plot', 1:'plot', 2:'plot',
                                    3:'plot', 4:'semilogy', 5:'plot'},
                                    comboBox_trazaB)
            eval("self.sd.axes['ax0']." + string_A + "(self.sd.freq, traza_A, color='red')")
            self.sd.axes['ax0'].tick_params(axis='y', colors='red')
            eval("self.sd.axes['ax1']." + string_B + "(self.sd.freq, traza_B, color='blue')")
            self.sd.axes['ax1'].grid(True)
            self.sd.axes['ax1'].tick_params(axis='y',colors='blue')

        elif(self.sd.def_cfg['tipo_barrido']['value']==1):
            string_A = self.switch({0:'semilogx', 1:'semilogx', 2:'semilogx',
                                    3:'semilogx', 4:'loglog', 5:'semilogx'},
                                    comboBox_trazaA)
            string_B = self.switch({0:'semilogx', 1:'semilogx', 2:'semilogx',
                                    3:'semilogx', 4:'loglog', 5:'semilogx'},
                                    comboBox_trazaB)
            eval("self.sd.axes['ax0']." + string_A + "(self.sd.freq, traza_A, color='red')")
            self.sd.axes['ax0'].tick_params(axis='y',colors='red')
            eval("self.sd.axes['ax1']." + string_B + "(self.sd.freq, traza_B, color='blue')")
            self.sd.axes['ax1'].grid(True)
            self.sd.axes['ax1'].tick_params(axis='y', colors='blue')

        self.sd.fig1.tight_layout()

    def show_data(self, comboBox_trazaA, comboBox_trazaB, data):
        self.sd.axes['ax2'].cla()
        self.sd.axes['ax3'].cla()

        traza_A = self.switch({ 0:data['Z_mod'],
                                1:data['Z_Fase'],
                                2:data['Err'],
                                3:data['Eri'],
                                4:data['E_mod'],
                                5:data['E_fase']},
                                comboBox_trazaA)

        traza_B = self.switch({ 0:data['Z_Fase'],
                                1:data['Z_mod'],
                                2:data['Err'],
                                3:data['Eri'],
                                4:data['E_mod'],
                                5:data['E_fase']},
                                comboBox_trazaB)

        if (self.sd.def_cfg['tipo_barrido']['value']==0):
            string_A = self.switch({0:'plot', 1:'plot', 2:'plot',
                                    3:'plot', 4:'semilogy', 5:'plot'},
                                    comboBox_trazaA)
            string_B = self.switch({0:'plot', 1:'plot', 2:'plot',
                                    3:'plot', 4:'semilogy', 5:'plot'},
                                    comboBox_trazaB)

            eval("self.sd.axes['ax2']." + string_A + "(data['Freq'], traza_A, color='red')")
            self.sd.axes['ax2'].tick_params(axis='y', colors='red')
            eval("self.sd.axes['ax3']." + string_B + "(data['Freq'], traza_B, color='blue')")
            self.sd.axes['ax3'].grid(True)
            self.sd.axes['ax3'].tick_params(axis='y',colors='blue')

        elif(self.sd.def_cfg['tipo_barrido']['value']==1):
            string_A = self.switch({0:'semilogx', 1:'semilogx', 2:'semilogx',
                                    3:'semilogx', 4:'loglog', 5:'semilogx'},
                                    comboBox_trazaA)
            string_B = self.switch({0:'semilogx', 1:'semilogx', 2:'semilogx',
                                    3:'semilogx', 4:'loglog', 5:'semilogx'},
                                    comboBox_trazaB)
            eval("self.sd.axes['ax2']." + string_A + "(data['Freq'], traza_A, color='red')")
            self.sd.axes['ax2'].tick_params(axis='y',colors='red')
            eval("self.sd.axes['ax3']." + string_B + "(data['Freq'], traza_B, color='blue')")
            self.sd.axes['ax3'].grid(True)
            self.sd.axes['ax3'].tick_params(axis='y', colors='blue')

        self.sd.fig2.tight_layout()


    def show_data_fit(self, comboBox_trazaA, comboBox_fit_alg, data, pollo_pw=0, medida_pw=0):
        # Posición en el vector de parametros
        pos_low = np.argwhere(np.array(self.sd.def_cfg['param_fit']['names'])=='f_low_fit')[0][0]
        pos_high = np.argwhere(np.array(self.sd.def_cfg['param_fit']['names'])=='f_high_fit')[0][0]
        pos_n_func = np.argwhere(np.array(self.sd.def_cfg['param_fit']['names'])=='n_func_fit')[0][0]

        A = fit.gompertz()
        traza_A = self.switch({ 0:data['Z_mod'].to_numpy(dtype=float),
                                1:data['Z_Fase'].to_numpy(dtype=float),
                                2:data['Err'].to_numpy(dtype=float),
                                3:data['Eri'].to_numpy(dtype=float),
                                4:np.log10(data['E_mod'].to_numpy(dtype=float)),
                                5:data['E_fase'].to_numpy(dtype=float)},
                                comboBox_trazaA)

        x_data = data['Freq'].to_numpy(dtype=float)

        index_range = np.where((x_data > self.sd.def_cfg['param_fit']['value'][pos_low])*
                               (x_data < self.sd.def_cfg['param_fit']['value'][pos_high]))[0]



        param_n_func = self.sd.def_cfg['param_fit']['value'][pos_n_func]
        bounds = np.array(self.sd.def_cfg['param_fit']['limits'][3:])
        bounds_low = bounds[0:param_n_func*3+1,0]
        bounds_high = bounds[0:param_n_func*3+1,1]
        # print([bounds_low.tolist(),bounds_high.tolist()])
        # print(self.sd.def_cfg['param_fit']['value'][3:4+3*(param_n_func)])

        A(np.log10(traza_A[index_range]),
               np.log10(x_data[index_range]),
               param_n_func,
               self.sd.def_cfg['param_fit']['value'][3:4+3*(param_n_func)],
               method = comboBox_fit_alg,
               bounds = [bounds_low.tolist(),bounds_high.tolist()]
               )

        # Main PARAMETERS
        epsilon_inf    = 10**A.coeff[0]
        epsilon_alfa   = 10**(A.coeff[0]+np.cumsum(A.coeff[1::3])-A.coeff[1::3]/2)
        # El término que resta se pone para compensar la última suma que lleva 1/2
        # y se hace algo similar para el error
        #10**(A.perr[0]+np.cumsum(A.perr[1::3])-A.perr[1::3]/2)
        f_alfa         = 10**(A.coeff[2::3]) # Pedro usa /(2.pi)


        if (np.isnan(A.perr).any()) or (np.isinf(A.perr).any()) :
            A.perr = np.zeros(np.shape(A.perr))
        # Get rid of warnings and errors due to perr NaN and Inf values

        epsilon_inf_e  = np.log(10)*(10**A.coeff[0])*np.sqrt(A.perr[0])
        epsilon_alfa_e = np.log(10)*epsilon_alfa*np.sqrt(np.cumsum(A.perr[1::3])-A.perr[1::3]*0.75)
        f_alfa_e       = np.log(10)*f_alfa*np.sqrt(A.perr[2::3])



        string0 = (("Epsilon_inf = %3.3e (+/- %3.3e) \n" ) %  (epsilon_inf, epsilon_inf_e))

        string1 = [(("Epsilon Alfa %d = %3.3e (+/- %3.3e)  \n" ) % \
                   (i+1,epsilon_alfa[i],epsilon_alfa_e[i])) for i in range(param_n_func)]

        string2 = [(("Frecuencia Alfa %d = %3.3e (+/- %3.3e)  \n" ) % \
                   (i+1,f_alfa[i],f_alfa_e[i])) for i in range(param_n_func)]


        self.append_fit("PARAMETROS \n" + str(A.coeff) + "\n")
        self.append_fit("ERROR \n" + str(A.perr) + "\n")
        self.append_fit("Goodnes of Fit - R2 = %f \n" % A.r_sqr + "\n")
        self.append_fit(string0)
        for i in range(param_n_func):
            self.append_fit(string1[i])
        for i in range(param_n_func):
            self.append_fit(string2[i])

        self.sd.axes['ax4'].cla()


        self.sd.axes['ax4'].loglog(x_data, traza_A, color='red')
        #self.sd.axes['ax4'].semilogx(data['Freq'], traza_B, color='blue')
        self.sd.axes['ax4'].loglog(x_data, 10**(A.evaluate(np.log10(x_data))), color='green')
        #self.sd.axes['ax4'].tick_params(axis='y',colors='red')
        self.sd.axes['ax4'].grid(True)

        self.sd.fig3.tight_layout()

        # Save fit information in Shared Data
        fit_data_HF = np.zeros((1,35))
        p_count = 0
        strt_p  = [0,10,20,21,24,27,28,31,34]
        strt_count = 0
        for j in [A.coeff, A.perr, [epsilon_inf], epsilon_alfa, f_alfa,
                                   [epsilon_inf_e], epsilon_alfa_e, f_alfa_e,
                                   [A.r_sqr]]:
            p_count = strt_p[strt_count]
            strt_count = strt_count = strt_count + 1

            for i in j:
                fit_data_HF[0,p_count] = i
                p_count = p_count + 1

        keys = data.keys()

        if 'Pollo' in keys:
            pollo_medida = np.array([np.array(data['Pollo'])[0],np.array(data['Medida'])[0]]).reshape(1,2)
            print("Pollo y medida",pollo_medida)
        else:
            pollo_medida = np.array([pollo_pw,medida_pw]).reshape(1,2)

        fit_data_HF = np.concatenate([pollo_medida,fit_data_HF],axis=1)

        self.sd.fit_data_frame = pd.DataFrame(fit_data_HF,
                            columns=['Pollo','Medida','A','B1','C1','D1','B2','C2','D2','B3','C3','D3',
                                     'Ae','B1e','C1e','D1e','B2e','C2e','D2e','B3e','C3e','D3e',
                                     'EPS_INF','EPS_ALFA1','EPS_ALFA2','EPS_ALFA3',
                                     'F_ALFA1','F_ALFA2','F_ALFA3',
                                     'EPS_INFe','EPS_ALFA1e','EPS_ALFA2e','EPS_ALFA3e',
                                     'F_ALFA1e','F_ALFA2e','F_ALFA3e','R2'])

    def show_data_rafa(self, comboBox_trazaA,  data,data1,data2,data3):
        self.sd.axes['ax5'].cla()
        # self.sd.axes['ax3'].cla()

        traza_A = self.switch({ 0:data['Z_mod'],
                                1:data['Z_Fase'],
                                2:data['Err'],
                                3:data['Eri'],
                                4:data['E_mod'],
                                5:data['E_fase']},
                                comboBox_trazaA)

        traza_B = self.switch({ 0:data1['Z_mod'],
                                 1:data1['Z_Fase'],
                                 2:data1['Err'],
                                 3:data1['Eri'],
                                 4:data1['E_mod'],
                                 5:data1['E_fase']},
                                 comboBox_trazaA)
        traza_C = self.switch({ 0:data2['Z_mod'],
                                 1:data2['Z_Fase'],
                                 2:data2['Err'],
                                 3:data2['Eri'],
                                 4:data2['E_mod'],
                                 5:data2['E_fase']},
                                 comboBox_trazaA)   
        traza_D = self.switch({ 0:data3['Z_mod'],
                                 1:data3['Z_Fase'],
                                 2:data3['Err'],
                                 3:data3['Eri'],
                                 4:data3['E_mod'],
                                 5:data3['E_fase']},
                                 comboBox_trazaA)                                                                

        if (self.sd.def_cfg['tipo_barrido']['value']==0):
            string_A = self.switch({0:'plot', 1:'plot', 2:'plot',
                                    3:'plot', 4:'semilogy', 5:'plot'},
                                    comboBox_trazaA)
            # string_B = self.switch({0:'plot', 1:'plot', 2:'plot',
            #                         3:'plot', 4:'semilogy', 5:'plot'},
            #                         comboBox_trazaB)

            eval("self.sd.axes['ax5']." + string_A + "(data['Freq'], traza_A, color='red')")
            self.sd.axes['ax5'].tick_params(axis='y', colors='red')
            # eval("self.sd.axes['ax3']." + string_B + "(data['Freq'], traza_B, color='blue')")
            self.sd.axes['ax5'].grid(True)
            # self.sd.axes['ax3'].tick_params(axis='y',colors='blue')

        elif(self.sd.def_cfg['tipo_barrido']['value']==1):
            string_A = self.switch({0:'semilogx', 1:'semilogx', 2:'semilogx',
                                    3:'semilogx', 4:'loglog', 5:'semilogx'},
                                    comboBox_trazaA)
            # string_B = self.switch({0:'semilogx', 1:'semilogx', 2:'semilogx',
            #                         3:'semilogx', 4:'loglog', 5:'semilogx'},
            #                         comboBox_trazaB)
            
            eval("self.sd.axes['ax5']." + string_A + "(data['Freq'], traza_A, color='green', label='vacio')")
            self.sd.axes['ax5'].tick_params(axis='y',colors='red')
            eval("self.sd.axes['ax5']." + string_A + "(data1['Freq'], traza_B, color='blue', label='agua')")
            eval("self.sd.axes['ax5']." + string_A + "(data2['Freq'], traza_C, color='orange', label='zumo')")       
            eval("self.sd.axes['ax5']." + string_A + "(data3['Freq'], traza_D, color='purple', label='sal')")       

            self.sd.axes['ax5'].legend()     
            self.sd.axes['ax5'].grid(True)
            # self.sd.axes['ax3'].tick_params(axis='y', colors='blue')

        self.sd.fig4.tight_layout()
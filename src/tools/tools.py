import numpy as np
import pandas as pd
from scipy.stats import gamma
from scipy.linalg import cholesky
from datetime import datetime


class WeatherGenerator(object):

    def __init__(self, precip, s_rad, t_min, t_max, history_dates, simulation_dates):

        self.simulation_dates_original = [i.isoformat() for i in simulation_dates]
        self.simulation_dates = [i.timetuple() for i in simulation_dates]
        self.simulated_year_days = [i.tm_yday for i in self.simulation_dates]
        self.simulated_months = [i.tm_mon for i in self.simulation_dates]

        self.history_dates = [i.timetuple() for i in history_dates]
        self.history_year_days = [i.tm_yday for i in self.history_dates]
        self.history_days = [i.tm_mday for i in self.history_dates]
        self.history_months = [i.tm_mon for i in self.history_dates]

        self.history_data = np.array(
            [
                self.history_year_days,
                self.history_days,
                self.history_months,
                precip,
                t_min,
                t_max,
                s_rad
            ]
        )

        self.limiting_measured_raifall = 0.1
        self.simulated_t_min = None
        self.simulated_t_max = None
        self.simulated_s_rad = None
        self.simulated_precip = None

    def generate_precipitation(self):
        """ Returnes a list of simulated precipitation values. """
        time1 = datetime.now()
        prob_w_d = {}
        prob_d_w = {}
        prob_dry = {}
        shape = {}
        location = {}
        scale = {}
        grouped_precip = {}
        for i in range(1, 13):
            idx = self.history_data[2, :] == i
            grouped_precip[i] = self.history_data[3][idx]

        for month in grouped_precip:
            if len(grouped_precip[month]) > 0:
                w_d, d_w, dry, sh, loc, sc = self.markov_chain_gamma_distr(
                    grouped_precip[month],
                    self.limiting_measured_raifall
                    )
                prob_w_d[month] = w_d
                prob_d_w[month] = d_w
                prob_dry[month] = dry
                shape[month] = sh
                location[month] = loc
                scale[month] = sc

        simulated_precip = []

        random_numbers = np.random.rand(len(self.simulation_dates))
        state = None
        for i, month in enumerate(self.simulated_months):
            try:
                result = self.generate_precip_series(
                    state,
                    random_numbers[i],
                    prob_w_d[month],
                    prob_d_w[month],
                    prob_dry[month],
                    shape[month],
                    location[month],
                    scale[month]
                    )
                simulated_precip.append(result)
                state = 'wet' if result > 0 else 'dry'

            except KeyError:
                return "Month # " + str(month) + " does not exist in given data"

        self.simulated_precip = np.array(simulated_precip)
        print('precipitation time')
        print(datetime.now() - time1)
        return self.simulated_precip


    def generate_temperatures(self):
        """ Generate t min, t max, sol radiation series using VAR model """
        time2 = datetime.now()
        noisy_series = {
            't_min_mean':[],
            't_min_std':[],
            't_max_mean':[],
            't_max_std':[],
            's_rad_mean':[],
            's_rad_std':[],
        }
        for i in range(1, 367):
            idx = self.history_data[0, :] == i
            grouped_t_min = self.history_data[4][idx]
            grouped_t_max = self.history_data[5][idx]
            grouped_s_rad = self.history_data[6][idx]

            noisy_series['t_min_mean'].append(grouped_t_min.mean())
            noisy_series['t_min_std'].append(grouped_t_min.std())
            noisy_series['t_max_mean'].append(grouped_t_max.mean())
            noisy_series['t_max_std'].append(grouped_t_max.std())
            noisy_series['s_rad_mean'].append(grouped_s_rad.mean())
            noisy_series['s_rad_std'].append(grouped_s_rad.std())

        noise_free_series = {i: self.fourier_noise_remove(noisy_series[i]) for i in noisy_series}

        noise_free_series_ext = self.extend_sereies(noise_free_series, self.history_year_days)

        t_min_res, t_max_res, s_rad_res = self.calculate_residuals(
            noise_free_series_ext,
            self.history_data
            )

        wet_days_idx = self.history_data[3, :] > self.limiting_measured_raifall

        A_wet, B_wet = self.calculate_AB(
            z_tmin=t_min_res[wet_days_idx],
            z_tmax=t_max_res[wet_days_idx],
            z_srad=s_rad_res[wet_days_idx]
        )
        A_dry, B_dry = self.calculate_AB(
            z_tmin=t_min_res[~wet_days_idx],
            z_tmax=t_max_res[~wet_days_idx],
            z_srad=s_rad_res[~wet_days_idx]
        )

        t_min_res_sim, t_max_res_sim, s_rad_res_sim = self.generate_residuals(
            A_wet, B_wet, A_dry, B_dry,
            self.simulated_precip,
            t_min_res[0], t_max_res[0], s_rad_res[0]
            )
        
        noise_free_series_ext = self.extend_sereies(noise_free_series, self.simulated_year_days)
        self.simulated_t_min, self.simulated_t_max, self.simulated_s_rad = \
        self.generate_temperature_series(t_min_res_sim, t_max_res_sim,
                                         s_rad_res_sim, noise_free_series_ext)
        print('temperature time')
        print(datetime.now() - time2)
        return self.simulated_t_min, self.simulated_t_max, self.simulated_s_rad



    @staticmethod
    def markov_chain_gamma_distr(precip, limiting_measured_raifall):
        """
        Returns calculated Markov probabilities of wet after dry,
        dry after wet and dry days and parameters of fitted
        gamma distribution.
        """
        number_of_dry = 0.
        number_of_wet = 0.
        wet_after_dry = 0.
        wet_after_wet = 0.
        dry_after_wet = 0.
        dry_after_dry = 0.
        only_rainy_measurements = []

        rainfall = np.array(precip) > limiting_measured_raifall

        for day in range(len(rainfall)):
            if rainfall[day] == True:
                only_rainy_measurements.append(precip[day])
                number_of_wet += 1
                if day > 0 and rainfall[day - 1] == False:
                    wet_after_dry += 1
                else:
                    wet_after_wet += 1

            else:
                number_of_dry += 1
                if day > 0 and rainfall[day - 1] == True:
                    dry_after_wet += 1
                else:
                    dry_after_dry += 1

        prob_w_d = wet_after_dry / (number_of_dry + 0.1)
        prob_d_w = dry_after_wet / (number_of_wet + 0.1)
        prob_dry = number_of_dry / (number_of_wet + number_of_dry)

        sh, loc, sc = gamma.fit(only_rainy_measurements, floc = 0)

        return prob_w_d, prob_d_w, prob_dry, sh, loc, sc

    @staticmethod
    def generate_precip_series(state, random_number, prob_w_d, 
                               prob_d_w, prob_dry, shape, location, scale):
        """ Returnes a simulated precipitation value for a single day. """
        if state == None:
            if random_number < prob_dry:
                return 0.
            else:
                return gamma.rvs(shape, scale=scale, loc=location)

        elif state == 'dry':
            if random_number < prob_w_d:
                return gamma.rvs(shape, scale=scale, loc=location)
            else:
                return 0.
        else:
            if random_number < prob_d_w:
                return 0.
            else:
                return gamma.rvs(shape, scale=scale, loc=location)

    @staticmethod
    def fourier_noise_remove(serie):
        """ Returns Fourier transformed series. """
        serie = np.fft.rfft(serie)
        serie[2:] = 0
        return np.fft.irfft(serie)

    @staticmethod
    def extend_sereies(noise_free_series, year_days):
        noise_free_series_ext = {}
        for i in noise_free_series:
            serie = np.zeros(len(year_days))
            for idx, day in enumerate(year_days):
                serie[idx] = noise_free_series[i][day-1]
            noise_free_series_ext[i] = serie
        return noise_free_series_ext

    @staticmethod
    def calculate_residuals(noise_free_series_ext, history_data):
        """ Calcuates residuals from history data. """
        t_min_res = (history_data[4] - noise_free_series_ext['t_min_mean']) \
                    * noise_free_series_ext['t_min_std']
        t_max_res = (history_data[5] - noise_free_series_ext['t_max_mean']) \
                    * noise_free_series_ext['t_max_std']
        s_rad_res = (history_data[6] - noise_free_series_ext['s_rad_mean']) \
                    * noise_free_series_ext['s_rad_std']

        return t_min_res, t_max_res, s_rad_res


    @staticmethod
    def generate_residuals(A_wet, B_wet, A_dry, B_dry, simulated_precip,
                           t_min_init, t_max_init, s_rad_init):
        """ Generates series of residuals of simulation lenght. """
        t_min_res_sim = np.zeros(len(simulated_precip))
        t_max_res_sim = np.zeros(len(simulated_precip))
        s_rad_res_sim = np.zeros(len(simulated_precip))
        t_min_res_sim[0] = t_min_init
        t_max_res_sim[0] = t_max_init
        s_rad_res_sim[0] = s_rad_init

        it_rains = simulated_precip > 0
        for i in range(1, len(simulated_precip)):
            A, B = (A_wet, B_wet) if it_rains[i] else (A_dry, B_dry)
            t_min_res_sim[i] = A[0][0] * t_min_res_sim[i-1] \
                            + A[0][1] * t_max_res_sim[i-1] \
                            + A[0][2] * s_rad_res_sim[i-1] \
                            + B[0][0] * np.random.normal() \
                            + B[0][1] * np.random.normal() \
                            + B[0][2] * np.random.normal()
            t_max_res_sim[i] = A[1][0] * t_min_res_sim[i-1] \
                            + A[1][1] * t_max_res_sim[i-1] \
                            + A[1][2] * s_rad_res_sim[i-1] \
                            + B[1][0] * np.random.normal() \
                            + B[1][1] * np.random.normal() \
                            + B[1][2] * np.random.normal()
            s_rad_res_sim[i] = A[2][0] * t_min_res_sim[i-1] \
                            + A[2][1] * t_max_res_sim[i-1] \
                            + A[2][2] * s_rad_res_sim[i-1] \
                            + B[2][0] * np.random.normal() \
                            + B[2][1] * np.random.normal() \
                            + B[2][2] * np.random.normal()

        return t_min_res_sim, t_max_res_sim, s_rad_res_sim

    @staticmethod
    def generate_temperature_series(t_min_res_sim, t_max_res_sim,
                                    s_rad_res_sim, noise_free_series_ext):
        """ Generate temperature and radiation series """

        simlated_t_min = np.zeros(len(t_min_res_sim))
        simlated_t_max = np.zeros(len(t_max_res_sim))
        simlated_s_rad = np.zeros(len(s_rad_res_sim))

        simlated_t_min = t_min_res_sim * noise_free_series_ext['t_min_std'] \
                         + noise_free_series_ext['t_min_mean']
        simlated_t_max = t_min_res_sim * noise_free_series_ext['t_max_std'] \
                         + noise_free_series_ext['t_max_mean']
        simlated_s_rad = t_min_res_sim * noise_free_series_ext['s_rad_std'] \
                         + noise_free_series_ext['s_rad_mean']

        return simlated_t_min, simlated_t_max, simlated_s_rad

    @staticmethod
    def calculate_AB(z_tmin, z_tmax, z_srad):
        """ Calculated A anb B matrices for VAR """
        X = np.vstack([z_tmin[0:],z_tmax[0:],z_srad[0:]])
        Y = np.vstack([z_tmin[1:],z_tmax[1:],z_srad[1:],z_tmin[:-1],z_tmax[:-1],z_srad[:-1]])
        M0 = np.corrcoef(X)
        M1 = np.corrcoef(Y)
        M1 = np.delete(M1[:3], [0, 1, 2], 1)
        M0_inv = np.linalg.inv(M0)
        M1_trans = M1.transpose()
        M0 = np.matrix(M0)
        M1 = np.matrix(M1)
        M0_inv = np.matrix(M0_inv)
        M1_trans = np.matrix(M1_trans)
        B_BT = M0 - M1 * M0_inv * M1_trans
        # Application of the Cholesky decomposition for calculation B*BT matrix product
        B = cholesky(B_BT, lower=True)
        A = np.array(M1 * M0_inv)

        return A, B

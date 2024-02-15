import numpy as np
from scipy.stats import beta, uniform
from matplotlib import pyplot as plt
import math
from runtime.data_classes import AggregatedTraffic


class TrafficGenerator:

    def __init__(self, simulation):
        """The expected number of arrivals (active number of devices is received from
        1)Laner, M., Svoboda, P., Nikaein, N., & Rupp, M. (2013, August). Traffic models for machine type communications.
        In ISWCS 2013; The Tenth International Symposium on Wireless Communication Systems (pp. 1-5). VDE

        2)3GPP. Study on RAN Improvement for Machine-type communications. Technical report TR 37.868, 2012

        The traffic model for packets in each MTC device is retrieved from:
        3) 3GPP, Technical specification group radio access network; Evolved Universial Terrestrial Radio Access (E-UTRAN)
        Further advances for E_UTRAN physical layer aspects (Release 9). Tech. Rep. 3GPP TR 36.814 V9.2.0, March 2017"""
        self.simulation = simulation
        print("SIMULATION SIM PARAMS")
        print(self.simulation.sim_params)
        print("max devices")
        print(self.simulation.sim_params.scenario.max_num_devices_per_scenario)
        self.nr_devices_minimum = simulation.sim_params.scenario.min_num_devices_per_scenario
        self.nr_devices_maximum = simulation.sim_params.scenario.max_num_devices_per_scenario
        self.aggregated_traffic_model = simulation.sim_params.agreggated_traffic_model
        self.simulation = simulation
        self.period = self.simulation.sim_params.num_TTI  # s
        self.beta_alpha = 3
        self.beta_beta = 4
        self.poisson_lambda = 0.1
        self.exponential_mean = 5  # ms
        self.exponential_lambda = 0.2
        self.logNormal_mu = 10
        self.logNormal_sigma = 1
        self.LogNormal_upperlimit = 5  # Mbytes

    def traffic_per_cell_generation(self, plot_model=False):
        """Assuming that all MTC devices activate between t=0 and t=T, the random access intensity is described by
        the distribution p(t) and the total number of MTC devices in the cell is N, then the number of arrivals in
        the i-th access opportunity is given byAssuming that all MTC devices activate between t=0 and t=T,
        the random access intensity is described by the distribution p(t) and the total number of MTC devices in the
        cell is N, then the number of arrivals in the i-th access opportunity is given by: N * CDF """
        expected_nr_of_MTC_arrivals=[]
        if self.aggregated_traffic_model == AggregatedTraffic.model1:
            time_scaled = np.arange(0, self.period, 1)
            uniform_pdf_scaled = uniform.pdf(time_scaled, self.simulation.sim_params.initial_TTI,self.period)
            expected_nr_of_MTC_arrivals = uniform.cdf(time_scaled, self.simulation.sim_params.initial_TTI, self.period)
            if plot_model:
                plt.plot(time_scaled, uniform_pdf_scaled)
                plt.xlabel('Time')
                plt.ylabel('Expected number of MTC arrivals')
                plt.title(
                    'Traffic model 1 - uniform distribution')
                plt.grid()
                plt.show()
        elif self.aggregated_traffic_model == AggregatedTraffic.model2:
            time_scaled = np.arange(0, self.period, 1)
            beta_pdf_scaled = beta.pdf(time_scaled, self.beta_alpha, self.beta_beta, scale=self.period)
            expected_nr_of_MTC_arrivals = beta.cdf(time_scaled, self.beta_alpha, self.beta_beta, scale=self.period)
            if plot_model:
                plt.plot(time_scaled,beta_pdf_scaled ,
                         label='scaled 'r'$\alpha=%.1f,\ \beta=%.1f$' % (self.beta_alpha, self.beta_beta))
                plt.xlabel('Time')
                plt.ylabel('Expected number of MTC arrivals')
                plt.title(
                    'Traffic model 2 - beta distribution 'r'$\alpha=%.1f,\ \beta=%.1f$' % (self.beta_alpha, self.beta_beta))
                plt.legend(loc=0)
                plt.grid()
                plt.show()
        return expected_nr_of_MTC_arrivals

    def packet_inter_arrival_time(self):
        #if self.simulation.seed:
        #    np.random.seed(self.simulation.seed)
        """Poisson distribution mean value, specified as a nonnegative scalar. This property must be expressed in
        milliseconds. The object uses this property to calculate the packet interarrival time. """
        mean = 1. / float(self.poisson_lambda)
        inter_arrival_time = -math.log(np.random.uniform(0,1)) * mean  # random.uniform()
        return inter_arrival_time

    def file_reading_time(self, plot_reading_time=False):
        """Time interval between two consecutive file transfers, specified as a positive scalar. This porporty must
        be expressed in milliseconds.To specify a customized value for the reading time, specify this property. If you
        don not specify this property, the object uses the exponential distribution to calculate the reading time """
        pass

    def packet_size(self):
        packet_size = 200  # bits
        return packet_size


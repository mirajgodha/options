from numpy import sqrt, log, exp, pi
from scipy.stats import norm
import numpy as np

from dao.Option import OptionType


# Underlying price (per share): S;
# Strike price of the option (per share): K;
# Time to maturity (years): T;
# Continuously compounding risk-free interest rate: r;
# Volatility: sigma;

## define two functions, d1 and d2 in Black-Scholes model
def d1(S, K, T, r, sigma):
    return (log(S / K) + (r + sigma ** 2 / 2.) * T) / sigma * sqrt(T)


def d2(S, K, T, r, sigma):
    return d1(S, K, T, r, sigma) - sigma * sqrt(T)


## define the call options price function
def bs_call(S, K, T, r, sigma):
    return S * norm.cdf(d1(S, K, T, r, sigma)) - K * exp(-r * T) * norm.cdf(d2(S, K, T, r, sigma))


## define the put options price function
def bs_put(S, K, T, r, sigma):
    return K * exp(-r * T) - S + bs_call(S, K, T, r, sigma)


## define the Call_Greeks of an option
def call_delta(S, K, T, r, sigma):
    return norm.cdf(d1(S, K, T, r, sigma))


def call_gamma(S, K, T, r, sigma):
    return norm.pdf(d1(S, K, T, r, sigma)) / (S * sigma * sqrt(T))


def call_vega(S, K, T, r, sigma):
    return 0.01 * (S * norm.pdf(d1(S, K, T, r, sigma)) * sqrt(T))


def call_theta(S, K, T, r, sigma):
    return 0.01 * (-(S * norm.pdf(d1(S, K, T, r, sigma)) * sigma) / (2 * sqrt(T)) - r * K * exp(-r * T) * norm.cdf(
        d2(S, K, T, r, sigma)))


def call_rho(S, K, T, r, sigma):
    return 0.01 * (K * T * exp(-r * T) * norm.cdf(d2(S, K, T, r, sigma)))


## define the Put_Greeks of an option
def put_delta(S, K, T, r, sigma):
    return -norm.cdf(-d1(S, K, T, r, sigma))


def put_gamma(S, K, T, r, sigma):
    return norm.pdf(d1(S, K, T, r, sigma)) / (S * sigma * sqrt(T))


def put_vega(S, K, T, r, sigma):
    return 0.01 * (S * norm.pdf(d1(S, K, T, r, sigma)) * sqrt(T))


def put_theta(S, K, T, r, sigma):
    return 0.01 * (-(S * norm.pdf(d1(S, K, T, r, sigma)) * sigma) / (2 * sqrt(T)) + r * K * exp(-r * T) * norm.cdf(
        -d2(S, K, T, r, sigma)))


def put_rho(S, K, T, r, sigma):
    return 0.01 * (-K * T * exp(-r * T) * norm.cdf(-d2(S, K, T, r, sigma)))


## to calculate the volatility of a put/call option

def implied_volatility(option_price, S, K, T, r, option: OptionType, sigma):
    """
    Volatility: sigma;
    :param option_price: Option price
    :param S: Underlying price (per share): S;
    :param K: Strike price of the option (per share): K;
    :param T: Time to maturity (days): T;
    :param r: Continuously compounding risk-free interest rate: r in %
    :param option:
    :param sigma: Volatility: sigma in %
    :return:
    """
    T = T / 365  # convert to years
    r = r / 100  # convert to decimals
    sigma = sigma / 100  # convert to decimals
    print(np.array([['option_price', 'S', 'K', 'T', 'r', 'sigma'], [option_price, S, K, T, r, sigma]]))
    if option == OptionType.CALL:
        while sigma < 1:
            Price_implied = S * norm.cdf(d1(S, K, T, r, sigma)) - K * exp(-r * T) * norm.cdf(d2(S, K, T, r, sigma))
            if option_price - (Price_implied) < 0.001:
                return round(sigma * 100, 2)
            sigma += 0.001
        return "It could not find the right volatility of the call option."
    else:
        while sigma < 1:
            Price_implied = K * exp(-r * T) - S + bs_call(S, K, T, r, sigma)
            if option_price - (Price_implied) < 0.001:
                return round(sigma * 100, 2)
            sigma += 0.001
        return "It could not find the right volatility of the put option."
    return


def test_greek():
    """
    This method just test the greeks util
    :return: 
    """
    Price = 9.75
    S = 423.30
    K = 420
    T = 25
    r = 10
    option = 'C'
    sigma = 10.94

    print("The implied volatility is " + str(implied_volatility(Price, S, K, T, r, option, sigma)) + " %.")


test_greek()

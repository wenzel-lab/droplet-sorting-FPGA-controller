ADC_BITS = 14
MAX_VOLTAGE = 1
MIN_VOLTAGE = -1

def analog_voltage(digital_voltage,signed):

    if signed:
        min_digital = -(2**ADC_BITS)/2
        max_digital = ((2**ADC_BITS)/2) - 1
    else:
        min_digital = 0
        max_digital = -(2**ADC_BITS)/2

    m = (MAX_VOLTAGE - MIN_VOLTAGE)/(max_digital-min_digital)
    n = MAX_VOLTAGE - (m*max_digital)

    if digital_voltage>max_digital or digital_voltage<min_digital:
        a_volt = 0
    else:
        a_volt = m*digital_voltage + n

    return a_volt
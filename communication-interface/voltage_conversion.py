ADC_BITS = 14       # Number of bits used for ADC conversion
MAX_VOLTAGE = 1     # Maximum analog voltage 
MIN_VOLTAGE = -1    # Minimum analog voltage

def analog_voltage(digital_voltage,signed):
    """
    Converts a digital voltage value to its corresponding analog voltage value.

    Args:
        digital_voltage (int): The digital voltage value (ADC counts).
        signed (bool): Indicates if the digital voltage is signed (True) or unsigned (False).

    Returns:
        float: The corresponding analog voltage value.
    """

    try:
        # Define the range of digital voltage based on whether it's signed or unsigned
        if signed:
            min_digital = -(2**ADC_BITS)/2
            max_digital = ((2**ADC_BITS)/2) - 1
        else:
            min_digital = 0
            max_digital = (2**ADC_BITS)

        # Linear transformation parameters
        m = (MAX_VOLTAGE - MIN_VOLTAGE)/(max_digital-min_digital)
        n = MAX_VOLTAGE - (m*max_digital)

        # Check if the digital voltage is within the valid range
        if digital_voltage>max_digital or digital_voltage<min_digital:
            a_volt = 0                          # Return 0 if digital voltage is out of range
        else:
            a_volt = m*digital_voltage + n      # Apply the transformation to get the analog voltage

        return a_volt

    except Exception as e:
        print(f"Error in analog_voltage function: {e}")
        return None



def analog_accum_voltage(digital_voltage,signed):
    """
    Converts a digital voltage value to an accumulated analog voltage value.
    Similar to the analog_voltage function, but this one doesn't check for out-of-range
    values and directly returns the transformed accumulated voltage.

    Args:
        digital_voltage (int): The digital voltage value (ADC counts).
        signed (bool): Indicates if the digital voltage is signed (True) or unsigned (False).

    Returns:
        float: The corresponding accumulated analog voltage value.
    """

    try:
        # Define the range of digital voltage based on whether it's signed or unsigned
        if signed:
            min_digital = -(2**ADC_BITS)/2
            max_digital = ((2**ADC_BITS)/2) - 1
        else:
            min_digital = 0
            max_digital = (2**ADC_BITS)

        # Linear transformation parameters
        m = (MAX_VOLTAGE - MIN_VOLTAGE)/(max_digital-min_digital)
        n = MAX_VOLTAGE - (m*max_digital)

        # Apply the transformation to get the accumulated analog voltage
        accum_volt = m*digital_voltage + n

        return accum_volt
        
    except Exception as e:
        print(f"Error in analog_accum_voltage function: {e}")
        return None
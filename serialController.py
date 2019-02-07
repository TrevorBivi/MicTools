import serial

ser = serial.Serial('COM1',9600)
while True:
    try:
        val = ser.read()
        if val[:5] == 'btUp:':
            print('button #' + val[5:] + ' released')
        elif val[:5] == 'btDn:':
            print('button #' + val[5:] + ' pressed')
            
    except (serial.SerialException, serial.SerialTimeoutException):
        continue
    

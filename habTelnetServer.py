import asyncio, telnetlib3, requests

@asyncio.coroutine
def shell(reader, writer):
    
    while True:
        writer.write('\r\nHAB Command> ')
        input = yield from reader.read(1)
        if input:
            if (input == "t"):
                # Display data
                r = requests.get('http://hab.nfaschool.org/getData')
        
                writer.write('\r\n {:<15} {:<18} {:<8} {:<8}'.format('Client ID', 'Date / Time', 'In (C)', 'Out (C)'))
                for line in r.json():
                    writer.write('\r\n {:<15} {:<18} {:<8} {:<8}'.format(line['clientID'], line['date'] + ' ' + line['time'], line['insideTemp'], line['outsideTemp']))
                
                writer.write('\r\n')
                #yield from writer.drain()
            if (input == "p"):
                r = requests.get('http://hab.nfaschool.org/getData')
        
                writer.write('\r\n {:<15} {:<18} {:<5} {:<8}'.format('Client ID', 'Date / Time', 'mBar', 'Altitude (m)'))
                for line in r.json():
                    writer.write('\r\n {:<15} {:<18} {:<5} {:<8}'.format(line['clientID'], line['date'] + ' ' + line['time'], line['pressure'], line['altitude']))
                
                writer.write('\r\n')
            if (input == "v"):
                r = requests.get('http://hab.nfaschool.org/getData')
        
                writer.write('\r\n {:<15} {:<18} {:<8} {:<8} {:<8}'.format('Client ID', 'Date / Time', 'Batt (V)', 'Solar (V)', 'Signal'))
                for line in r.json():
                    writer.write('\r\n {:<15} {:<18} {:<8} {:<8} {:<8}'.format(line['clientID'], line['date'] + ' ' + line['time'], line['batteryVoltage'], line['solarVoltage'], line['signal']))
                
                writer.write('\r\n')
            if (input == "?"):
                writer.write('\r\n Valid commands are:')
                writer.write('\r\n\r\n p: Barometric Pressure and Altitude')
                writer.write('\r\n t: Temperature Data')
                writer.write('\r\n v: Voltage Data and Signal Strength')
                writer.write('\r\n q: Quit')
            if (input == "q"):
                # Quit
                writer.write('\r\nQuitting...')
                yield from writer.drain()
                writer.close()


loop = asyncio.get_event_loop()
coro = telnetlib3.create_server(port=6023, shell=shell)
server = loop.run_until_complete(coro)
loop.run_until_complete(server.wait_closed())

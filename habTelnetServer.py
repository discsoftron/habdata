import asyncio, telnetlib3, requests

@asyncio.coroutine
def shell(reader, writer):
    
    while True:
        writer.write('\r\nHAB Command> ')
        input = yield from reader.read(1)
        if input:
            if (input == "d"):
                # Display data
                r = requests.get('http://hab.nfaschool.org/getData')
        
                writer.write('\r\n {:<15} {:<18} {:<8} {:<8} {:<5} {:<8} {:<8} {:<8}'.format('Client ID', 'Date / Time', 'In (C)', 'Out (C)', 'mBar', 'Batt (V)', 'Solar (V)', 'Signal'))
                for line in r.json():
                    writer.write('\r\n {:<15} {:<18} {:<8} {:<8} {:<5} {:<8} {:<8} {:<8}'.format(line['clientID'], line['date'] + ' ' + line['time'], line['insideTemp'], line['outsideTemp'], line['pressure'], line['batteryVoltage'], line['solarVoltage'], line['signal']))
                
                writer.write('\r\n')
                #yield from writer.drain()
            if (input == "q"):
                # Quit
                writer.write('\r\nQuitting...')
                yield from writer.drain()
                writer.close()


loop = asyncio.get_event_loop()
coro = telnetlib3.create_server(port=6023, shell=shell)
server = loop.run_until_complete(coro)
loop.run_until_complete(server.wait_closed())

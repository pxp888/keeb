import configparser

config = configparser.ConfigParser()
config['DEFAULT'] = {'ServerIP': 'tcp://10.0.0.11:64023', 'clientID': 'x'}

deviceNames = ['Keebio Keebio Iris Rev. 4', 'OLKB Planck Light']
mediaNames = ['Keebio Keebio Iris Rev. 4 Consumer Control', 'OLKB Planck Light Consumer Control']

config['server'] = {}
config.set('server', 'DeviceNames', '|'.join(deviceNames))

with open('Config.ini', 'w') as configfile:
	config.write(configfile)


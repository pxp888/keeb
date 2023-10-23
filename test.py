import configparser

config = configparser.ConfigParser()
config['DEFAULT'] = {'ServerIP': 'tcp://10.0.0.11:64023'}

deviceNames = ['Keebio Keebio Iris Rev. 4', 'OLKB Planck Light']
mediaNames = ['Keebio Keebio Iris Rev. 4 Consumer Control', 'OLKB Planck Light Consumer Control']

config.set('DEFAULT', 'DeviceNames', '|'.join(deviceNames))
config.set('DEFAULT', 'MediaNames', '|'.join(mediaNames))

with open('Config.ini', 'w') as configfile:
	config.write(configfile)


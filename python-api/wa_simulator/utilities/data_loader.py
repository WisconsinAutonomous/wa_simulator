import pathlib

DATA_DIRECTORY = str(pathlib.Path(__file__).absolute().parent.parent.parent.parent / 'data')

def GetWADataFile(filename):
	return str(pathlib.Path(DATA_DIRECTORY) / filename)
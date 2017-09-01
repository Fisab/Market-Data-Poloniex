from cx_Freeze import setup, Executable

base = None

executables = [Executable("crypt.py", base=base)]

packages = ['idna', 'time', 'json', 'requests', 'os', 'sys', 'queue', 'threading']
options = {
	'build_exe': {
		'packages':packages,
	},

}

setup(
	name = 'bittrex_downloader',
	options = options,
	version = "0.1",
	description = 'bittrex downloader market data',
	executables = executables
)


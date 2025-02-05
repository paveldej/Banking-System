from cx_Freeze import setup, Executable

executables = [Executable("main.py")]

options = {
    'build_exe': {
        'packages': [],
        'include_files': ['data']
    },
}

setup(
    name="MyProject",
    options=options,
    executables=executables
)

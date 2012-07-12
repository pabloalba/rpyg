from cx_Freeze import setup, Executable

build_exe_options = {"include_files":["actor.py","dialog.py","game.py","inventory.py","rpyg_utils.py"]}#,"zip_includes":["images/","samples/"]}#,"include_path":["images","samples"]}

#my_data_files = [("",["actor.py"]),("",["dialog.py"]),("",["game.py"]),("",["inventory.py"]),("",["rpyg_utils.py"])]

RPyGExecutable = Executable(
    script = "rpyg.py",
    initScript = None,
#    targetDir = r"build",
#    compress = False,
    copyDependentFiles = True,
    appendScriptToExe = True,
#    appendScriptToLibrary = False,
    icon = None
    )

setup(
    name = "RPyG",
    version = "0.1",
    author = "Pablo Alba Chao",
    description = "RPyG app",
    executables = [RPyGExecutable],
    options = {"build_exe":build_exe_options},
    data_files = my_data_files,
    )

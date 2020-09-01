from cx_Freeze import setup, Executable

options = {
    "build_exe": {
        "includes": ["modules.__init__",
                     "modules.background",
                     "modules.block",
                     "modules.camera",
                     "modules.components",
                     "modules.entities",
                     "modules.entitystate",
                     "modules.gamescene",
                     "modules.headsupdisplay",
                     "modules.leveljson",
                     "modules.spritesheet",
                     "modules.textureset",
                     "dev_modules.__init__",
                     "dev_modules.editorcamera",
                     "dev_modules.editorlevel",
                     "dev_modules.editorpanels",
                     "dev_modules.editorscenes",
                     "dev_modules.events"
                     ],

        "include_files": ["assets/",
                          "Level Editor Instructions.md"]
    }
}

executables = [Executable("main.py", targetName = "The Tower"),
               Executable("level_editor.py", targetName = "The Tower - Level Editor")
               ]

setup(name = "The Tower",
      version = "0.1b",
      description = "Beta release for The Tower",
      executables = executables,
      options = options
      )

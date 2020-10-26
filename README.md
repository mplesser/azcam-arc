# azcam-arc

*azcam-arc* is an *azcam* extension for Astronomical Research Cameras, Inc. gen1, gen2, and gen3 controllers. See https://www.astro-cam.com/.

## Installation

Download from github: https://github.com/mplesser/azcam-arc.git.

## Example Code

The code below is for example only.

### Controller
    controller = ControllerArc()
    controller.timing_board = "arc22"
    controller.clock_boards = ["arc32"]
    controller.video_boards = ["arc45", "arc45"]
    controller.set_boards()
    controller.utility_board = ""
    controller.utility_file = ""
    controller.pci_file = os.path.join(azcam.db.systemfolder, "dspcode", "dsppci3", "pci3.lod")
    controller.video_gain = 2
    controller.video_speed = 1

### Exposure
    exposure = ExposureArc()
    filetype = "MEF"
    exposure.filetype = azcam.db.filetypes[filetype]
    exposure.image.filetype = azcam.db.filetypes[filetype]
    exposure.set_remote_server("localhost", 6543)
    exposure.image.remote_imageserver_filename = "\\data\\imagewriter.fits"
    exposure.image.server_type = "azcam"
    exposure.set_remote_server()

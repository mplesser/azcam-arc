"""
Client-side commands for ARC controller.
"""

from azcam import api


def stop_idle():
    """
    Stop idle clocking.
    """

    s = "controller.stop_idle"
    api.server.rcommand(s)

    return


def start_idle():
    """
    Start idle clocking.
    """

    s = "controller.start_idle"
    api.server.rcommand(s)

    return


def set_bias_number(board_number, dac_number, board_type, dac_value):
    """
    Sets a bias value.
    BoardNumber is the controller board number.
    DAC is DAC number.
    Type is 'VID' or 'CLK'.
    DacValue is DAC value for voltage.
    """

    s = f"controller.set_bias_number {board_number} {dac_number} {board_type} {dac_value}"
    api.server.rcommand(s)

    return


def write_controller_memory(mem_type, board_number, address, value):
    """
    Write a word to a DSP memory location.
    Type is P, X, Y, or R memory space.
    BoardNumber is controller board number.
    Address is memory address to write.
    value is data to write.
    """

    s = f"controller.write_memory {mem_type} {board_number} {address} {value}"
    api.server.rcommand(s)

    return


def read_controller_memory(mem_type, board_number, address):
    """
    Read from DSP memory.
    Type is P, X, Y, or R memory space.
    BoardNumber is controller board number.
    Address is memory address to read.
    """

    s = f"controller.read_memory {mem_type} {board_number} {address}"
    reply = api.server.rcommand(s)

    return int(reply)


def board_command(command, board_number, arg1=-1, arg2=-1, arg3=-1, arg4=-1):
    """
    Send a specific command to an ARC controller board.
    The reply from the board is not usually 'OK', it is often 'DON' but could be data.
    Command is the board command to send.
    BoardNumber is controller board number.
    ArgN are arguments for Cmd.
    """

    s = f"controller.board_command {command} {board_number} {arg1} {arg2} {arg3} {arg4}"
    api.server.rcommand(s)

    return

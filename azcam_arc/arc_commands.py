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


def set_bias_number(
    board_number: int, dac_number: int, board_type: str, dac_value: int
):
    """
    Sets a bias value.
    Args:
        board_number: controller board number
        dac_number: DAC number
        board_type: 'VID' or 'CLK'
        dac_value: DAC value for voltage
    """

    s = f"controller.set_bias_number {board_number} {dac_number} {board_type} {dac_value}"
    api.server.rcommand(s)

    return


def write_controller_memory(mem_type: str, board_number: int, address: int, value: int):
    """
    Write a word to a DSP memory location.
    Args:
        mem_type: P, X, Y, or R memory space
        board_number: controller board number
        address: memory address to write
        value: data to write
    """

    s = f"controller.write_memory {mem_type} {board_number} {address} {value}"
    api.server.rcommand(s)

    return


def read_controller_memory(mem_type: str, board_number: int, address: int):
    """
    Read from DSP memory.
    Args:
        mem_type: P, X, Y, or R memory space
        board_number: controller board number
        address: memory address to read
    Returns:
        Value of memory
    """

    s = f"controller.read_memory {mem_type} {board_number} {address}"
    reply = api.server.rcommand(s)

    return int(reply)


def board_command(command, board_number, arg1=-1, arg2=-1, arg3=-1, arg4=-1):
    """
    Send a specific command to an ARC controller board.
    The reply from the board is not usually 'OK', it is often 'DON' but could be data.
    Args:
        command: board command to send
        board_number: controller board number
        argN: arguments for command
    """

    s = f"controller.board_command {command} {board_number} {arg1} {arg2} {arg3} {arg4}"
    api.server.rcommand(s)

    return

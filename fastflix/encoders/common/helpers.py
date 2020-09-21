# -*- coding: utf-8 -*-


class Loop:

    item = "loop"

    def __init__(self, condition, commands, dirs=(), files=(), name="", ensure_paths=()):
        self.name = name
        self.condition = condition
        self.commands = commands
        self.ensure_paths = ensure_paths
        self.dirs = dirs
        self.files = files


class Command:

    item = "command"

    def __init__(self, command, variables, internal, name="", ensure_paths=(), exe=None):
        self.name = name
        self.command = command
        self.variables = variables
        self.internal = internal
        self.ensure_paths = ensure_paths
        self.exe = exe


def start_and_input(source, ffmpeg, start_time=0, duration=None, copy_chapters=True, remove_metadata=True, **_):

    return (
        f'"{ffmpeg}" -y '
        f'{f"-ss {start_time}" if start_time else ""} '
        f'-i "{source}" '
        f'{f"-t {duration - start_time}" if duration else ""} '
        f"{'-map_metadata -1' if remove_metadata else ''} "
        f"{'-map_chapters 0' if copy_chapters else ''} "
    )


def generate_filters(**kwargs):
    crop = kwargs.get("crop")
    scale = kwargs.get("scale")
    scale_filter = kwargs.get("scale_filter", "lanczos")
    scale_width = kwargs.get("scale_width")
    scale_height = kwargs.get("scale_height")
    disable_hdr = kwargs.get("disable_hdr")
    rotate = kwargs.get("rotate")
    vflip = kwargs.get("v_flip")
    hflip = kwargs.get("h_flip")

    filter_list = []
    if crop:
        filter_list.append(f"crop={crop}")
    if scale:
        filter_list.append(f"scale={scale}:flags={scale_filter}")
    elif scale_width:
        filter_list.append(f"scale={scale_width}:-1:flags={scale_filter}")
    elif scale_height:
        filter_list.append(f"scale=-1:{scale_height}:flags={scale_filter}")
    if rotate is not None:
        if rotate < 3:
            filter_list.append(f"transpose={rotate}")
        if rotate == 4:
            filter_list.append(f"transpose=2,transpose=2")
    if vflip:
        filter_list.append("vflip")
    if hflip:
        filter_list.append("hflip")

    if disable_hdr:
        filter_list.append(
            "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,"
            "zscale=t=bt709:m=bt709:r=tv,format=yuv420p"
        )

    return ",".join(filter_list)
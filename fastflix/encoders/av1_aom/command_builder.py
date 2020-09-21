# -*- coding: utf-8 -*-
import re
import secrets
from pathlib import Path

import reusables

from fastflix.encoders.common.audio import build_audio
from fastflix.encoders.common.helpers import Command, generate_filters, start_and_input
from fastflix.encoders.common.subtitles import build_subtitle


def build(
    source,
    video_track,
    ffmpeg,
    temp_dir,
    output_video,
    bitrate=None,
    crf=None,
    audio_tracks=(),
    subtitle_tracks=(),
    row_mt=None,
    cpu_used="1",
    tile_columns="-1",
    tile_rows="-1",
    attachments="",
    extra="",
    **kwargs,
):
    filters = generate_filters(**kwargs)
    audio = build_audio(audio_tracks)
    subtitles = build_subtitle(subtitle_tracks)

    ending = "/dev/null"
    if reusables.win_based:
        ending = "NUL"

    beginning = start_and_input(source, ffmpeg, **kwargs) + (
        f"{extra} "
        f"-map 0:{video_track} "
        f"-c:v:0 libaom-av1 -strict experimental "
        f'{f"-vf {filters}" if filters else ""} '
        f"-cpu-used {cpu_used} "
        f"-tile-rows {tile_rows} "
        f"-tile-columns {tile_columns} "
    )

    if row_mt is not None:
        beginning += f"-row-mt {row_mt} "

    beginning = re.sub("[ ]+", " ", beginning)

    if bitrate:
        pass_log_file = Path(temp_dir) / f"pass_log_file_{secrets.token_hex(10)}.log"
        command_1 = f'{beginning} -passlogfile "{pass_log_file}" -b:v {bitrate} -pass 1 -an -f matroska {ending}'
        command_2 = f'{beginning} -passlogfile "{pass_log_file}" -b:v {bitrate} -pass 2 {audio} {subtitles} {attachments} "{output_video}"'
        return [
            Command(command_1, ["ffmpeg", "output"], False, name="First Pass bitrate"),
            Command(command_2, ["ffmpeg", "output"], False, name="Second Pass bitrate"),
        ]
    elif crf:
        command_1 = f'{beginning} -b:v 0 -crf {crf} {audio} {subtitles} {attachments} "{output_video}"'
        return [Command(command_1, ["ffmpeg", "output"], False, name="Single Pass CRF")]
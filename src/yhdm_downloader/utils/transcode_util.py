import ffmpeg


def transcode(output_file_name: str):
    try:
        tmp_video = ffmpeg.input(f="concat", safe=0, filename="file_list.txt")
        tmp_video = ffmpeg.output(tmp_video, c="copy", filename=output_file_name)
        ffmpeg.run(tmp_video)
        return True
    except ffmpeg._run.Error:
        return False

import ffmpeg
from pathlib import Path
from typing import Optional, Union

TEST_VIDEO_PATH = Path("../data/NINJVP_S001_S001_T001.MOV")

class VideoConverter:
    def __init__(self, input_path: Path = TEST_VIDEO_PATH):
        """
        Initialize the VideoConverter.

        Args:
            input_path: Path to the input video file. Default is TEST_VIDEO_PATH.
        """
        self.input_path = input_path
        self.probe_raw = self.get_metadata()
        self.probe = self.get_simplified_probe()

    def get_metadata(self) -> dict:
        """
        Fetch metadata of the video file using ffmpeg.probe.

        Returns:
            Dictionary containing the metadata.
        """
        try:
            probe = ffmpeg.probe(self.input_path)
        except ffmpeg.Error as e:
            print(f'Error during fetching metadata: {e.stderr.decode()}')
            raise e

        return probe

    def get_simplified_probe(self) -> dict:
        """
        Simplify the metadata to include only necessary information.

        Returns:
            Simplified dictionary of metadata.
        """
        probe = {
            'filename': self.probe_raw['format']['filename'],
            'duration': self.probe_raw['format']['duration'],
            'size': self.probe_raw['format']['size'],
            'bit_rate': self.probe_raw['format']['bit_rate'],
            'creation_time': self.probe_raw['format']['tags']['creation_time'] if 'creation_time' in self.probe_raw['format']['tags'] else None,
            'streams': []
        }

        for stream in self.probe_raw['streams']:
            new_stream = {
                'codec_name': stream['codec_name'] if 'codec_name' in stream else None,
                'codec_type': stream['codec_type'] if 'codec_type' in stream else None,
                'duration': stream['duration'] if 'duration' in stream else None,
                'bit_rate': stream['bit_rate'] if 'bit_rate' in stream else None,
                'frame_rate': stream['r_frame_rate'] if 'r_frame_rate' in stream else None,
                'color_space': stream['color_space'] if 'color_space' in stream else None,
                'color_range': stream['color_range'] if 'color_range' in stream else None,
            }
            if 'width' in stream:
                new_stream['width'] = stream['width']
            if 'height' in stream:
                new_stream['height'] = stream['height']
            
            probe['streams'].append(new_stream)
        
        return probe

    def print_metadata(self):
        """
        Print the simplified metadata of the video file.
        """
        print(f'Video duration: {self.probe["duration"]}')
        print(f'Video framerate: {self.probe["streams"][0]["frame_rate"]}')
        print(f'Video dimensions: {self.probe["streams"][0]["width"]}x{self.probe["streams"][0]["height"]}')
        print(f'Video creation time: {self.probe["creation_time"] if self.probe["creation_time"] else "Unknown"}')

    def validate_file(self) -> bool:
        """
        Validate the video file format and streams.

        Returns:
            True if the format is valid and there are video streams, False otherwise.
        """
        format = self.probe['format']['format_name']

        if format not in ["mov,mp4,m4a,3gp,3g2,mj2", "matroska,webm", "avi", "quicktime, mov", "rawvideo"]:
            print(f'Invalid format: {format}')
            return False

        video_streams = [stream for stream in self.probe['streams'] if stream['codec_type'] == 'video']
        
        if len(video_streams) == 0:
            print('No valid video stream.')
            return False

        return True

    def convert(self, output_format: str, output_path: Optional[Union[str, Path]] = None):
        """
        Convert the video file to the specified output format.

        Args:
            output_format: The output video format.
            output_path: Path to save the converted video file. If not provided, the input file name is used with the new file type suffix.

        Returns:
            None
        """
        if output_path is None:
            output_path = self.input_path.with_suffix(f'.{output_format}')
        else:
            output_path = Path(output_path)

        if self.input_path.suffix == output_path.suffix:
            print(f'Error: Input and output file types are the same ({self.input_path.suffix}). Conversion cancelled.')
            return

        try:
            stream = ffmpeg.input(str(self.input_path))
            stream = ffmpeg.output(stream, str(output_path), format=output_format)
            ffmpeg.run(stream, overwrite_output=True)
        except ffmpeg.Error as e:
            print(f'Error during conversion: {e.stderr.decode()}')
            raise e

        print(f'Successfully converted {self.input_path} to {output_path}')



    def check_result_integrity(self, output_path: Union[str, Path]) -> bool:
        """
        Check the integrity of the converted video file.

        Args:
            output_path: Path to the converted video file.

        Returns:
            True if the video file can be probed, False otherwise.
        """
        try:
            ffmpeg.probe(output_path)
        except ffmpeg.Error as e:
            print(f'Error during result checking: {e.stderr.decode()}')
            return False

        return True

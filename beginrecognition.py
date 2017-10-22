#!/usr/bin/env python

# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Cloud Speech API sample application using the streaming API.

NOTE: This module requires the additional dependency `pyaudio`. To install
using pip:

    pip install pyaudio

Example usage:
    python transcribe_streaming_mic.py
"""

# [START import_libraries]
from __future__ import division

import re
import sys
import handy

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import pyaudio
from six.moves import queue
# [END import_libraries]

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
global_out = ""

class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None) # Signal the generator to terminate
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break
            yield b''.join(data)

def listen_print_loop(responses):
    num_chars_printed = 0
    totalScript = []
    for response in responses:
        if not response.results:
            continue
        result = response.results[0]
        print(result)
        if not result.alternatives:
            continue
        transcript = result.alternatives[0].transcript
        overwrite_chars = ' ' * (num_chars_printed - len(transcript))
        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + '\r')
            sys.stdout.flush()
            num_chars_printed = len(transcript)
        else:
            print(transcript + overwrite_chars)
            if re.search(r'\b(done|dune|don)\b', transcript, re.I):
                print('Processing..')
                a = str(result)[str(result).index("transcript")+13:str(result).index("done")-1]
                text_file = open("outputtext.txt", "w")
                text_file.write(a)
                text_file.close()
                handy.testBreak()
                break
            num_chars_printed = 0
            totalScript += [transcript + overwrite_chars]

def main():
    language_code = 'en-US'  # a BCP-47 language tag
    client = speech.SpeechClient()
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)
    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)
    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)
        listen_print_loop(responses)
    

if __name__ == '__main__':
    main()

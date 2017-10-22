from pydub import AudioSegment
sounds = AudioSegment.from_wav("output.wav")
sounds = sounds.set_channels(1)
sounds.export("out2.wav", format = "wav")

def transcribe_file(speech_file):
    """Transcribe the given audio file."""
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    import io
    import json
    client = speech.SpeechClient()

    with io.open(speech_file, 'rb') as audio_file:
        content = audio_file.read()

    audio = types.RecognitionAudio(content=content)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,
        language_code='en-US')

    response = client.recognize(config, audio)
    # Print the first alternative of all the consecutive results.
    # print(json.dumps(response))
    for result in response.results:
        print('Transcript: {}'.format(result.alternatives[0].transcript))

transcribe_file("out2.wav")

#key ya29.GlzqBHVSZ965WcJ-9btV6BxbgkbrZNFasUIgwl_h2S8W8x836prUwWqQh5FEC3PFAUckN7aIwcZHa4ve7IKDJ55jf0kck0VW4VeN6QXMcnWQMpW5S4j-h06Ctecptw
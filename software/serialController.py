

class serialController():
    def __init__(self,
                 audio_path,
                 mic_input,
                                  
                 private_audio_vol,
                 private_beep_vol,
                 private_mic_vol,
                 private_rec_vol,
                 private_tts_vol,

                 private_output,
                 public_output,

                 tts_path,
                 tts_device)

        self.audio_path = audio_path
        self.mic_input = mic_input

        self.private_audio_vol = private_audio_vol
        self.private_beep_vol = private_beep_vol
        self.private_mic_vol = private_mic_vol
        self.private_rec_vol = private_rec_vol
        self.private_tts_vol = private_tts_vol

        self._state = {
            #mic
            'morph_program':,
            'morph_type':,
            'pitch':,
            'volume':,
            'morphing':,

            
            
            }

import requests
import json

class Voicevox():
    def __init__( self, host="127.0.0.1", speaker=2 ):
        self.host = host
        self.speaker = speaker
        
    def synthesis(self, text, filename  ):
        res1 = requests.post('http://' + self.host + ':50021/audio_query',
                            params={'text': text, 'speaker': self.speaker})
        res2 = requests.post('http://' + self.host + ':50021/synthesis',
                            params={'speaker': self.speaker},
                            json=res1.json())
        with open(filename, mode='wb') as f:
            f.write(res2.content)

if __name__=="__main__":
    vv = Voicevox()
    vv.synthesis("こんにちは" , "test.wav")
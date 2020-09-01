import requests
from Crypto.Cipher import AES


# req = requests.get('http://localhost:3000/highscores')
# print(req.text)
encrypter = AES.new("u8x/A?D(G+KaPdSgVkYp3s6v9y$B&E)H".encode("utf-8"), 
                    AES.MODE_CBC,
                    "LoremIpsumDolorS".encode("utf-8"))

def pad_whitespace(input):
  pad_length = (16 - (len(str(input)) % 16)) % 16
  output = str(input) + " " * pad_length
  return output

def pad(input):
  pad_length = (16 - (len(str(input)) % 16)) % 16
  output = (str(input) + (str(chr(pad_length)) * pad_length)).encode("utf-8")
  return output

post = requests.post('http://localhost:3000/highscores',
                      headers = {'User-Agent': 'The Tower - Game Client'},
                      data = {'user': encrypter.encrypt(pad(" testificated")), 'time': encrypter.encrypt(pad("0.80"))})
print(post.status_code)
print('Complete!')
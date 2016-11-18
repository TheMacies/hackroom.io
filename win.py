import time
import requests
import grequests
from bs4 import BeautifulSoup

mail = "test@test.pl" 
name = "your name"
university = "PW"

d = {693: 2, 737: 8,
     895: 4, 692: 9,
     1032: 6, 555: 6,
     724: 7, 624: 4,
     502: 3, 525: 9,
     646: 9, 446: 5,
     561: 9, 415: 2,
     663: 7, 1001: 3,
     680: 1, 353: 7,
     908: 9, 531: 6,
     252: 2, 775: 5,
     644: 4, 928: 5,
     979: 7, 774: 8,
     534: 7, 676: 2,
     1100: 4, 964: 8,
     530: 3, 348: 4,
     681: 5, 431: 1,
     729: 7, 613: 6,
     661: 8, 466: 3,
     2702: 3, 545: 8,
     582: 1, 586: 8,
     665: 5, 730: 1,
     815: 6, 205: 1,
     659: 4, 961: 2,
     512: 4, 710: 9,
     554: 4, 501: 2,
     611: 3, 510: 1, 631: 5}

proxies = {
  'http': 'http://127.0.0.1:8080',
  'https': 'http://127.0.0.1:8080',
}
headers = {"User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36"}

r = requests.get("http://www.hackroom.io",  headers=headers)
with open("output", "w") as f:
    f.write(str(r.content))

soup = BeautifulSoup(str(r.content), "lxml")
csrf_token = soup.find("meta", {"name" :"csrf-token"})["content"]

ctfuid = r.cookies['__cfduid']
escape_room_session = r.cookies["_escape_room_session"]

headers["X-CSRF-Token"] = csrf_token

t = time.time()
sumy = requests.get("http://www.hackroom.io/game_attempts/new",
                    cookies={"_escape_room_session" : escape_room_session, "__cfduid" : ctfuid},
                    headers=headers)

escape_room_session = sumy.cookies["_escape_room_session"]

sumy = sumy.json()["sums"]

lista = [[] for x in range(7)]
lista[5] = sumy[0]
lista[6] = sumy[1]

obrazki = {}

def response_handler(r, *args, **kwargs):
    number = int(r.url.split("?i=")[1])
    image_size = len(r.content)
    obrazki[number] = d[image_size]
    if number == 24:
        escape_room_session = r.cookies["_escape_room_session"]

urls = ["http://www.hackroom.io/images" + "?i=" + str(a) for a in range(25)]
rs = (grequests.get(u, cookies={"_escape_room_session" : escape_room_session, "__cfduid" : ctfuid},
                      headers=headers, callback=response_handler) for u in urls)

grequests.map(rs)

for i in range(25):
    lista[i%5].append(obrazki[i])

elapsed = time.time() - t
print(elapsed)
elapsed = time.time()



def tryCreateMatrix(columns, rows):
    for i in range(5):
        for j in range(5):
            if (columns[i][j] != rows[j][i]):
                return False
    return True


def correspondingRowsExist(columns, rsolve):
    answers = []
    answers = [(a, b, c, d, e) for a in rsolve[0] for b in rsolve[1] for c in rsolve[2] for d in rsolve[3] for e in
               rsolve[4] if (tryCreateMatrix(columns, [a, b, c, d, e]))]
    if (len(answers) == 0):
        return False
    return True

csolve = []
for i in range(5):
    csolve.append([(a, b, c, d, e) for a in [0, 1] for b in [0, 1] for c in [0, 1] for d in [0, 1] for e in [0, 1] if
                   a * lista[i][0] + b * lista[i][1] + c * lista[i][2] + d * lista[i][3] + e * lista[i][4] == lista[5][
                       i]])

rsolve = []
for i in range(5):
    rsolve.append([(a, b, c, d, e) for a in [0, 1] for b in [0, 1] for c in [0, 1] for d in [0, 1] for e in [0, 1] if
                   a * lista[0][i] + b * lista[1][i] + c * lista[2][i] + d * lista[3][i] + e * lista[4][i] == lista[6][
                       i]])

solves = [(a, b, c, d, e) for a in csolve[0] for b in csolve[1] for c in csolve[2] for d in csolve[3] for e in csolve[4]
          if (correspondingRowsExist([a, b, c, d, e], rsolve))]


answers = []
for i in range(5):
    for j in range(5):
        if solves[0][j][i] == 1:
            answers.append(j+i*5)

print(time.time() - elapsed)

r = requests.patch("http://www.hackroom.io/game_attempts/",
                   data={"answers[]":answers},
                   cookies={"_escape_room_session" : escape_room_session, "__cfduid" : ctfuid},
                    headers=headers)

escape_room_session = r.cookies["_escape_room_session"]

r = requests.post("http://www.hackroom.io/game_attempts/",
                   data={"email":mail, "name":name, "university":university},
                   cookies={"_escape_room_session" : escape_room_session, "__cfduid" : ctfuid}, headers=headers)
print (r.content)

import requests
from bs4 import BeautifulSoup
from flask import Flask, request, render_template

app = Flask(__name__)


def is_sports_person(soup):

    sports_keywords = [
        'athlete', 'player', 'striker', 'midfielder', 'defender', 'goalkeeper',
        'batsman', 'bowler', 'cricketer', 'tennis', 'basketball', 'football', 'soccer',
        'baseball', 'hockey', 'golf', 'rugby', 'olympic', 'championship', 'tournament',
        'boxing', 'wrestler', 'racing', 'swimmer', 'gymnast', 'coach', 'captain'
    ]

    paragraphs = soup.select('#mw-content-text > div > p')[:3]
    text = ' '.join([p.get_text().lower() for p in paragraphs])

    categories = soup.select('div.mw-normal-catlinks ul li a')
    category_text = ' '.join([cat.get_text().lower() for cat in categories])

    for keyword in sports_keywords:
        if keyword.lower() in text or keyword.lower() in category_text:
            return True

    infobox = soup.find('table', class_='infobox vcard') or soup.find('table', class_='infobox')
    if infobox:
        rows = infobox.find_all("tr")
        for row in rows:
            if row.th and row.td:
                header = row.th.get_text(" ", strip=True).lower()
                value = row.td.get_text(" ", strip=True).lower()

                if 'occupation' in header or 'profession' in header:
                    for keyword in sports_keywords:
                        if keyword.lower() in value:
                            return True

    return False


def get_player_stats(player_name):

    url_name = player_name.replace(" ", "_")
    url = f"https://en.wikipedia.org/wiki/{url_name}"
    response = requests.get(url)
    if response.status_code != 200:
        return None, None, f"Player page for '{player_name}' not found (Status Code: {response.status_code})."
    soup = BeautifulSoup(response.text, 'html.parser')

    if not is_sports_person(soup):
        return None, None, f"'{player_name}' does not appear to be a sports person. Please try searching for an athlete."

    infobox = soup.find('table', class_='infobox vcard') or soup.find('table', class_='infobox')
    if not infobox:
        return None, None, "No infobox found for the player."

    image_url = None
    image_element = infobox.find('img')
    if image_element and 'src' in image_element.attrs:
        image_url = 'https:' + image_element['src'] if image_element['src'].startswith('//') else image_element['src']

    stats = {}
    for row in infobox.find_all("tr"):
        if row.th and row.td:
            header = row.th.get_text(" ", strip=True)
            value = row.td.get_text(" ", strip=True)
            stats[header] = value

    return stats, image_url, None


def detect_sport(stats):

    sports_dict = {
        "Cricket": ["odi", "batting", "bowling", "wicket", "ipl", "run", "test match", "t20", "cricketer", "bowler",
                    "batsman"],
        "Football": ["cap", "goal", "midfielder", "defender", "goalkeeper", "striker", "fifa", "club", "football",
                     "soccer"],
        "Tennis": ["atp", "wta", "grand slam", "ranking", "serve", "court", "racquet", "singles", "doubles", "tennis"],
        "Basketball": ["nba", "point", "rebound", "assist", "field goal", "fiba", "dunk", "court", "basketball"],
        "Golf": ["pga", "lpga", "masters", "open championship", "course", "putt", "hole", "par", "birdie", "golf"],
        "Athletics": ["sprint", "javelin", "discus", "marathon", "hurdle", "track", "jump", "relay", "athletics"],
        "Swimming": ["freestyle", "breaststroke", "backstroke", "butterfly", "relay", "medley", "pool", "swim"],
        "Baseball": ["mlb", "baseball", "pitcher", "batter", "home run", "inning", "batting average", "rbi"],
        "Hockey": ["nhl", "hockey", "goalie", "goal", "ice hockey", "field hockey", "puck", "stick"],
        "Rugby": ["rugby", "try", "scrum", "conversion", "lineout", "ruck", "maul", "union", "league"],
        "Boxing": ["boxing", "boxer", "bout", "knockout", "ko", "tko", "round", "heavyweight", "lightweight"],
        "MMA": ["mma", "ufc", "fighter", "bout", "submission", "knockout", "octagon", "bellator"],
        "Wrestling": ["wwe", "wrestling", "wrestler", "pin", "submission", "greco-roman", "freestyle wrestling"],
        "Gymnastics": ["gymnastics", "gymnast", "vault", "beam", "bar", "floor", "routine", "artistic", "rhythmic"],
        "Cycling": ["cycling", "cyclist", "tour de france", "giro", "peloton", "bike", "mountain bike", "bmx"],
        "Skiing": ["skiing", "skier", "slalom", "downhill", "cross-country", "alpine"],
        "Snowboarding": ["snowboard", "snowboarding", "halfpipe", "big air", "slope style"],
        "Figure Skating": ["figure skating", "ice skating", "skater", "jump", "axel", "ice dance"],
        "Volleyball": ["volleyball", "setter", "spiker", "dig", "serve", "block", "libero", "spike"],
        "Badminton": ["badminton", "shuttlecock", "racket", "smash", "bwf", "singles", "doubles", "mixed doubles",
                      "all england", "net", "birdie", "rally", "clear", "drop shot", "drive", "service", "thomas cup",
                      "uber cup", "sudirman cup", "badminton world federation", "yonex", "li-ning"],
        "Table Tennis": ["table tennis", "ping pong", "paddle", "forehand", "backhand", "ittf"],
        "Formula Racing": ["formula", "f1", "formula one", "grand prix", "driver", "racing", "ferrari"],
        "NASCAR": ["nascar", "racing", "driver", "daytona", "speedway", "talladega"],
        "American Football": ["nfl", "quarterback", "touchdown", "field goal", "american football"],
        "Martial Arts": ["karate", "judo", "taekwondo", "muay thai", "kickboxing", "bjj"],
        "Surfing": ["surf", "surfer", "surfing", "wave", "pipeline", "shortboard", "longboard"],
        "Skateboarding": ["skateboarding", "skateboarder", "skateboard", "halfpipe", "vert", "street"],
        "Weightlifting": ["weightlifting", "weightlifter", "clean and jerk", "snatch", "powerlifting"],
        "Archery": ["archery", "archer", "bow", "arrow", "target", "compound", "recurve"],
        "Fencing": ["fencing", "foil", "epee", "sabre", "bout", "touche"],
        "Rowing": ["rowing", "rower", "crew", "sculling", "regatta", "oar"],
        "Sailing": ["sailing", "sailor", "yacht", "regatta", "america's cup"],
        "Diving": ["diving", "diver", "platform", "springboard", "synchronized diving"],
        "Water Polo": ["water polo", "goalkeeper", "driver", "hole set"],
        "Handball": ["handball", "goalkeeper", "backcourt", "playmaker"],
        "Squash": ["squash", "racquet", "court", "psa"],
        "Lacrosse": ["lacrosse", "midfielder", "attack", "defense", "goalie"],
        "Polo": ["polo", "chukker", "mallet", "pony"],
        "Curling": ["curling", "skip", "sweeping", "stone", "house"],
        "Esports": ["esports", "gamer", "gaming", "league of legends", "dota", "counter-strike"]
    }

    for key in stats:
        if key.lower() == 'sport':
            return stats[key]

    for key, value in stats.items():
        key_lower = key.lower()
        value_lower = value.lower()

        if 'occupation' in key_lower or 'profession' in key_lower or 'category' in key_lower:
            for sport, keywords in sports_dict.items():
                for keyword in keywords:
                    if keyword in value_lower:
                        return sport

        if 'sport' in key_lower or 'discipline' in key_lower or 'event' in key_lower:
            for sport, keywords in sports_dict.items():
                for keyword in keywords:
                    if keyword in value_lower:
                        return sport

    all_text = ' '.join([f"{k} {v}".lower() for k, v in stats.items()])

    for sport, keywords in sports_dict.items():
        for keyword in keywords:
            if keyword.lower() in all_text:
                return sport

    return "Unknown"


@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")


@app.route('/player', methods=['POST'])
def player():
    player_name = request.form.get('player_name').strip()
    stats, image_url, error = get_player_stats(player_name)
    if error:
        return render_template("index.html", error=error)
    sport = detect_sport(stats)
    return render_template("player.html", player_name=player_name, stats=stats, sport=sport, image_url=image_url)


if __name__ == '__main__':
    app.run(debug=True)
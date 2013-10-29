import urllib2
import json
import re
import xml.etree.ElementTree as ET
from HTMLParser import HTMLParser


def clean(unclean):
    return re.sub(r"^\s+|\s+$","", unclean)

class ScoreBoard(HTMLParser):
    def __init__(self):
        self.match_state = {}
        HTMLParser.__init__(self)
        self.flag = 0
        self.data = []
        self.team_name = "bangladesh"
        self.url = self._extract_match_url('http://static.cricinfo.com/rss/livescores.xml')

    def handle_starttag(self, tag, attrs):
        self.flag = 0
        if (tag == "title"):
            self.flag = 1

    def handle_data(self, data):
        if(self.flag == 1):
            self.data.append(data)
        self.flag = 0

    def _extract_match_url(self, url):
        html = self.wget(url)
        root = ET.fromstring(html)
        companion_url = "http://www.espncricinfo.com/ci/engine/match/companion/data/main.json"
        return "".join([ companion_url  if "companion" in item.find('./title').text.lower() else item.find('./link').text for item in root.findall('./channel/item') if self.team_name in item.find('./title').text.lower() ])

    def wget(self, url):
        req = urllib2.Request(url)
        response = urllib2.urlopen(req, timeout=55)
        return response.read()

    def get_score_card(self, unformatted):
        self.match_state = {'team':{}, 'batsmen': {}, 'bowler': {}}
        parsed = re.match(r"([^\(]+)\(([^\)]+)\)([^|]+).*", unformatted)
        team = re.match(r"([^\d]+)(\d+)(\/(\d))?", parsed.group(1))
        overs = re.match(r"([\d\.]+) ov", parsed.group(2))
        self.match_state['team']={'team_name': clean(team.group(1)), 'runs': int(team.group(2)), 'wickets': int(team.group(4)), 'overs': float(overs.group(1)) }
        self.match_state['status'] = parsed.group(3)
        for details in [ re.match(r"([^\d]+)(\d+)(\/(\d))?",player) for player in parsed.group(2).split(',') if ' ov' not in player ]:
            self.match_state[ 'bowler' if details.group(4) else 'batsmen' ][ clean(details.group(1)) ] = details.group(2) + ( details.group(3) or "" )


class Displayer:
    def __init__(self):     # TODO: Config reader
        self.old_score = {}
        self.event = ""

    def display(self, score):
        board = score.match_state['team']
        print score.match_state
        if self.old_score and board['overs'] != self.old_score['team']['overs']:
            title = board['team_name'] + " " + str(board['runs']) + "/" + str(board['wickets']) +" Overs: " + str(board['overs'])
            message = "\n".join([ "%s: %s" % (k,str(v)) for k,v in score.match_state['batsmen'].iteritems() ])
            submessage = self.get_submessage(score.match_state)
            print title
            print message
            print submessage
            print "*" * 20
        self.old_score = score.match_state

    def match_delay(self, latest):
        return latest['status'] if latest['status'] != self.old_score['status'] and re.match(r"^\s+$",latest['status']) else None

    def wicket_gone(self, latest):
        if latest['team']['wickets'] - self.old_score['team']['wickets'] > 0:
            self.event = 1
            out_batsman = "".join([ k for k in self.old_score['batsmen'].keys() if k not in latest['batsmen'].keys() ])
            return out_batsman + "(" + self.old_score['batsmen'][out_batsman]  + ") got OUT by " + latest['bowler'].keys()[0] + "(" + latest['bowler'].values()[0] + ")"
        return None

    def runs_taken(self, latest):
        self.event = runs_taken = latest['team']['runs'] - self.old_score['team']['runs']
        who = " ".join([ man for man, run in latest['batsmen'].iteritems() if self.old_score['batsmen'].has_key(man) if int(run) - (int(self.old_score['batsmen'][man])) ])
        return latest['bowler'].keys()[0] + " to " + who + str(runs_taken) if runs_taken else None

    def get_submessage(self, score):
        submsg = (self.match_delay(score) or  self.wicket_gone(score) or self.runs_taken(score) )
        return submsg if submsg else ""


class LiveCricket:
    def __init__(self):
        self.scoreboard = ScoreBoard()
        self.displayer = Displayer()

    def notify(self, bubble):
        unformatted = ""
        if "main.json" in self.scoreboard.url:
            match_json = self.scoreboard.wget(self.scoreboard.url)
            jsoned = json.loads(match_json)
            unformatted = jsoned[0]['current_summary']
        else:
            self.scoreboard.feed(self.scoreboard.wget(self.scoreboard.url))
            unformatted = self.scoreboard.data[0]
            print "<title>: " + unformatted
        self.scoreboard.get_score_card(unformatted)
        self.displayer.display(self.scoreboard)

if __name__ == "__main__":
    livecric = LiveCricket()
    f = open("/Users/knamasi/workspace/desktopnotify/server/jsonop", "r")
    for line in f:
        jsoned = json.loads(line)
        livecric.notify(jsoned[0]['current_summary'])

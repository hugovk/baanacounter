#!/usr/bin/env python
# encoding: utf-8
"""
Scraper to tweet the number of bikes using Helsinki's Baana
"""
from __future__ import print_function, unicode_literals

import argparse
import sys
import webbrowser

import twitter  # pip install twitter
import yaml  # pip install pyyaml
from bs4 import BeautifulSoup  # pip install BeautifulSoup4

try:
    # Python 3
    from urllib.request import urlopen
except ImportError:
    # Python 2
    from urllib2 import urlopen


BAANA_LAT = 60.169173
BAANA_LONG = 24.926085


# cmd.exe cannot do Unicode so encode first
def print_it(text):
    print(text.encode("utf-8"))


def baanacounter():
    url = "https://www.hepo.fi/"
    page = urlopen(url)
    soup = BeautifulSoup(page.read())

    # <div id="text-3" class="widget widget_text">
    #   <h3>Baanalaskuri</h3>
    #   <div class="textwidget">
    #     <div id="baanalaskuri">
    #       <div id="baanascreen">
    #         <div id="baanascreentext">Tänään&nbsp; Idag</div>
    #         <div id="baanacount">201</div>
    #       </div>
    #       <div id="baanaupdate"><!--14.03.2015 11:15--></div>
    #     </div>
    #   </div>
    # </div>

    baanacount = soup.find(id="baanacount")
    count = baanacount.text
    print(count)

    try:
        baanupdate = soup.find(id="baanaupdate")
        update = baanupdate.string
        print(update)
    except:
        pass

    return count, None, None, None, None


def clean_value(value):
    return value.replace("\xa0", " ").strip()


def baanacounter2():
    url = "http://www1.infracontrol.com/cykla/data.asp?system=helsinki"
    page = urlopen(url)
    soup = BeautifulSoup(page.read(), "lxml")
    #     print(soup)

    # <table>
    # <tr>
    # <td><font size="2"> Hittills i år:</font></td><td><font size="2">47 854</font></td><td><font color="green" size="1">CO2-reduktion ca 13 207 kg <a href="http://publikationswebbutik.vv.se/shopping/ShowItem____6006.aspx" target="_blank" title="Uppskattat värde om varje resa skulle skett med bil och att varje färd är motsvarande  2 km lång med ett utsläpp på 138 g/km. Klicka för mer info på Trafikverkets hemsida">info</a></font></td>
    # </tr>
    # <td><font size="2"> Förra året:</font></td><td><font size="2">743 109</font></td><td><font color="green" size="1">CO2-reduktion ca 205 098 kg <a href="http://publikationswebbutik.vv.se/shopping/ShowItem____6006.aspx" target="_blank" title="Uppskattat värde om varje resa skulle skett med bil och att varje färd är motsvarande  2 km lång med ett utsläpp på 138 g/km. Klicka för mer info på Trafikverkets hemsida">info</a></font></td>
    # </table>

    # <table cellpadding="2" cellspacing="0" width="350">
    # <tr>
    # <td bgcolor="#808080"><font color="#FFFFFF" face="Arial" size="2">Plats</font></td>
    # <td bgcolor="#808080"><font color="#FFFFFF" face="Arial" size="2">Cyklister <br/>idag</font></td>
    # <td bgcolor="#808080"><font color="#FFFFFF" face="Arial" size="2">Samma tid <br/>1 vecka sedan</font></td>
    # <td align="center" bgcolor="#808080">
    # <font color="#FFFFFF" face="Arial" size="2">Aktuell<br/>trend</font></td>
    # </tr>
    # <tr>
    # <td><font face="Arial" size="2">  Pohjoinen Rautaiekatu:
    # </font>
    # </td><td><font face="Arial" size="2">573 </font> </td><td>
    # <font face="Arial" size="2">  213 </font> </td><td align="center">
    # <font face="Arial" size="2"> <img alt="ökande trafik" src="http://www1.infracontrol.com/images/uparrow.gif"/></font><font face="Arial" size="1"> 169%</font></td>
    # </tr>
    # </table>
    tables = soup.find_all("table")

    # Hittills i år:/So far this year:
    # tables[0].find_all('td')[0].text  # u'\xa0Hittills i \xe5r:'
    this_year = tables[0].find_all("td")[1].text  # u'47\xa0854'
    this_year = clean_value(this_year)

    last_year = tables[0].find_all("td")[4].text  # u'47\xa0854'
    last_year = clean_value(last_year)

    # tables[1].find_all('td')[4].text  # u'\xa0\xa0Pohjoinen Rautaiekatu: \r\n\n'
    today = tables[1].find_all("td")[5].text  # u'573  '
    today = clean_value(today)

    same_time_last_week = tables[1].find_all("td")[6].text  # u'\n  1022  '
    same_time_last_week = clean_value(same_time_last_week)

    trend = tables[1].find_all("td")[7].text  # u'\n  1022  '
    trend = clean_value(trend)

    return today, same_time_last_week, trend, this_year, last_year


def load_yaml(filename):
    """
    File should contain:
    consumer_key: TODO_ENTER_YOURS
    consumer_secret: TODO_ENTER_YOURS
    access_token: TODO_ENTER_YOURS
    access_token_secret: TODO_ENTER_YOURS
    """
    with open(filename) as f:
        data = yaml.safe_load(f)

    keys = data.viewkeys() if sys.version_info.major == 2 else data.keys()
    if not keys >= {"access_token", "access_token", "consumer_key", "consumer_secret"}:
        sys.exit("Twitter credentials missing from YAML: " + filename)
    return data


def save_yaml(filename, data):
    with open(filename, "w") as yaml_file:
        yaml_file.write(yaml.dump(data, default_flow_style=False))


def build_tweet(count, last_week, trend, year, last_year):
    print(count, last_week, trend, year, last_year)
    tweet = "Baana bicycle counter.\nToday: " + str(count)
    if last_week:
        tweet += "\nSame time last week: " + str(last_week)
    if trend:
        print(trend)
        if int(last_week) > int(count):
            arrow = "\u2193"  # down arrow
        elif int(count) > int(last_week):
            arrow = "\u2191"  # up arrow
        else:
            arrow = "\u2194"  # left/right arrow
        tweet += "\nTrend: " + arrow + trend
    if year:
        tweet += "\nThis year: " + str(year)
    if last_year:
        tweet += "\nLast year: " + str(last_year)
    tweet += "\n#Helsinki #pyöräily #cycling"
    return tweet


def bingo_tweet(count, last_week):
    if int(count) > 99 and count == last_week:
        print("Baana bingo!")
        print(count, last_week, year, last_year)
        tweet = "Baana bingo!\nToday: " + str(count)
        if last_week:
            tweet += "\nSame time last week: " + str(last_week)
        tweet += "\n#Helsinki #pyöräily #cycling"
        return tweet
    else:
        return None


def baana_record(count, last_record):
    if int(count) > last_record:
        print("New Baana record!")
        print(count, last_record)
        tweet = "New baana record!\nPrevious record: {}\nToday: {}".format(
            last_record, str(count)
        )
        tweet += "\n#Helsinki #pyöräily #cycling"
        return tweet
    else:
        return None


def tweet_it(string, credentials):
    if len(string) <= 0:
        return

    # Create and authorise an app with (read and) write access at:
    # https://dev.twitter.com/apps/new
    # Store credentials in YAML file
    t = twitter.Twitter(
        auth=twitter.OAuth(
            credentials["access_token"],
            credentials["access_token_secret"],
            credentials["consumer_key"],
            credentials["consumer_secret"],
        )
    )

    print_it("TWEETING THIS:\n" + string)

    if args.test:
        print("(Test mode, not actually tweeting)")
    else:
        result = t.statuses.update(
            status=string, lat=BAANA_LAT, long=BAANA_LONG, display_coordinates=True
        )
        url = (
            "http://twitter.com/"
            + result["user"]["screen_name"]
            + "/status/"
            + result["id_str"]
        )
        print("Tweeted:\n" + url)
        if not args.no_web:
            webbrowser.open(url, new=2)  # 2 = open in a new tab, if possible


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Tweet the number of bikes using Helsinki's Baana",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-y",
        "--yaml",
        default="/Users/hugo/Dropbox/bin/data/baanacounter.yaml",
        help="YAML file location containing Twitter keys and secrets",
    )
    parser.add_argument(
        "-nw",
        "--no-web",
        action="store_true",
        help="Don't open a web browser to show the tweeted tweet",
    )
    parser.add_argument(
        "-x",
        "--test",
        action="store_true",
        help="Test mode: go through the motions but don't tweet anything",
    )
    args = parser.parse_args()

    try:
        count, last_week, trend, year, last_year = baanacounter2()
        tweet = build_tweet(count, last_week, trend, year, last_year)
    except:
        count, last_week, trend, year, last_year = baanacounter()
        tweet = build_tweet(count, last_week, trend, year, last_year)

    print(len(tweet))
    # TEMP whilst the data is broken
    # Don't tweet if count is zero but others are non-zero
    if count == "0" and year != "0":
        sys.exit("DATA BROKEN, DON'T TWEET")

    data = load_yaml(args.yaml)

    print_it("Tweet this:\n" + tweet)
    tweet_it(tweet, data)

    bingo = bingo_tweet(count, last_week)
    if bingo:
        tweet_it(bingo, data)

    record = baana_record(count, data["baana_record"])
    if record:
        tweet_it(record, data)
        tweet_it("@hugovk " + record, data)
        data["baana_record"] = int(count)
        save_yaml(args.yaml, data)

# End of file

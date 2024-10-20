from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException
import matplotlib.pyplot as plt
import re
import numpy as np
import sys

def loadWithSelenium(url): #Open url with Selenium.
    while True:
        try:
            driver = webdriver.Chrome()
            driver.set_page_load_timeout(7)
            try:
                driver.get(url)
            except TimeoutException:
                print("Continuing...")
            html = driver.page_source
            driver.quit()
            return html
        except WebDriverException as e: #In case Webdriver fails.
            print("One of the pages did not load in time")
            retry = input("Would you like to try again? (yes/no) --> ")
            if retry.lower() != 'yes':
                return None

def writeHTMLToFile(url): #Write the html to a .html.
    soup = loadPage(url)
    with open('stats.html', 'w') as file:
        file.write(soup)

def getTable(): #Find player specific link from list of all Premier League players.
    with open('stats.html', 'r') as file:
        soup = bs(file, 'html.parser')
        table = soup.find_all('table')
        with open('actstat.txt', 'w') as file: #Write all player links in to a file.
            for val in table:
                rows = val.find_all('a', href=re.compile(r"^/en/players/[a-f0-9]{8}/[A-Za-z-]+$"))
                for row in rows:
                    if 'href' in row.attrs:
                        file.write(str(row) + ',\n') #Split player links with comma and newline.

def loadPage(url): #Get page HTML.
    html = loadWithSelenium(url)
    soup = str(bs(html, 'html.parser'))
    return soup

def getPlayerLink(playername): #Get general player link to eventually get player scouting report.       
    with open('actstat.txt', 'r') as file:
        filesplit = file.read().split(',')
        url = 'https://fbref.com/'
        id = 0
        for name in filesplit:
            if playername.lower() in name.lower(): #If name matches, only get a certain part of what is in the tag (We want the player link).
                end = len(name) - (len(playername) + 6)
                url += name[10:end]
                return url
                break
        return -1

def getStats(playerlink): #Create list of stats.
    writeHTMLToFile(playerlink)
    statList = []
    with open('stats.html', 'r') as file:
        soup = bs(file, 'html.parser')
        tables = soup.find_all('table', class_='stats_table sortable suppress_partial suppress_share suppress_link now_sortable')
        count = 0
        for table in tables:
            tbody = table.find('tbody')
            if tbody:
                td = tbody.find_all('td', class_='left endpoint tooltip')
                for val in td:
                    if count < 19: #Ignore rest of stats as these first 19 are the only relevant ones for this project (Player percentile compared to the rest of the Premier League).
                        statList.append(int(val['csk']))
                    else:
                        break
                    count += 1
    return statList

def plot(list1, list2, playername1, playername2): #Create bar plot for player stats.
    width = .35
    fig = plt.subplots(figsize =(8, 6))
    bar1 = np.arange(len(list1))
    bar2 = [x + width for x in bar1]
    plt.bar(bar1, list1, color='c', width=width, edgecolor='black', label=playername1.capitalize()) 
    plt.bar(bar2, list2, color='m', width=width, edgecolor='black', label=playername2.capitalize()) 
    plt.xlabel('Player Stat', fontweight ='bold', fontsize = 15) 
    plt.ylabel('Percentile', fontweight ='bold', fontsize = 15) 
    plt.title('Premier League Percentile Comparison', fontweight ='bold', fontsize = 15)
    plt.xticks([x + width for x in range(len(list1))], ['Non-Penalty Goals', 'Non-Penalty xG', 'Shots Total', 'Assists', 'Assisted Goals', 'npxG + xAG', 'Shot-Creating Actions', 'Passes Attempted', 'Pass Completion %', 'Progressive Passes', 'Progressive Carries', 'Successful Take-Ons', 'Touches', 'Progressive Passes Rec', 'Tackles', 'Interceptions', 'Blocks', 'Clearances', 'Aerials Won'])
    plt.xticks(rotation=90, fontsize='small')
    plt.tight_layout()
    plt.legend()
    plt.show() 

while True:
    while True:
        playername = str(input('Please enter a player whose stats you want to look up --> '))
        playername2 = str(input('Please enter a player to comapre them to --> '))

        #Open url and write the html to a file.
        url ='https://fbref.com/en/comps/9/stats/Premier-League-Stats#stats_squads_standard_for'
        writeHTMLToFile(url)
        getTable()

        #Get player specific links from the list of all players in Premier League.
        playerlink = getPlayerLink(playername)
        playerlink2 = getPlayerLink(playername2)
        if playerlink == -1 or playerlink2 == -1: #Error handling. Make sure player names are correct.
            print('It seems that player can not be found. Ensure the spelling is correct and that the player is in the Men\'s Premier League.')
            retry = str(input('Would you like to try again? (yes/no) --> '))
            if retry.lower() == 'yes':
                continue
            else:
                sys.exit(0)
        else:
            break
            
    #Extract player id from playerlink.
    id = playerlink[30:(len(playerlink) - len(playername) - 1)]
    id2 = playerlink2[30:(len(playerlink2) - len(playername2) - 1)]

    #Add dashes instead of spaces to match url format.
    playernamedash = playername.replace(" ", "-")
    playernamedash2 = playername2.replace(" ", "-")

    #Get scout link with player percentiles.
    scoutlink = 'https://fbref.com/en/players/' + id + '/scout/365_m1/' + playernamedash + '-Scouting-Report'
    scoutlink2 = 'https://fbref.com/en/players/' + id2 + '/scout/365_m1/' + playernamedash2 + '-Scouting-Report'

    #Retrieve player stats and percentiles.
    statsList = getStats(scoutlink)
    statsList2 = getStats(scoutlink2)

    #Plot the graph and catch errors plotting.
    work = True
    try:
        plot(statsList, statsList2, playername, playername2)
    except:
        work = False
        pass

    if work == True:
        again = str(input('Would you like to look up more player statistics? (yes/no) --> '))
        if again.lower() == 'yes':
            continue
        else:
            break
    else:
        erroragain = str(input('Something went wrong when graphing, would you like to retry? (yes/no) --> '))
        if erroragain.lower() == 'yes':
            continue
        else:
            break


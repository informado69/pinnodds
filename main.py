import os
import telegram
from selenium import webdriver
from bs4 import BeautifulSoup
import asyncio
import time
import pickle

async def main(bot, chat_id):
    driver = webdriver.Chrome()
    driver.get("https://www.pinnacle.com/pt/esports-hub/valorant/")
    time.sleep(15)

    # Carregando partidas enviadas anteriormente
    sent_matches = []
    if os.path.exists("sent_matches.pickle"):
        with open("sent_matches.pickle", "rb") as f:
            sent_matches = pickle.load(f)
            # Enviar mensagem informando que está carregando partidas
            message = "Partidas já enviadas anteriormente:"
            for match in sent_matches:
                message += f"\n{match['team1']} x {match['team2']} - Odd {match['odd1']} para a vitória de {match['team1']}, Odd {match['odd2']} para a vitória de {match['team2']}"
            await bot.send_message(chat_id=chat_id, text=message)

    while True:
        driver.refresh()
        time.sleep(5)
        
        # Obtendo as partidas e odds da página
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        elements = soup.find_all(class_="flex-row style_buttons__IdJHy style_buttons__3khJN buttons-row")
        
        old_odds = {}
        for match in sent_matches:
            old_odds[match["team1"] + " x " + match["team2"]] = {"odd1": match["odd1"], "odd2": match["odd2"]}
        
        new_matches = []
        for element in elements:
            team1 = element.find_all(class_="style_drawTeamName__23rXu")[0].text.strip()
            team2 = element.find_all(class_="style_drawTeamName__23rXu")[1].text.strip()
            odds = element.find_all(class_="style_drawPrice__nWvMQ")
            if not odds:
                continue
            odd1 = odds[0].text.strip()
            odd2 = odds[1].text.strip()
            match_str = team1 + " x " + team2
            if match_str in old_odds:
                if odd1 != old_odds[match_str]["odd1"] or odd2 != old_odds[match_str]["odd2"]:
                    # Alteração na odd
                    message = f"Alteração na odd para a partida: {match_str}\nOdd {old_odds[match_str]['odd1']} -> {odd1} para a vitória de {team1}\nOdd {old_odds[match_str]['odd2']} -> {odd2} para a vitória de {team2}"
                    await bot.send_message(chat_id=chat_id, text=message)
                    old_odds[match_str]["odd1"] = odd1
                    old_odds[match_str]["odd2"] = odd2
            else:
                # Nova partida
                message = f"Nova partida: {match_str}\nOdd {odd1} para a vitória de {team1}\nOdd {odd2} para a vitória de {team2}"
                await bot.send_message(chat_id=chat_id, text=message)
                old_odds[match_str] = {"odd1": odd1, "odd2": odd2}
                new_matches.append({"team1": team1, "team2": team2, "odd1": odd1, "odd2": odd2})
        
        # Salvando partidas enviadas
        with open("sent_matches.pickle", "wb") as f:
            pickle.dump([match for match in old_odds.values()], f)
        
        # Enviar mensagem informando que está acompanhando as partidas
        if not new_matches:
            continue
        message = "Acompanhando as partidas:"
        for match in new_matches:
            message += f"\n{match['team1']} x {match['team2']} - Odd {match['odd1']} para a vitória de {match['team1']}, Odd {match['odd2']} para a vitória de {match['team2']}"
        await bot.send_message(chat_id=chat_id, text=message)

async def run_bot():
    bot = telegram.Bot(token="6046213201:AAGkVl1gQogkX9rXgvDGtE6IuBh3trfaBjw")
    chat_id = "-1001837847156"
    while True:
        try:
            await main(bot, chat_id)
        except Exception as e:
            print(e)
        finally:
            await asyncio.sleep(15)

asyncio.run(run_bot())

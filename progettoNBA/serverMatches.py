import json
import random
import asyncio
import tornado.web
import tornado.websocket


NUM_MATCHES = 5
MATCH_DURATION = 48

with open("Teams.json") as f:
    TEAMS_DICT = json.load(f)

# Serve per la classifica globale che vive per tutta la durata del server
for team in TEAMS_DICT:
    if "points" not in TEAMS_DICT[team]:
        TEAMS_DICT[team]["points"] = 0

# Lista dei nomi delle squadre
TEAMS = list(TEAMS_DICT.keys())

# Stato globale delle partite correnti
MATCHES = []

# Lista di client WebSocket connessi (live updates)
CLIENTS = []


# Crea un nuovo set di partite
# Viene chiamata all'avvio e quando tutte le partite finiscono
def create_matches():
    global MATCHES
    MATCHES = []

    # Selezionia squadre casuali, 2 per ogni partita
    selected_teams = []
    max_teams = min(len(TEAMS), NUM_MATCHES * 2)

    while len(selected_teams) < max_teams:
        team = random.choice(TEAMS)
        if team not in selected_teams:
            selected_teams.append(team)

    match_id = 1
    for i in range(0, len(selected_teams), 2):
        if i + 1 >= len(selected_teams):
            break

        MATCHES.append({
            "id": match_id,
            "home": selected_teams[i],
            "away": selected_teams[i + 1],
            "score": {"home": 0, "away": 0},
            "time": 0,
            "status": "LIVE",
            "events": []
        })

        match_id += 1


# Genera un evento casuale
def generate_event(match):
    is_home = random.choice([True, False])
    team = match["home"] if is_home else match["away"]
    score_key = "home" if is_home else "away"

    # Peschiamo un giocatore a caso dalla squadra
    player = random.choice(TEAMS_DICT[team]["players"])

    # Punti casuali (1, 2 o 3)
    points = random.choice([1, 2, 3])

    # Aggiorniamo il punteggio
    match["score"][score_key] += points

    # Registriamo l'evento per il dettaglio partita
    match["events"].append({
        "time": match["time"],
        "team": team,
        "player": player,
        "points": points,
        "icon": "🔥"
    })


# Aggiorna il tempo, genera eventi e notifica i client WebSocket
async def update_matches():
    while True:
        all_finished = True

        for match in MATCHES:
            if match["status"] != "LIVE":
                continue

            all_finished = False
            match["time"] += 1

            # Probabilità che succeda qualcosa in questo secondo
            if random.random() < 0.2:
                generate_event(match)

            # Fine partita
            if match["time"] >= MATCH_DURATION:
                match["status"] = "FINISHED"

                hs = match["score"]["home"]
                as_ = match["score"]["away"]

                # Assegnazione punti classifica
                if hs > as_:
                    TEAMS_DICT[match["home"]]["points"] += 2
                elif as_ > hs:
                    TEAMS_DICT[match["away"]]["points"] += 2
                else:
                    TEAMS_DICT[match["home"]]["points"] += 1
                    TEAMS_DICT[match["away"]]["points"] += 1

        # Inviamo lo stato aggiornato a tutti i client connessi
        payload = json.dumps({
            "type": "UPDATE",
            "matches": MATCHES
        })

        for client in CLIENTS:
            try:
                await client.write_message(payload)
            except:
                # Se un client non risponde viene ignorato
                pass

        # Se tutte le partite sono finite, ne vengono create di nuove
        if all_finished and MATCHES:
            create_matches()

        # Tick di simulazione (1 secondo)
        await asyncio.sleep(1)


# Lista partite
class MatchListHandler(tornado.web.RequestHandler):
    async def get(self):
        # Invia semplicemente l'elenco completo dei match
        self.write(json.dumps(MATCHES))


# Dettaglio singola partita
class MatchDetailHandler(tornado.web.RequestHandler):
    async def get(self, match_id):
        # Trasforma l'id ricevuto in numero intero
        match_id = int(match_id)

        # Cicla tutti i match per trovare quello giusto
        match = None
        for m in MATCHES:
            if m["id"] == match_id:
                match = m
                break  # appena lo troviamo, usciamo dal ciclo

        # Se esiste il match, invia i dettagli come JSON
        if match:
            self.write(json.dumps(match))
        else:
            # Se non trovato, invia errore 404
            self.set_status(404)
            self.write({"error": "Match not found"})


# Classifica
class ClassificaHandler(tornado.web.RequestHandler):
    async def get(self):
        classifica = []

        # Crea la lista della classifica
        for team in TEAMS_DICT:
            classifica.append({
                "team": team,
                "points": TEAMS_DICT[team]["points"]
            })

        # Ordinamento manuale dei punti in ordine decrescente
        for i in range(len(classifica)):
            for j in range(i + 1, len(classifica)):
                if classifica[j]["points"] > classifica[i]["points"]:
                    # scambia le posizioni
                    temp = classifica[i]
                    classifica[i] = classifica[j]
                    classifica[j] = temp

        # Invia la classifica come JSON
        self.write(json.dumps(classifica)) #dati elaborati su js


# WebSocket per aggiornamenti live
class WSHandler(tornado.websocket.WebSocketHandler):
    async def open(self):
        CLIENTS.append(self)

    async def on_close(self):
        if self in CLIENTS:
            CLIENTS.remove(self)


# Configurazione dell'app Tornado
def make_app():
    return tornado.web.Application([
        (r"/matches", MatchListHandler),
        (r"/matches/([0-9]+)", MatchDetailHandler),
        (r"/standings", ClassificaHandler),
        (r"/ws", WSHandler),

        # Serve il frontend statico
        (r"/(.*)", tornado.web.StaticFileHandler, {
            "path": "frontend",
            "default_filename": "index.html"
        })
    ])


async def main():
    create_matches()

    app = make_app()
    app.listen(8888)

    print("Server avviato su http://localhost:8888")

    # Loop infinito che gestisce la simulazione
    await update_matches()


if __name__ == "__main__":
    asyncio.run(main())



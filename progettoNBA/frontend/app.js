// Crea una connessione WebSocket verso il server
var socket = new WebSocket("ws://localhost:8888/ws");


// Funzione per convertire i secondi in formato minuti:secondi
function formattaTempo(secondi) {
    var minuti = Math.floor(secondi / 60);
    var sec = secondi % 60;
    if (sec < 10) {
        sec = "0" + sec;
    }
    return minuti + ":" + sec;
}


// Funzione chiamata ogni volta che arriva un messaggio dal server
// La variabile evento.data contiene i dati mandati dal server
socket.onmessage = function(evento) {
    var dati = JSON.parse(evento.data); // Converte JSON in oggetto JS

    // Se esiste il div "matches" siamo nella home, altrimenti dettaglio match
    if (document.getElementById("matches")) {
        mostraListaMatch(dati.matches);
    } else {
        mostraDettaglioMatch(dati.matches);
    }
};


// PAGINA HOME
function mostraListaMatch(listaMatch) {

    // Recupera il contenitore dei match
    var contenitore = document.getElementById("matches");

    // Inizializza stringa vuota per HTML
    var html = "";

    // Cicla tutti i match
    for (var i = 0; i < listaMatch.length; i++) {
        var match = listaMatch[i];

        // Determina il testo e la classe dello stato della partita
        var statoTesto;
        var classeStato;
        if (match.status === "LIVE") {
            statoTesto = "LIVE";
            classeStato = "live";
        } else {
            statoTesto = "FINE";
            classeStato = "finished";
        }

        // Costruisce l'HTML della card del match
        html += '<div class="match">';
        html += '<a href="match.html?id=' + match.id + '">';
        html += '<div class="teams">' + match.home + ' vs ' + match.away + '</div>';
        html += '<div class="score">' + match.score.home + ' - ' + match.score.away + '</div>';
        html += '<div class="status">' + formattaTempo(match.time);
        html += ' <span class="' + classeStato + '">' + statoTesto + '</span>';
        html += '</div>'; // chiude status
        html += '</a>';   // chiude link
        html += '</div>'; // chiude match
    }

    // Inserisce tutto il contenuto nella pagina
    contenitore.innerHTML = html;
}


// PAGINA DETTAGLIO MATCH
function mostraDettaglioMatch(listaMatch) {

    // Legge l'id del match dai parametri URL
    var idMatch = (new URLSearchParams(window.location.search)).get("id");

    // Cerca il match corrispondente
    var match = null;
    for (var i = 0; i < listaMatch.length; i++) {
        if (listaMatch[i].id == idMatch) {
            match = listaMatch[i];
            break;
        }
    }

    // Se non esiste, esce
    if (!match) return;

    // Recupera gli elementi della pagina
    var titolo = document.getElementById("title");
    var punteggio = document.getElementById("score");
    var listaEventi = document.getElementById("events");

    // Aggiorna titolo e punteggio
    titolo.innerText = match.home + " vs " + match.away;
    punteggio.innerText = match.score.home + " - " + match.score.away +
                          " (" + formattaTempo(match.time) + ")";

    // Costruisce la lista eventi
    var eventiHTML = "";
    for (var i = 0; i < match.events.length; i++) {
        var e = match.events[i];
        eventiHTML += '<li>';
        eventiHTML += '<span class="event-icon">' + e.icon + '</span>';
        eventiHTML += '<span><strong>' + e.player + '</strong> +' + e.points;
        eventiHTML += ' <small>(' + formattaTempo(e.time) + ')</small></span>';
        eventiHTML += '</li>';
    }

    // Inserisce gli eventi nella pagina
    listaEventi.innerHTML = eventiHTML;
}


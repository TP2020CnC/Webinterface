//
// Name: Allgemein.js
// Projekt: FS4V Abschlussprojekt Staubsaugerroboter
// Schule: Heinrich-Emanuel-Merck-Schule
// Betrieb: COUNT+CARE
// Autor: Robin Schepp
// Erstellt: 2020-05-20
// Letzte Änderung: 2020-06-2
//
// Allgemeine Aufgaben wie Füllen der Statistikanzeigen werden in der Allgemein.js in Funktionen implementiert
//

//Start bei Laden der App
window.onload = function () {
    fillStatistics();
} 

//Routinen 
setInterval(fillStatistics, 5000);

// Allgemeine Steuerungsbefehle werden im separatem Worker durchgeführt
worker2 = new Worker('static/js/Steuerungsseite.js');
worker2.addEventListener('message', function(e) {
    console.log(e.data);
    if (e.data == "loesche") {
        worker2.terminate();
    }
  })
  
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//Steuerungsthreads aufrufen
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
function startRobot()
{
    worker2 = new Worker('static/js/Steuerungsseite.js');
    worker2.postMessage({'cmd': 'start'});
}
function stopRobot()
{
    worker2 = new Worker('static/js/Steuerungsseite.js');
    worker2.postMessage({'cmd': 'stop'});
}
function pauseRobot()
{
    worker2 = new Worker('static/js/Steuerungsseite.js');
    worker2.postMessage({'cmd': 'pause'});
}
function findRobot()
{
    worker2 = new Worker('static/js/Steuerungsseite.js');
    worker2.postMessage({'cmd': 'find'});
}
function setFanToWhisper()
{
    worker2 = new Worker('static/js/Steuerungsseite.js');
    worker2.postMessage({'cmd': 'whisper'});
}
function setFanToQuiet()
{
    worker2 = new Worker('static/js/Steuerungsseite.js');
    worker2.postMessage({'cmd': 'quiet'});
}
function setFanToBalanced()
{
    worker2 = new Worker('static/js/Steuerungsseite.js');
    worker2.postMessage({'cmd': 'balanced'});
}
function setFanToTurbo()
{
    worker2 = new Worker('static/js/Steuerungsseite.js');
    worker2.postMessage({'cmd': 'turbo'});
}
function setFanToMax()
{
    worker2 = new Worker('static/js/Steuerungsseite.js');
    worker2.postMessage({'cmd': 'max'});
}
function setFanToMop()
{
    worker2 = new Worker('static/js/Steuerungsseite.js');
    worker2.postMessage({'cmd': 'mop'});
}
function gohomeRobot()
{
    worker2 = new Worker('static/js/Steuerungsseite.js');
    worker2.postMessage({'cmd': 'gohome'});
}
function insertTestData()
{
    worker2 = new Worker('static/js/Steuerungsseite.js');
    worker2.postMessage({'cmd': 'test'});
}


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//Anzeigen auf der Seite werden geladen
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
function getState() {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", "/api/state", false);
    xmlHttp.send();
    return JSON.parse(xmlHttp.responseText);
    }

function fillStatistics() {
    responseForMe = getState();
    document.getElementById('gr').innerHTML = "Gr&#246sse: " + (responseForMe.clean_area / 1000000).toFixed(2) + "m&#178";
    document.getElementById('bat').innerHTML = "Batterie: " + responseForMe.battery + "%";
    //document.getElementById('bat').innerHTML = " " + responseForMe.battery + "%";
    document.getElementById('robotState').innerHTML = responseForMe.human_state;
    if (document.getElementById('fanmode')) {
        var fanmode = "";
        if (responseForMe.fan_power == 1) {
            fanmode = "whisper";
        }
        else if (responseForMe.fan_power == 38) {
            fanmode = "quiet";
        }
        else if (responseForMe.fan_power == 60) {
            fanmode = "balanced";
        }
        else if (responseForMe.fan_power == 75) {
            fanmode = "turbo";
        }
        else if (responseForMe.fan_power == 100) {
            fanmode = "max";
        }
        else if (responseForMe.fan_power == 105) {
            fanmode = "mop";
        }
        document.getElementById('fanmode').innerHTML = fanmode;
    }
}


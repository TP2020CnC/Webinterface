
//
// Name: Steuerungsseite.js
// Projekt: FS4V Abschlussprojekt Staubsaugerroboter
// Schule: Heinrich-Emanuel-Merck-Schule
// Betrieb: COUNT+CARE
// Autor: Robin Schepp
// Erstellt: 2020-05-20
// Letzte Änderung: 2020-06-2
//
// Steuerbefehle laufen im separaten Thread, um zuverlässig zu funktionieren, dies passiert hier
//

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Steuerungsthreads aufrufen Worker zum Multithreading
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Worker lausch auf Message
self.addEventListener('message', function(e) {

// Funktionen für die Steuerung des Roboters

function startRobot() {
	var xhr = new XMLHttpRequest();
	xhr.open("PUT", '/api/start', true);
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.send();
	self.postMessage("loesche");
}

function stopRobot() {
	var xhr = new XMLHttpRequest();
	xhr.open("PUT", '/api/stop', true);
	xhr.setRequestHeader("Content-Type", "application/json");  
	xhr.send(); 
	self.postMessage("loesche");
}

function pauseRobot() {
	var xhr = new XMLHttpRequest();
	xhr.open("PUT", '/api/pause', true);
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.send();
	self.postMessage("loesche");
}


function findRobot() {
	var xhr = new XMLHttpRequest();
	xhr.open("PUT", '/api/find', true);
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.send();
	self.postMessage("loesche");
}


function gohomeRobot() {
	var xhr = new XMLHttpRequest();
	xhr.open("PUT", '/api/home', true);
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.send();
	self.postMessage("loesche");
}

function setFanToQuiet() {
	var xhr = new XMLHttpRequest();
	xhr.open("PUT", '/api/quiet', true);
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.send();
	self.postMessage("loesche");
}

function setFanToBalanced() {
	var xhr = new XMLHttpRequest();
	xhr.open("PUT", '/api/balanced', true);
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.send();
	self.postMessage("loesche");
}

function setFanToTurbo() {
	var xhr = new XMLHttpRequest();
	xhr.open("PUT", '/api/turbo', true);
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.send();
	self.postMessage("loesche");
}

function setFanToMax() {
	var xhr = new XMLHttpRequest();
	xhr.open("PUT", '/api/max', true);
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.send();
	self.postMessage("loesche");
}

function setFanToMop() {
	var xhr = new XMLHttpRequest();
	xhr.open("PUT", '/api/max', true);
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.send();
	self.postMessage("loesche");
}

function setFanToWhisper() {
	var xhr = new XMLHttpRequest();
	xhr.open("PUT", '/api/whisper', true);
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.send();
	self.postMessage("loesche");
}

function insertTestData() {
	var xhr = new XMLHttpRequest();
	xhr.open("PUT", '/api/dustTest', true);
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.send();
	self.postMessage("loesche");
}

// Anhand der Daten der Message e.data.cmd... wird die jeweilige Funktion aufgerufen

if (e.data.cmd == "start") {
	startRobot();
	self.postMessage("loesche");
}
else if (e.data.cmd == "stop") {
	stopRobot();
	self.postMessage("loesche");
}
else if (e.data.cmd == "pause") {
	pauseRobot();
	self.postMessage("loesche");
}
else if (e.data.cmd == "find") {
	findRobot();
	self.postMessage("loesche");
}
else if (e.data.cmd == "whisper") {
	setFanToWhisper();
	self.postMessage("loesche");
}
else if (e.data.cmd == "quiet") {
	setFanToQuiet();
	self.postMessage("loesche");
}
else if (e.data.cmd == "balanced") {
	setFanToBalanced();
	self.postMessage("loesche");
}
else if (e.data.cmd == "turbo") {
	setFanToTurbo();
	self.postMessage("loesche");
}
else if (e.data.cmd == "mop") {
	setFanToMop();
	self.postMessage("loesche");
}
else if (e.data.cmd == "max") {
	setFanToMax();
	self.postMessage("loesche");
}
else if (e.data.cmd == "gohome") {
	gohomeRobot();
	self.postMessage("loesche");
}
else if (e.data.cmd == "test") {
	insertTestData();
	self.postMessage("loesche");
}
})

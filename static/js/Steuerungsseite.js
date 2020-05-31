


//Worker zum Multithreading
self.addEventListener('message', function(e) {


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

//Start bei Laden der App
window.onload = function () {
    fillStatistics();
} 

//Routinen 
setInterval(fillStatistics, 5000);

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


function reloadMapTime() {
    responseForMe = getState();
    if (responseForMe.human_state == "Cleaning" || responseForMe.human_state == "Returning to dock" || responseForMe.human_state == "Idle") {
        reloadMap();
    }
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

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// // In diesem Bereich wird das Laden der Karte als PNG umgesetzt --Fallback
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
function reloadMap() {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", "/api/latest", false); // false for synchronous request
    xmlHttp.send();
    // xmlHttp.open("GET", "/api/karte", false);
    // xmlHttp.send();
    // refreshImage("map", "static/maps/karte.png");
}

 function refreshImage(imgElement, imgURL) {
     var timestamp = new Date().getTime();
     var el = document.getElementById(imgElement);
     var queryString = "?t=" + timestamp;
     el.src = imgURL + queryString;
 }
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// In diesem Bereich wird die Karte aus dem Json-String für PNG erstellt --Fallback
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
function mapDrawer() {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", "/api/map", false);
    xmlHttp.send();
    mapData = JSON.parse(xmlHttp.responseText);

    //Kartendaten
    var dimensions = mapData.image.dimensions;
    var floor = mapData.image.pixels.floor;
    var obstacle_strong = mapData.image.pixels.obstacle_strong;
    var no_go_areas = mapData.forbidden_zones;

    //Roboterdaten
    if (mapData.robot) {
        var robot = mapData.robot;
    }
	if (mapData.charger) {
        var charger = mapData.charger;
    }
    path = mapData.path.points;
    position = mapData.image.position;
    current_angle = mapData.path.current_angle;

    //Icons
    var d_station = new Image();
    d_station.src = "static/maps/assets/charger.png";
    var vacuum = new Image();
    vacuum.src = "static/maps/assets/robot.png";

    //Karte
    var canvas = document.getElementById("canvas");
    canvas.width = dimensions.width;
    canvas.height = dimensions.height;
    var canvasWidth = dimensions.width ;
    var canvasHeight = dimensions.height;
    var ctx = canvas.getContext("2d");
    var canvasData = ctx.getImageData(0, 0, canvasWidth, canvasHeight);

    // That's how you define the value of a pixel //
    function drawPixel (x, y, r, g, b, a) {
        var index = (x + y * canvasWidth) * 4;

        canvasData.data[index + 0] = r;
        canvasData.data[index + 1] = g;
        canvasData.data[index + 2] = b;
        canvasData.data[index + 3] = a;
    }

    // That's how you update the canvas, so that your //
    // modification are taken in consideration //
    function updateCanvas() {
        ctx.putImageData(canvasData, 0, 0);
    }
    ////Wände
    function rectTest() {
        ctx.fillStyle = "green";
        for (let i = 0; i < obstacle_strong.length; i++) {
            var a = obstacle_strong[i];
            ctx.fillRect(a[0], a[1], 1, 1);
        }
    }
    function buildWalls() {
        for (let i = 0; i < obstacle_strong.length; i++) {
            var a = obstacle_strong[i];
            drawPixel(a[0], a[1],0, 255, 64, 255);
        }
        updateCanvas();
    }
    ////Pfad

function TransformCoords(coord, offset_from) {
    coord = coord / 50;
    coord = coord - offset_from;
    coord = coord * 4;
    return Math.round(coord);
}

    function drawPath() {
        old_x = TransformCoords(path[0][0], position.left);
        old_y = TransformCoords(path[0][1], position.top);
        ctx.strokeStyle = "#d0d3cf";
        ctx.beginPath();
        for (let i= 0; i < path.length; i++) {
            if (i == path.length - 1) {
                break
            }
            if (i % 2 == 1) {
                continue
            }
            new_x = TransformCoords(path[i + 1][0], position.left);
            new_y = TransformCoords(path[i + 1][1], position.top);
            ctx.moveTo(old_x, old_y);
            ctx.lineTo(new_x, new_y);
            ctx.stroke(); 
            old_x = new_x;
            old_y = new_y;
        }
        ctx.closePath();
    }

    function resizeTo(canvas,pct){
        var tempCanvas=document.createElement("canvas");
        var tctx=tempCanvas.getContext("2d");
        var cw=canvas.width;
        var ch=canvas.height;
        tempCanvas.width=cw;
        tempCanvas.height=ch;
        tctx.drawImage(canvas,0,0);
        canvas.width*=pct;
        canvas.height*=pct;
        var ctx=canvas.getContext('2d');
        ctx.drawImage(tempCanvas,0,0,cw,ch,0,0,cw*pct,ch*pct);
    }

    //Icons
    function drawIcons() {
        if (vacuum) {
            ctx.drawImage(vacuum,  TransformCoords(robot[0], position.left) - Math.round(vacuum.width/2), TransformCoords(robot[1], position.top) - Math.round(vacuum.width/2), vacuum.width / 4, vacuum.height / 4);
        }
    }
    buildWalls();
    //rectTest();
    resizeTo(canvas, 4);
    drawIcons();
    drawPath();
}

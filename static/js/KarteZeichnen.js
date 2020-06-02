//
// Name: KarteZeichnen.js
// Projekt: FS4V Abschlussprojekt Staubsaugerroboter
// Schule: Heinrich-Emanuel-Merck-Schule
// Betrieb: COUNT+CARE
// Autor: Robin Schepp, Yannik Seitz               
// Erstellt: 2020-05-20
// Letzte Änderung: 2020-06-2
//
// Hier befinden sich die Funktionen zum erstellen der Karte in einer Vektorgrafik mithilfe eines Canvas Elements.
//

////////////////////////////////////////////////////////////////////////////////////////////////////
//D3 Code
////////////////////////////////////////////////////////////////////////////////////////////////////
// Schmutztoleranz und ausbreitungszerfall
//
const PRIM_DECAY = 1.8;
const SEC_DECAY = 1.4;
const TOLERANCE = 60;
/////////////////////////////////////////////////////

/////
//
// Farben von Hue zu RGB konvertieren
//
function HueToRGB(h) {
	var r, g, b, i, f, p, q, t;
	var s,
		v = 1;
	if (arguments.length === 1) {
		(s = h.s), (v = h.v), (h = h.h);
	}
	i = Math.floor(h * 6);
	f = h * 6 - i;
	p = v * (1 - s);
	q = v * (1 - f * s);
	t = v * (1 - (1 - f) * s);
	switch (i % 6) {
		case 0:
			(r = v), (g = t), (b = p);
			break;
		case 1:
			(r = q), (g = v), (b = p);
			break;
		case 2:
			(r = p), (g = v), (b = t);
			break;
		case 3:
			(r = p), (g = q), (b = v);
			break;
		case 4:
			(r = t), (g = p), (b = v);
			break;
		case 5:
			(r = v), (g = p), (b = q);
			break;
	}
	return {
		r: Math.round(r * 255),
		g: Math.round(g * 255),
		b: Math.round(b * 255)
	};
}
/////////////////////////////////////////////////////
// Variablen zum Debuggen
var countRefresh = 0;
var lastRefreshTime;
var globalMapData = null;
var dragging = false;

//Für Zeichnung relevante VAriablen werden initialisiert und Zeichnen angestoßen
function parseData() {
	if (globalMapData == null) {
		return;
	}
	//Kartendaten
	dimensions = globalMapData.image.dimensions;
	floor = globalMapData.image.pixels.floor;
	obstacle_strong = globalMapData.image.pixels.obstacle_strong;
	no_go_areas = globalMapData.forbidden_zones;
	dirt = globalMapData.dirt;

	//Roboterdaten
	if (globalMapData.robot) {
		robot = globalMapData.robot;
		console.log('mapdata_Robot' + globalMapData.robot);
	}
	if (globalMapData.charger) {
		charger = globalMapData.charger;
	}
	path = globalMapData.path.points;
	position = globalMapData.image.position;
	current_angle = globalMapData.path.current_angle;

	// Init Scales
	x = d3.scaleLinear().domain([ 0, d3.max(obstacle_strong, (d) => d[0]) ]).range([ 0, width ]).nice();
	y = d3.scaleLinear().domain([ 0, d3.max(obstacle_strong, (d) => d[1]) ]).range([ 0, height ]).nice();

	console.log('Daten geladen' + countRefresh);
	countRefresh++;

	//Transformierungsdaten übertragen
	//draw(currentTransform);

	//Daten neuladen
	drawInterval();
	setTimeout(loadData, 1000);
	//setInterval(loadData, 3000);
}

// Bedingter Zeichnenaufruf
function drawInterval() {
	if (globalMapData != null && dragging == false) {
		draw(currentTransform);
	}
}

//Testet, ob Json Daten vorhanden sind
function isJson(str) {
    try {
        JSON.parse(str);
    } catch (e) {
        return false;
    }
    return true;
}

//Daten Laden
function loadData() {
	//Daten anfragen
	var timestamp = new Date().getTime();
	var xmlHttp = new XMLHttpRequest();
	xmlHttp.open('GET', `/api/map?t=${timestamp}`, false);
	xmlHttp.onload = function() {
		// Wenn Response kein richtiger Json-String wird übersprungen und in 200ms neu versucht
		if (isJson(xmlHttp.responseText) == false) {
			setTimeout(loadData, 200);
			return;
		}
		globalMapData = JSON.parse(xmlHttp.responseText);
		// Karte wird gezeichnet
		parseData();
	};
	xmlHttp.send();
	//mapData = JSON.parse(xmlHttp.responseText);
}

// Übersetzt Koordinaten
function TransformCoords(coord, offset_from) {
	coord = coord / 50;
	coord = coord - offset_from;
	coord = coord * 1;
	return Math.round(coord);
}

// Icons geladen
var d_station = new Image();
d_station.src = 'static/maps/assets/charger.svg';
var vacuum = new Image();
vacuum.src = 'static/maps/assets/robot.svg';

// Attribute gesetzt
wallColor = '#00ff40';
ICON_SIZE = 16;
margin = { top: 1, right: 1, bottom: 1, left: 1 };
var help = document.getElementById("mapBox");
outerWidth = 500;
outerHeight = 500;
width = outerWidth;
height = outerHeight;
container = d3.select('.scatter-container');

// Init SVG
const svgChart = container
	.append('svg:svg')
	// .attr('width', outerWidth)
	// .attr('height', outerHeight)
	.attr('class', 'svg-plot col-lg-10 col-md-10 col-sm-10')
	.append('g');
// .attr('transform', `translate(${margin.left}, ${margin.top})`);

// Init Canvas
const canvasChart = container
	.append('canvas')
	.attr('width', width)
	.attr('height', height)
	.style('margin-left', margin.left + 'px')
	.style('margin-top', margin.top + 'px')
	.attr('class', 'canvas-plot');

// Kontext für Canvas wird erstellt
const context = canvasChart.node().getContext('2d');

// Daten werden initial geladen
loadData();

// Es wird gecheckt, ob Dreckdaten angezeigt werden sollen
function dirtOrNoDirt() {
	// var helper = document.getElementById('toggle');
	var helper = document.getElementById('ckbx-style-9-1');
	if (helper.checked) {
		return true;
	} else {
		return false;
	}
}

// Draw plot on canvas
var currentTransform;
function draw(transform) {
	if (!transform) {
		return;
	}
	currentTransform = transform;
	console.log(transform);
	const scaleX = transform.rescaleX(x);
	const scaleY = transform.rescaleY(y);
	console.log('draw');

	context.clearRect(0, 0, 2 * width, 2 * height);
	context.fillStyle = wallColor;

	obstacle_strong.forEach((point) => {
		drawPoint(scaleX, scaleY, point, transform.k);
	});
	if (dirtOrNoDirt()) {
		drawDirt(scaleX, scaleY, transform.k);
	} else{
		drawPath(scaleX, scaleY, transform.k);
	}
	drawRobot(scaleX, scaleY, transform.k);
	drawCharger(scaleX, scaleY, transform.k);
}
// Initial draw made with no zoom
draw(d3.zoomIdentity);

//Roboterposition
function drawRobot(scaleX, scaleY, k) {
	if (globalMapData.robot) {
		let xRobo = TransformCoords(robot[0], position.left);
		let yRobo = TransformCoords(robot[1], position.top);
		const px = scaleX(xRobo);
		const py = scaleY(yRobo);
		if (vacuum) {
			//context.save(); // save current state
			//context.rotate(current_angle); // rotate
			context.drawImage(
				vacuum,
				px - Math.round(ICON_SIZE / 2) * k,
				py - Math.round(ICON_SIZE / 2) * k,
				ICON_SIZE * k,
				ICON_SIZE * k
			);
			//context.restore(); // restore original states (no rotation etc)
		}
	}
}

//Ladestationposition
function drawCharger(scaleX, scaleY, k) {
	if (globalMapData.charger) {
		let xCha = TransformCoords(charger[0], position.left);
		let yCha = TransformCoords(charger[1], position.top);
		const px = scaleX(xCha);
		const py = scaleY(yCha);
		if (d_station) {
			context.drawImage(
				d_station,
				px - Math.round(ICON_SIZE / 2) * k,
				py - Math.round(ICON_SIZE / 2) * k,
				ICON_SIZE * k,
				ICON_SIZE * k
			);
		}
	}
}

//Wände
function drawPoint(scaleX, scaleY, point, k) {
	const px = scaleX(point[0]);
	const py = scaleY(point[1]);
	const center = 1.5 * k;
	const size = 3 * k;
	context.fillRect(px - center, py - center, size, size);
}

//Pfade
function drawPath(scaleX, scaleY, k) {
	if (path != undefined && path.length > 0) {
		let old_x = TransformCoords(path[0][0], position.left);
		let old_y = TransformCoords(path[0][1], position.top);
		var px = scaleX(old_x);
		var py = scaleY(old_y);
		context.strokeStyle = '#d0d3cf';
		context.beginPath();
		for (let i = 0; i < path.length; i++) {
			if (i == path.length - 1) {
				break;
			}
			if (i % 2 == 1) {
				continue;
			}
			new_x = TransformCoords(path[i + 1][0], position.left);
			new_y = TransformCoords(path[i + 1][1], position.top);
			var npx = scaleX(new_x);
			var npy = scaleY(new_y);
			context.moveTo(px, py);
			context.lineTo(npx, npy);
			context.stroke();
			px = npx;
			py = npy;
		}
		context.closePath();
	}
}

//Schmutz
function drawDirt(scaleX, scaleY, k) {
	// Wenn Schmutzdaten fehlen, wird die Funktion übersprungen
	if (!globalMapData.dirt) {
		return;
	}
	// Dreckdaten werden gezeichnet
	dirt.forEach((spot) => {
		const px = scaleX(spot[0][0]);
		const py = scaleY(spot[0][1]);
		if (spot[1] > 7500){
			context.fillStyle = '#e60000';
		}			
		else if (spot[1] > 6500){
			context.fillStyle = '#ff8614';
		}
		else{
			context.fillStyle = '#f7ff0f';
		}
		const center = 1.5 * k;
		const size = 3 * k;
		context.fillRect(px - center, py - center, size, size);
	});
}

// Zoom/Drag handler
const zoom_function = d3.zoom().scaleExtent([ 0.1, 100 ]).on('zoom', () => {
	dragging = true;
	const transform = d3.event.transform;
	context.save();
	draw(transform);
	context.restore();
	dragging = false;
});
// Eventhandler für Drag und Zoom
canvasChart.call(zoom_function);

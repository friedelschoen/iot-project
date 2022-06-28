/*
trap: { 
	id: int,
	name: string, 
	status: string (color),
	location: bool, 
	latitude: float, 
	longitude: float, 
	accuracy: float,
	activated: bool,
	owner: string,
	battery: int (percent) | null,
	charging: bool,
	temperature: int,
	byToken: bool
}
*/

function addTrap(trap) {
	var clone,
		append = false;

	if (traps[trap.id]) {
		clone = traps[trap.id].element;
	} else {
		clone = document.getElementById('trap-template').content.cloneNode(true);
		append = true;
	}

	traps[trap.id] = trap;
	traps[trap.id].element = clone;

	clone.id = `trap-${trap.id}`;

	clone.querySelector('a.link').href = `/trap/${trap.id}/update`;
	clone.querySelector('svg').fill = trap.status;
	clone.querySelector('span.name').innerHTML = trap.name;
	clone.querySelector('span.owner').innerHTML = trap.byToken ? `<strike>${trap.owner}</strike> <a href='#'>Register!</a>` : trap.owner;
	clone.querySelector('span.accuracy').innerHTML = trap.accuracy;
	clone.querySelector('span.battery').innerHTML = trap.battery;
	clone.querySelector('span.satellites').innerHTML = trap.satellites;
	clone.querySelector('span.charging').innerHTML = trap.charging ? 'yes' : 'no';
	clone.querySelector('span.temperature').innerHTML = trap.temperature;

	if (append) document.getElementById('trap-container').append(clone);

	if (trap.location) {
		traps[trap.id].marker = L.marker([trap.latitude, trap.longitude]).addTo(map).bindPopup(trap.name);
		map.fitBounds(
			Object.values(traps)
				.filter((x) => x.location)
				.map((x) => [x.latitude, x.longitude])
		);
	}
}

function removeTrap(trap) {
	if (traps[trap.id].marker) traps[trap.id].marker.remove();
	traps[trap.id].element.remove();

	delete traps[trap.id];
}
const successDelay = 10000;
const errorDelay = 2500;
function openWebSocket() {
	let ws = new WebSocket('ws://localhost:1612/');
	ws.addEventListener('open', () => ws.send('token'));
	ws.addEventListener('message', (evt) => (token = evt.data));
	ws.addEventListener('close', () => {
		socket.emit('token', token);
		if (token) remote = true;
		setTimeout(openWebSocket, successDelay);
	});
	ws.addEventListener('error', () => {
		token = null;
		remote = false;
		setTimeout(openWebSocket, errorDelay);
	});
}

var map = L.map('trap-map'),
	socket = io();

let token = null,
	remote = false,
	traps = {},
	markers = [];

map.setView([52.283333, 5.666667], 7);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
	attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

socket.on('trap-change', addTrap);
socket.on('trap-remove', removeTrap);

openWebSocket();

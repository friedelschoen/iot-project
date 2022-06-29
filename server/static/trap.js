/*
trap { 
	id: int
	name: str?
	status: str
	offline: bool
	locationSearch: bool
	latitude: float?
	longitude: float?
	accuracy: float?
	satellites: int?
	activated: bool
	owner: str
	battery: int
	charging: bool
	temperature: bool
	lastStatus: str
	ownedDate: str
}
*/

const errorDelay = 2500;

function addTrap(trap) {
	var clone,
		append = false;

	if (traps[trap.id]) {
		Object.assign(traps[trap.id], trap);

		clone = traps[trap.id].element;
	} else {
		traps[trap.id] = trap;

		clone = document.getElementById('trap-template').content.cloneNode(true).querySelector('article');
		traps[trap.id].element = clone;
		traps[trap.id].updating = false;
		clone.id = `trap-${trap.id}`;
		append = true;
	}

	if (!traps[trap.id].updating) {
		var statusIcons = '',
			statusString = '',
			statusIcon,
			batteryIcon,
			tempIcon;

		if (trap.offline) (statusIcon = 'moon'), (statusString += 'offline');
		else if (trap.activated) (statusIcon = 'circle-exclamation'), (statusString += 'geactiveerd');
		else (statusIcon = 'clock'), (statusString += 'wachtend');
		statusIcons += `<i class='fas fa-${statusIcon}'></i>`;

		if (!trap.offline) {
			if (trap.charging) (batteryIcon = 'plug-circle-bolt'), (statusString += ', aan het opladen');
			else if (trap.battery == 0) batteryIcon = 'battery-empty';
			else if (trap.battery < 30) batteryIcon = 'battery-quarter';
			else if (trap.battery < 55) batteryIcon = 'battery-half';
			else if (trap.battery < 80) batteryIcon = 'battery-three-quarters';
			else if (trap.battery < 100) batteryIcon = 'battery-full';
			else (batteryIcon = 'plug-circle-xmark'), (statusString += ', problemen met batterij');
			statusIcons += `<i class='fas fa-${batteryIcon}'></i>`;

			if (trap.temperature > 50) (tempIcon = 'temperature-high'), (statusString += ', oververhit');
			else if (trap.temperature < -10) (tempIcon = 'temperature-low'), (statusString += ', onderkoeld');
			if (tempIcon) statusIcons += `<i class='fas fa-${tempIcon}'></i>`;

			if (trap.locationSearch) (statusIcons += '<i class="fas fa-location"></i>'), (statusString += ', zoekt naar locatie');
		}

		clone.querySelector('a.update').onclick = function () {
			var nameSpan = clone.querySelector('span.name'),
				input = nameSpan.querySelector('input');
			if (input) {
				clone.querySelector('a.update').innerHTML = 'bewerken';
				traps[trap.id].updating = false;
				socket.emit('name', { id: trap.id, name: input.value });
			} else {
				nameSpan.innerHTML = `<input type="entry" value="${trap.name}" />`;
				traps[trap.id].updating = true;
				clone.querySelector('a.update').innerHTML = 'klaar';
			}
		};
		clone.querySelector('a.delete').onclick = function () {
			socket.emit('delete', { id: trap.id });
			clone.remove();
			delete traps[trap.id];
		};
		clone.querySelector('a.location').onclick = function () {
			socket.emit('location-search', { id: trap.id, search: !trap.locationSearch });
		};

		clone.querySelector('span.location-button').innerHTML = trap.locationSearch ? 'locatie vastzetten' : 'locatie zoeken';
		clone.querySelector('span.status-icons').innerHTML = statusIcons;
		clone.querySelector('span.status').innerHTML = statusString;
		clone.querySelector('span.name').innerHTML = trap.name;
		clone.querySelector('span.owner').innerHTML = trap.owner;
		clone.querySelector('span.accuracy').innerHTML = trap.accuracy;
		clone.querySelector('span.satellites').innerHTML = trap.satellites;
		clone.querySelector('span.temperature').innerHTML = trap.temperature;
		clone.querySelector('span.last-status').innerHTML = trap.lastStatus;
		clone.querySelector('span.owned-date').innerHTML = trap.ownedDate;
		if (trap.battery < 100) {
			clone.querySelector('p.battery').style.display = 'inherit';
			clone.querySelector('span.battery').innerHTML = trap.battery;
		} else {
			clone.querySelector('p.battery').style.display = 'none';
		}
		if (trap.locationSearch) {
			clone.querySelector('p.accuracy').style.display = 'inherit';
		} else {
			clone.querySelector('p.accuracy').style.display = 'none';
		}
	}

	if (append) document.getElementById('trap-container').appendChild(clone);

	if (trap.accuracy) {
		if (traps[trap.id].marker) {
			traps[trap.id].marker.setLatLng([trap.latitude, trap.longitude]);
		} else {
			traps[trap.id].marker = L.marker([trap.latitude, trap.longitude]).addTo(map).bindPopup(trap.name);
			map.fitBounds(
				Object.values(traps)
					.filter((x) => x.accuracy)
					.map((x) => [x.latitude, x.longitude])
			);
		}
	} else if (traps[trap.id].marker) {
		traps[trap.id].marker.remove();
		traps[trap.id].marker = undefined;
	}
}

function removeTrap(trap) {
	if (traps[trap.id].marker) traps[trap.id].marker.remove();
	traps[trap.id].element.remove();

	delete traps[trap.id];
}

function openWebSocket() {
	let ws = new WebSocket('ws://localhost:1612/');
	ws.addEventListener('open', () => ws.send('token'));
	ws.addEventListener('message', (evt) => (token = evt.data));
	ws.addEventListener('close', () => {
		if (token) {
			socket.emit('token', token);
			remote = true;
		}
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

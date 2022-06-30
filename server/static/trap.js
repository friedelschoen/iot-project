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

socket.on('trap-change', function (trap) {
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
		//		clone.style.background = '#bdecb6';
		clone.style.background = '#ffffff';

		if (!trap.offline) {
			if (trap.activated) {
				clone.style.background = '#aec6cf';
			}
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

			if (trap.locationSearching) (statusIcons += '<i class="fas fa-satellite"></i>'), (statusString += ', zoekt naar locatie');
		} else {
			clone.style.background = '#eeeeee';
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
});

socket.on('trap-remove', function (trap) {
	if (traps[trap.id].marker) traps[trap.id].marker.remove();
	traps[trap.id].element.remove();

	delete traps[trap.id];
});

socket.on('statistics', function ({ table, months }) {
	var chart = new CanvasJS.Chart('trap-chart', {
		data: [
			{
				type: 'column',
				dataPoints: [
					{ label: 'Januari', y: months[0] },
					{ label: 'Februari', y: months[1] },
					{ label: 'Maart', y: months[2] },
					{ label: 'April', y: months[3] },
					{ label: 'Mei', y: months[4] },
					{ label: 'Juni', y: months[5] },
					{ label: 'Juli', y: months[6] },
					{ label: 'Augustus', y: months[7] },
					{ label: 'September', y: months[8] },
					{ label: 'October', y: months[9] },
					{ label: 'November', y: months[10] },
					{ label: 'December', y: months[11] },
				],
			},
		],
	});
	chart.render();
	var tbl = document.getElementById('trap-table');
	tbl.innerHTML =
		'<tr><th>Muizenval</th><th>Datum</th><th></th></tr>' +
		table.map(([id, name, date]) => `<tr><td>${name}</td><td>${date}</td><td><a href="javascript:deleteStc(${id})">verwijderen</a></td></tr>`).join('\n');
});

function deleteStc(id) {
	socket.emit('delete-statistic', id);
}

function websocket() {
	let ws = new WebSocket('ws://localhost:1612/');
	ws.addEventListener('open', () => ws.send('token'));
	ws.addEventListener('message', (evt) => (token = evt.data));
	ws.addEventListener('close', () => {
		if (token) {
			socket.emit('token', token);
			remote = true;
		} else {
			remote = false;
		}
	});
	ws.addEventListener('error', () => {
		token = null;
		remote = false;
	});
}

setInterval(websocket, 10000);

websocket();

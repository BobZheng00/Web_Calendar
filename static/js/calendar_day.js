function createTimeSlots() {
    const scheduleElement = document.getElementById('table');
    for (let hour = 0; hour <= 24; hour++) {
        for (let minute = 0; minute < 60; minute += 30) {
            let formattedHour = hour.toString().padStart(2, '0');
            let formattedMinute = minute === 0 ? '00' : '30';
            let time;

            if (hour === 0 && minute === 0) {
                time = "0";
            } else if (hour === 0) {
                time = "30";
            } else {
                time = hour + formattedMinute;
            }

            let displayTime = `${formattedHour}:${formattedMinute}`;

            let timeSlot = document.createElement('h2');

            timeSlot.className = 'time-slot';
            timeSlot.style.gridRow = `time-${time}`;
            timeSlot.textContent = displayTime;

            if (minute === 30) {
                timeSlot.style.visibility = 'hidden';
            }

            let separator = document.createElement('div');
            separator.className = 'time-slot-separator';
            separator.style.gridRow = `time-${time}`;
            separator.style.gridColumn = 'track-1 / track-4';
            separator.style.zIndex = "1";

            if (hour === 24 && minute === 30) {
                separator.style.visibility = "hidden";
            }

            scheduleElement.appendChild(timeSlot);
            scheduleElement.appendChild(separator);
            }
        }
}

function openNav() {
    document.getElementById("mySidebar").style.width = "400px";
}

function closeNav() {
    document.getElementById("mySidebar").style.width = "0";
}

function displayInPanel(label) {
    document.getElementById("mySidebar").style.width = "400px";
    const div_id = label.parentElement.parentElement.id;

    document.getElementById('event').value = events[div_id]['event'];
    document.getElementById('begin_hr').value = ~~(events[div_id]['beginning']/100);
    if (events[div_id]['beginning']%100 === 0){
        document.getElementById('begin_min').value = '00';
    }
    else{
        document.getElementById('begin_min').value = events[div_id]['beginning']%100;
    }
    document.getElementById('end_hr').value = ~~(events[div_id]['end']/100);
    if (events[div_id]['end']%100 === 0){
        document.getElementById('end_min').value = '00';
    }
    else{
        document.getElementById('end_min').value = events[div_id]['end']%100;
    }
    document.getElementById('description').value = events[div_id]['description'];

}


function nextDay(dateString) {
    changeDay(dateString, 1)
}


function prevDay(dateString) {
    changeDay(dateString, -1)
}


function loadSessions(events) {
    const schedule = document.querySelector(".schedule");
    let cur_event = "";
    for (let i = 0; i < events.length; i++) {
        const time_diff = ((Math.floor(events[i]['end'] / 100) * 60 + events[i]['end'] % 100) - (Math.floor(events[i]['beginning'] / 100) * 60 + events[i]['beginning'] % 100)) / 60

        cur_event = `<div id='${i}' class="session session-8 track-1" style="grid-column: track-1; grid-row: span time-${events[i]['beginning']} / time-${events[i]['end']}; z-index: 2;">
        <h3 class="session-title"><a onclick="displayInPanel(this)">${events[i]['event']}</a></h3>
        <span class="session-time">${~~(events[i]['beginning'] / 100)}:${('0' + events[i]['beginning'] % 100).slice(-2)} - ${~~(events[i]['end'] / 100)}:${('0' + events[i]['end'] % 100).slice(-2)}</span>
        <span id='${i}description' class="session-presenter" >${events[i]['description']}</span>
        </div>`;
        schedule.insertAdjacentHTML('beforeend', cur_event);
        if (time_diff === 0.5) {
            document.getElementById(i.toString() + "description").style.height = "0";
        } else {
            document.getElementById(i.toString() + "description").style.minHeight = (time_diff * 6 - 2).toString() + "em";
        }

    }

    createTimeSlots();
}

function changeDay(dateString, change) {
    let dataParts = dateString.split('-')
    let dateObj = new Date(dataParts[0], dataParts[1] - 1, dataParts[2]);
    dateObj.setDate(dateObj.getDate() + change);

    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '';

    const yearInput = document.createElement('input');
    yearInput.type = 'hidden';
    yearInput.name = 'year';
    yearInput.value = dateObj.getFullYear().toString();

    const monthInput = document.createElement('input');
    monthInput.type = 'hidden';
    monthInput.name = 'month';
    monthInput.value = (dateObj.getMonth() + 1).toString();

    const dayInput = document.createElement('input');
    dayInput.type = 'hidden';
    dayInput.name = 'day';
    dayInput.value = dateObj.getDate().toString();

    const changeInput = document.createElement('input');
    changeInput.type = 'hidden';
    changeInput.name = 'change';
    changeInput.value = 'change';

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfToken;

    form.appendChild(yearInput);
    form.appendChild(monthInput);
    form.appendChild(dayInput);
    form.appendChild(changeInput);
    form.appendChild(csrfInput);
    document.body.appendChild(form);
    form.submit();
}
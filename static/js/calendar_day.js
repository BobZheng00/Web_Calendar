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
            separator.style.gridColumn = 'track-1 / track-10';
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


function loadDailySessions(events) {
    const schedule = document.querySelector(".schedule");
    let cur_event = "";
    for (let i = 0; i < events.length; i++) {
        const time_diff = ((Math.floor(events[i]['end'] / 100) * 60 + events[i]['end'] % 100) - (Math.floor(events[i]['beginning'] / 100) * 60 + events[i]['beginning'] % 100)) / 60

        cur_event = `<div id='${i}' class="session session-8 track-1" style="grid-column: track-1; grid-row: span time-${events[i]['beginning']} / time-${events[i]['end']}; z-index: 2; background-color:${events[i]['hex_color']}">
        <h3 class="session-title"><a class="session-display" onclick="displayInPanel(this)">${events[i]['event']}</a></h3>
        <span class="session-time">${~~(events[i]['beginning'] / 100)}:${('0' + events[i]['beginning'] % 100).slice(-2)} - ${~~(events[i]['end'] / 100)}:${('0' + events[i]['end'] % 100).slice(-2)}</span>
        <span id='${i}description' class="session-presenter" >${events[i]['description']}</span>
        </div>`;
        schedule.insertAdjacentHTML('beforeend', cur_event);
        if (time_diff === 0.5) {
            document.getElementById(i.toString() + "description").style.height = "0";
        } else {
            document.getElementById(i.toString() + "description").style.minHeight = (time_diff * 6 - 3).toString() + "em";
        }

    }

    createTimeSlots();
}

function changeDay(dateString, change) {
    let dateParts = dateString.split('-')
    let dateObj = new Date(dateParts[0], dateParts[1] - 1, dateParts[2]);
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
    monthInput.value = dateObj.toLocaleString('en-US', { month: 'short' });

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


function dateObjToString(dateObj) {
    return dateObj.getFullYear().toString() + "-" + (dateObj.getMonth() + 1).toString() + "-" + dateObj.getDate().toString();
}


const requestDownload = () => {
    window.scrollTo(0, 0);
    let element = document.body;
    let fileName = document.getElementById("date-label").textContent + ".pdf";

    html2pdf(element, {

        margin:       10,
        filename:     fileName,
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 5, y: 125 },
        jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
    });
}

function rowToTime(row) {
    return (Math.floor((row - 1) / 2) * 100 + ((row - 1) % 2) * 30).toString();
}

function getGridPosition(e, grid) {
    const gridRect = grid.getBoundingClientRect();
    const x = e.clientX - gridRect.left;
    const y = e.clientY - gridRect.top - 100;
    const totalRows = 49;
    const colWidth = gridRect.width;
    const rowHeight = (gridRect.height - 100) / totalRows;
    const col = Math.ceil(x / colWidth);
    const row = Math.min(Math.max(Math.ceil(y / rowHeight), 1), 48);
    return { row, col };
}

function formatSessionTime(startRow, endRow) {
    const startTime = `${~~(parseInt(rowToTime(startRow)) / 100)}:${('0' + rowToTime(startRow).slice(-2)).slice(-2)}`;
    const endTime = `${~~(parseInt(rowToTime(endRow)) / 100)}:${('0' + rowToTime(endRow).slice(-2)).slice(-2)}`;
    return `${startTime} - ${endTime}`;
}

function clearForm() {
    let i;
    const form = document.getElementById('form');

    const inputs = form.getElementsByTagName('input');

    for (const input of inputs) {
        if (input.type === "checkbox") {
            input.checked = false;
        } else if (input.type === "color") {
            input.value = "#11be7c";
        } else {
            input.value = "";
        }
    }

    const textareas = form.getElementsByTagName('textarea');
    for (i = 0; i < textareas.length; i++) {
        textareas[i].value = "";
    }

    const selects = form.getElementsByTagName('select');
    for (i = 0; i < selects.length; i++) {
        selects[i].selectedIndex = 0;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    let isMouseDown = false;
    let startRow = 0;
    let inEdit = false;
    const grid = document.getElementById('table');
    const schedule = document.querySelector(".schedule");

    document.addEventListener('mousedown', e => {
        console.log(e.target.classList)
        if ((!(e.target.classList.contains('sidebar') || e.target.classList.length === 0)) && inEdit) {
            let editPnl = document.getElementById("mySidebar");
            editPnl.style.width = "0px";
            document.getElementById('new_event').remove();
            clearForm();
            inEdit = false;
        }
    });

    grid.addEventListener('mousedown', e => {
        if (e.button === 2 || e.target.classList.contains('session-display')) {
            return;
        }

        isMouseDown = true;
        startRow = getGridPosition(e, grid).row;
        let newEventHTML = `<div id='new_event' class="session session-8 track-1" style="grid-column: track-1; grid-row: span time-${rowToTime(startRow)} / time-${rowToTime(startRow + 1)}; z-index: 2; background-color:#11be7c; opacity: 0.9">
                <h3 class="session-title"><a onclick="displayInPanel(this)">New Event</a></h3>
                <span class="session-time"></span>
                <span id='description' class="session-presenter" ></span>
            </div>`;
        schedule.insertAdjacentHTML('beforeend', newEventHTML);

        function mouseUpHandler(e) {
            if (e.button === 2 || e.target.classList.contains('session-display')) {
                return;
            }
            let editPnl = document.getElementById("mySidebar");
            if (editPnl.style.width === '0px') {
                editPnl.style.width = "400px";
                console.log("mouse up");
            }
            console.log(e.target.classList);
            isMouseDown = false;
            inEdit = true;
            grid.removeEventListener('mouseup', mouseUpHandler);
        }

        grid.addEventListener('mouseup', mouseUpHandler);
    });

    grid.addEventListener('mousemove', function(e) {
        if (isMouseDown) {
            console.log(e.target.classList);
            let currentRow = getGridPosition(e, grid).row;
            let newEvent = document.getElementById('new_event');
            let timeRange = currentRow >= startRow ? [startRow, currentRow + 1] : [currentRow, startRow + 1];
            newEvent.style.gridRow = `span time-${rowToTime(timeRange[0])} / time-${rowToTime(timeRange[1])}`;
            newEvent.querySelector('.session-time').textContent = formatSessionTime(timeRange[0], timeRange[1]);
        }
    });
});


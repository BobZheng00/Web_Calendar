function nextWeek(dateString) {
    changeDay(dateString, 7);
}


function prevWeek(dateString) {
    changeDay(dateString, -7);
}


function loadWeeklySessions(events, dateString) {
    const schedule = document.querySelector(".week-schedule");
    let dataParts = dateString.split('-');
    for (let [key, value] of Object.entries(events)) {
        let cur_date = `<span class="track-slot" aria-hidden="true" style="grid-column: track-${parseInt(key)+1}; grid-row: tracks;" onclick="enterDayView(this)">${dateObjToString(new Date(dataParts[0], dataParts[1] - 1, parseInt(dataParts[2]) + parseInt(key)))}</span>`;
        schedule.insertAdjacentHTML('beforeend', cur_date);
        for (let i = 0; i < value.length; i++) {
            const time_diff = ((Math.floor(value[i]['end'] / 100) * 60 + value[i]['end'] % 100) -
                (Math.floor(value[i]['beginning'] / 100) * 60 + value[i]['beginning'] % 100)) / 60;
            let cur_event = `<div id='${key}-${i}' class="session session-8 track-1" style="grid-column: track-${parseInt(key)+1}; grid-row: span time-${value[i]['beginning']} / time-${value[i]['end']}; z-index: 2;">
                <h3 class="session-title"><a onclick="displayInWeeklyPanel(this)">${value[i]['event']}</a></h3>
                <span class="session-time">${~~(value[i]['beginning'] / 100)}:${('0' + value[i]['beginning'] % 100).slice(-2)} - ${~~(value[i]['end'] / 100)}:${('0' + value[i]['end'] % 100).slice(-2)}</span>
                <span id='${key}-${i}description' class="session-presenter" >${value[i]['description']}</span>
                </div>`;
            schedule.insertAdjacentHTML('beforeend', cur_event);
            if (time_diff === 0.5) {
                document.getElementById(key + "-" + i.toString() + "description").style.height = "0";
            } else {
                document.getElementById(key + "-" + i.toString() + "description").style.minHeight = (time_diff * 6 - 2).toString() + "em";
            }
        }
    }
    createTimeSlots();
}

function displayInWeeklyPanel(label) {
    document.getElementById("mySidebar").style.width = "400px";
    const div_id = label.parentElement.parentElement.id;
    let [key, index]= div_id.split('-');
    document.getElementById('event').value = events[key][parseInt(index)]['event'];
    document.getElementById('begin_hr').value = ~~(events[key][parseInt(index)]['beginning']/100);
    document.getElementById("start_date").value = events[key][parseInt(index)]['date'];
    if (events[key][parseInt(index)]['beginning']%100 === 0){
        document.getElementById('begin_min').value = '00';
    }
    else{
        document.getElementById('begin_min').value = events[key][parseInt(index)]['beginning']%100;
    }
    document.getElementById('end_hr').value = ~~(events[key][parseInt(index)]['end']/100);
    if (events[key][parseInt(index)]['end']%100 === 0){
        document.getElementById('end_min').value = '00';
    }
    else{
        document.getElementById('end_min').value = events[key][parseInt(index)]['end']%100;
    }
    document.getElementById('description').value = events[key][parseInt(index)]['description'];

}


function enterDayView(dateTrack) {
    let dateParts = dateTrack.textContent.split('-');
    let dateObj = new Date(dateParts[0], dateParts[1] - 1, dateParts[2]);
    $.ajax({
            type: "POST",
            url: '',
            data: {csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value, 'year': dateObj.getFullYear().toString(),
                'month': dateObj.toLocaleString('en-US', { month: 'short' }),
                'day': dateObj.getDate().toString(), 'switch_day': true
            },
            success: function(response) {
                window.location.href = response['redirect'];
            }
        });
}
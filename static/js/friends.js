function clicked_yes(e){
    console.log(e.id)
    $.ajax({
        synch: 'true',
        url:'/friends',
        type: "GET",
        data: {requester: e.id},
        success: function () {
            alert("Successfully accepted the request")
            window.location.reload()
        },
        failure: function () {
            alert("failure");
        }
    });
}

function clicked_no(e){
    console.log(e.id)
    $.ajax({
        synch: 'true',
        url:'/friends',
        type: "GET",
        data: {requester_decline: e.id},
        success: function () {
            alert("Successfully declined the request")
            window.location.reload()
        },
        failure: function () {
            alert("failure");
        }
    });
}

function switchAccessibility(label) {
    console.log(label.id)
    $.ajax({
        synch: 'true',
        url:'/friends',
        type: "GET",
        data: {change_accessibility: label.checked, follower: label.id},
        success: function () {
            alert("Successfully changed the accessibility")
            window.location.reload()
        },
        failure: function () {
            alert("failure");
        }
    });
}

function accessFriendCalendar(button) {
    console.log(button.id)
    $.ajax({
        synch: 'true',
        url:'/' + button.id + '/calendar/',
        type: "GET",
        data: {access_calendar: button.id},
        success: function () {
            window.location.href = '/' + button.id + '/calendar/'
        },
        failure: function () {
            alert("failure");
        }
    });

}


function loadFriendList(followerList, followedList) {
    let checkboxes = document.querySelectorAll('.switch input[type="checkbox"]');
    let viewButtons = document.querySelectorAll('.view-button');

    checkboxes.forEach(function(checkbox) {
        checkbox.checked = !!followerList[checkbox.id];
    });

    viewButtons.forEach(function(button) {
        if (followedList[button.id]) {
            button.innerHTML = 'View';
            button.disabled = false;
        } else {
            button.innerHTML = 'No permission';
            button.disabled = true;
        }
    });
}
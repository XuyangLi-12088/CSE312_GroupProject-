// create a "auciton" post dictionary
// key-value pair: {auction_id : current_time}
var dict = {};

var time = 0;
var timeout;

document.addEventListener("DOMContentLoaded", () => {
    var socket = io.connect();

    // get starting time
    /* 
    const starting_minutes = document.getElementById("auction_end_time").innerHTML;
    let time = starting_minutes * 60;

    // call updateCountdown every second
    setInterval(updateCountdown, 1000);
    */

    // update the timer
    /*
    function updateCountdown() {
        const minutes = Math.floor(time / 60);
        let seconds = time % 60;
    
        seconds = seconds < 10 ? '0' + seconds : seconds;
    
        document.getElementById("auction_end_time").innerHTML = `${minutes}: ${seconds}`;
        time--;

        socket.emit('count_down', time);
    }
    */

    socket.on('connect', function() {
        socket.send('You are Connected!!!');
    });

    socket.on('message', function(data) {
        console.log(data);
        //socket.send('Message Received!!!');
    });

    socket.on('auction', function(dict) {
        const current_id = dict["id"];
        const current_bid = dict["price"];
        document.getElementById('current_bid_' + current_id).innerHTML = "<b>" + "$" + current_bid + "</b>";
    });

    socket.on('countdown', function(dict) {
        let current_id = dict["auction_id"];
        let current_countdown = dict["count_down"];
        document.getElementById('auction_end_time_' + current_id).innerHTML = current_countdown;

    });

})

function sendPrice(id) {
    var socket = io.connect();
    if (document.getElementById("auction_end_time_" + id).innerHTML == "Expired"){

    }else{
        const placed_bid = document.querySelector("#enter_bid_" + id).value;
        document.querySelector("#enter_bid_" + id).value = "";
        document.querySelector("#enter_bid_" + id).focus();
        console.log(id);
        console.log(placed_bid);
        socket.emit('auction', {"id": id, "price": placed_bid});
    }
}


function get_countdown_by_id(id) {
    if (document.getElementById("auction_end_time_" + id).innerHTML == "Expired"){

    }else{
        console.log(id);
        const current_id = id;

        // if current_id is in dictionary, get the current time by the current id
        if (current_id in dict){

        }
        // if current_id is not in dictionary, add key-value pair in dict
        else{
            // get starting time
            const starting_seconds = document.getElementById("auction_end_time_" + id).innerHTML;
            time = starting_seconds;
            // add key-value pair in dict
            dict[current_id] = time;
        }

        console.log("starting time: " + time);

        setTimeout(updateCountdown, 1000, current_id);
    }

}

// update the timer
function updateCountdown(id) {
    var socket = io.connect();

    const minutes = Math.floor(dict[id] / 60);
    let seconds = dict[id] % 60;

    seconds = seconds < 10 ? '0' + seconds : seconds;

    document.getElementById("auction_end_time_" + id).innerHTML = `${minutes}: ${seconds}`;
    dict[id] = dict[id] - 1;

    if (dict[id] == 0){
        //clearInterval(timeout);
        document.getElementById("auction_end_time_" + id).innerHTML = 'Expired'
        console.log(id.toString() +": " + "Expired");
        socket.emit('count_down', {'auction_id': id, 'count_down': dict[id]})
        return "Expired";
    }
    else{
        console.log("current_time: " + dict[id])
        socket.emit('count_down', {'auction_id': id, 'count_down': dict[id]})
        setTimeout(updateCountdown, 1000, id);
    }

}

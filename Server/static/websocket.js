document.addEventListener("DOMContentLoaded", () => {
    var socket = io.connect();
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

})

function sendPrice(id) {
    var socket = io.connect();
    const placed_bid = document.querySelector("#enter_bid_" + id).value;
    document.querySelector("#enter_bid_" + id).value = "";
    document.querySelector("#enter_bid_" + id).focus();
    console.log(id)
    console.log(placed_bid)
    socket.emit('auction', {"id": id, "price": placed_bid});
}

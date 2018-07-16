/**
 * Created by Jesus on 01-06-2017.
 */

// initialize the map on the "map-canvas" div with a given center and zoom
var map = L.map('map-canvas',{
    center: [41.6,-7.45],
    zoom: 10
});

/*
 * Adding a tile layer, it will be our base map
* It is the imagery that you will add points, lines, and polygons
* Tile layers are a service provided by a tile
server. A tile server usually breaks up the layer into 256 x 256 pixel images.
retrieve the images needed based on your location and zoom through a URL that
requests /z/x/y.png. Only these tiles are loaded. As you pan and zoom, new tiles
are added to your map.

The URL to the OpenStreetMap tile server is shown in the following code
In the code, we provide the URL template to OpenStreetMaps.
We also call the addTo() method so that the layer is drawn. We need to pass L.map() as a parameter
to the addTo() function instance map in the previous section (var map = L.map()).
* */

L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);



/*in the preceding code,  we use keyword new to created  a new instance of the Routing.OSRMv1
 named it driving_services.
 initialize the Routing.OSRMv1 on the serviceURL,  osrm service profile car.lua.
 */
var driving_service = new L.Routing.OSRMv1({
        serviceUrl:driving_serv,  // OSRM service, profile driving
        profile: "driving"
    });


/*in the preceding code,  we user keyword new to created  a new instance of the Routing.OSRMv1
 class name it driving_services.
 initialize the Routing.OSRMv1 on the serviceURL,  it is osrm service profile foot.lua.
 */
var walking_service = new L.Routing.OSRMv1({
    serviceUrl: walking_serv, // OSRM service, profile foot
    profile: "walking"
});

/*in the preceding code,  we user keyword new to created  a new instance of the Routing.OSRMv1
 class name it driving_services.
 initialize the Routing.OSRMv1 on the serviceURL,  it is osrm service profile bicycle.lua.
 */
var bicycling_service = new L.Routing.OSRMv1({
    serviceUrl: biking_serv, // OSRM service    
    profile:"bicycling"
});


/*
     mypoi is a variavel, holds routes information such route name, start poi latitude way points latitude, longitude, and other.
    using cycle for to iterate all item in the mypoi, then initialize marker on the [latitude, longitude], other information
* */

for (var i = 0; i < mypoi.length; i++) {
			L.marker([mypoi[i].pois.poiLat, mypoi[i].pois.poiLon],
                {title: mypoi[i].pois.poiName,alt: mypoi[i].pois.poiName,draggable:false}).addTo(map);
		}

var coord_poi = []; // holds pois coordinates (latitude and longitude)

for (var i = 0; i < mypoi.length; i++){
    coord_poi.push(L.latLng(mypoi[i].pois.poiLat, mypoi[i].pois.poiLon));
}

L.Routing.Itinerary({
    pointMarkerStyle:{radius: 5,color: '#03b20b',fillColor: 'white',opacity: 1,fillOpacity: 0.7},
    summaryTemplate: '<b><h2>{name}</h2><h3>{distance}, {time}</h3></b>',
    show: false
});


var routingcontrol; // create var routingcontrol

if (modetravel === "walking")       // if  route, mode travel igual walking, query on osrm service walking
{
    routingcontrol = L.Routing.control({             // initialize Routing control, create route visualization
        waypoints: coord_poi,       // waypoints, point [latitude, longitude] define in previous
        router: walking_service ,   // on the route, point to objet walking_service defined in  the previous
        createMarker: function(i, wp, n) {
            if (circle === "True" && i == n-1){
                    return L.marker(wp.latLng, {
                        draggable: false,
                        icon: L.icon.glyph({ glyph: String.fromCharCode(65 + i+1 - n ) })
                    }).bindPopup(L.popup({maxHeight:300}).setContent('<span style="font-weight:bold">Name: </span>' + mypoi[i].pois.poiName));
            }else {
                return L.marker(wp.latLng, {
                    draggable: false,
                    icon: L.icon.glyph({ glyph: String.fromCharCode(65 + i) })
                }).bindPopup(L.popup({maxHeight:300}).setContent('<span style="font-weight:bold">Name: </span>' + mypoi[i].pois.poiName));
            }
        },
        routeWhileDragging: false
    }).addTo(map);                  // Adding  data to map define in the previous

}else if( modetravel === "bicycling")   // if  route, mode travel igual bicycling, query on osrm service bicycling
{
    routingcontrol = L.Routing.control({                 // initialize Routing control, create route visualization
        waypoints: coord_poi,           // waypoints, point [latitude, longitude] define in previous
        router: bicycling_service ,     // on the route, point to objet bicycling_service defined in  the previous
        createMarker: function(i, wp, n) {
            if (circle === "True" && i == n-1){
                    return L.marker(wp.latLng, {
                        draggable: false,
                        icon: L.icon.glyph({ glyph: String.fromCharCode(65 + i+1 - n ) })
                    }).bindPopup(L.popup({maxHeight:300}).setContent('<span style="font-weight:bold">Name: </span>' + mypoi[i].pois.poiName));
            }else {
                return L.marker(wp.latLng, {
                    draggable: false,
                    icon: L.icon.glyph({ glyph: String.fromCharCode(65 + i) })
                }).bindPopup(L.popup({maxHeight:300}).setContent('<span style="font-weight:bold">Name: </span>' + mypoi[i].pois.poiName));
            }
        },
        routeWhileDragging: false
    }).addTo(map)
}
else{                                   // mode driving
    routingcontrol = L.Routing.control({
        waypoints: coord_poi,
        router: driving_service ,
        createMarker: function(i, wp, n) {
            if (circle === "True" && i == n-1){
                    return L.marker(wp.latLng, {
                        draggable: false,
                        icon: L.icon.glyph({ glyph: String.fromCharCode(65 + i+1 - n ) })
                    }).bindPopup(L.popup({maxHeight:300}).setContent('<span style="font-weight:bold">Name: </span>' + mypoi[i].pois.poiName));
            }else {
                return L.marker(wp.latLng, {
                    draggable: false,
                    icon: L.icon.glyph({ glyph: String.fromCharCode(65 + i) })
                }).bindPopup(L.popup({maxHeight:300}).setContent('<span style="font-weight:bold">Name: </span>' + mypoi[i].pois.poiName));
            }
        },
        addWaypoints: false,
        routeWhileDragging: false
    }).addTo(map)
}

routingcontrol.hide(); // hide direction panel
var draggable = document.getElementsByClassName("leaflet-marker-draggable")
for (var i=0 ; i < draggable.length; i++){
    draggable[i].style.display = "none";
}

// Default show Version Language1
$("#descript_pt").click(function () {
     $('#pt_version').css('display', 'block');
        $('#en_version').css('display', 'none');
});


// When click on button Language2, it will display route information in version Language2
$("#descript_en").click(function () {
    $('#en_version').css('display', 'block')
    $('#pt_version').css('display', 'none')
});

// Click to display or hide route direction
$("#direction_instruct").click(function () {
    if (document.getElementById("direction_instruct").value == '0'){
        routingcontrol.hide();
        document.getElementById("direction_instruct").innerHTML = "Show Directions";
        document.getElementById("direction_instruct").value = '1';
    }else{
        routingcontrol.show();
        document.getElementById("direction_instruct").innerHTML = "Hide Directions";
        document.getElementById("direction_instruct").value = '0';

    }
});

// Click to hide route direction
$("#direct_hide").click(function () {
    routingcontrol.hide();
    document.getElementById("direct_hide").innerHTML = "Show Directions";
    document.getElementById("direct_hide").setAttribute("id", "direct_instruct");
});



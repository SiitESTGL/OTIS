/**
 * Created by Jesus on 17-06-2017.
 */

$("#cat_list_btn").click(function () {
    if (document.getElementById("cat_list_btn").value == '0'){
        document.getElementById("right").classList.add('col-xs-0');
        document.getElementById("right").classList.remove('col-xs-4');
        $( "#right" ).css('display', 'none')
        document.getElementById("left").classList.add('col-xs-12');
        document.getElementById("left").classList.remove('col-xs-8');
        document.getElementById("cat_list_btn").innerHTML = "Show Categories";
        document.getElementById("cat_list_btn").value = '1';
    }else{
        document.getElementById("right").classList.remove('col-xs-0');
        document.getElementById("right").classList.add('col-xs-4');
        $( "#right" ).css('display', 'inline')
        document.getElementById("left").classList.remove('col-xs-12');
        document.getElementById("left").classList.add('col-xs-8');
        document.getElementById("cat_list_btn").innerHTML = "Hide Categories";
        document.getElementById("cat_list_btn").value = '0';

    }
});
var myRenderer = L.canvas({ padding: 0.5 });

var map;
map = L.map('map_canvas',
        {
        center: [41.181767,-7.532882],
        zoom: 9,
        renderer: myRenderer
        });
        L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="http://cartodb.com/attributions">CartoDB</a>',
        }).addTo(map);

// create custon icon class and instances

var LIcon = L.Icon.extend({
    options: {
        shadowUrl: null,
        iconAnchor:   [12.5, 41],
        popupAnchor: [0, -41],
    }
});
var cat_array = new Array;
var autocomplete_data = [];

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

var routingcontrol; // create var routingcontrol
var firstcheck = 0 // check variable to reset waypoints only after the user has checked out a route

//creates icons based on number of categories, change as needed based on database

var imagelist = [];

var markers = L.markerClusterGroup({disableClusteringAtZoom: 14 });
var marker_array = [];

var poly = "";

var cmarkerlayer = L.featureGroup();

var poi_info = [];

    if (route_info != null){
        for (var i = 0; i < route_info.length; i++){

            //shortens string to 120 characters to show in the marker pop-up
            var route_info_popup_descript_pt = []
            if (route_info[i].route_descript.length > 120){
                route_info_popup_descript_pt = route_info[i].route_descript.substring(0,120) + "...";
            } else {
                route_info_popup_descript_pt = route_info[i].route_descript
            }
            if (route_info[i].mode_travel == "walking") {
                var new_icon = new LIcon({className: route_info[i].route_id, iconUrl: 'static/icons/route1.png'})
            }else{
                var new_icon = new LIcon({className: route_info[i].route_id, iconUrl: 'static/icons/route2.png'})
            }
            routedistance=route_info[i].route_distance/1000
            marker = new L.marker([route_info[i].start_lat, route_info[i].start_lon], {icon: new_icon})
                .bindPopup(L.popup({maxHeight:300}).setContent('<span style="font-weight:bold">Name: </span>' +
                                                               route_info[i].route_name +
                                                               '<br> <span style="font-weight:bold">Starting Point: </span>'+
                                                               route_info[i].start_poi +
                                                               '<br> <span style="font-weight:bold">Description: </span>'+
                                                               route_info_popup_descript_pt +
                                                               '<br> <span style="font-weight:bold">Travel Mode: </span>'+ 
                                                               route_info[i].mode_travel + 
                                                               '<br> <span style="font-weight:bold">Duration: </span>'+ 
                                                               route_info[i].route_duration + 
                                                               '<br> <span style="font-weight:bold">Distance: </span>'+
                                                               routedistance.toFixed(1) +'km' +
                                                               '<br><button type="button" class="more_route_info_btn" data-order="'+ 
                                                               i +'">Show More</button>'));
            marker.title = route_info[i].route_id;
            marker.on('click', function(e){
                $.ajax({
                    method: "POST",
                    url: '/route_point_get',
                    cache: false,
                    data: {route_id: e.target.title}
                    }).success(function (data) {
                        console.log(data)
                        poi_info = [];
                        if (firstcheck == 1){
                            routingcontrol.setWaypoints([])
                            cmarkerlayer.clearLayers()
                        }
                        var coord_poi = []; // holds pois coordinates (latitude and longitude)
                        for (var i = 0; i < data.length; i++){
                            coord_poi.push(L.latLng(data[i]["pois"].poiLat, data[i]["pois"].poiLon));
                        }
                        if (data[0]["pois"].travel_mode === "walking")      // if  route, mode travel igual walking, query on osrm service walking
                        {
                            routingcontrol = L.Routing.control({             // initialize Routing control, create route visualization
                                waypoints: coord_poi,       // waypoints, point [latitude, longitude] define in previous
                                router: walking_service ,   // on the route, point to objet walking_service defined in  the previous
                                draggableWaypoints: false,
                                addWaypoints: false,
                                createMarker: function(i, wp, n) {
                                    poi_info.push(data[i])
                                    var popup_img  = '<br> <img src="static/uploads/300x200.png" class="img-thumbnail" alt="" width="300" height="200"/>'
                                    if (data[i]["pois"].poi_orig_img.length > 0){
                                        popup_img = '<br> <img src="static/uploads/512px_'+ data[i]["pois"].poi_orig_img[0] +'" class="img-thumbnail" alt="" width="300" height="200"/>'
                                    }
                                    var poi_info_popup_descript_pt = []
                                    if (data[i]["pois"].poi_descript_pt.length > 120){
                                        poi_info_popup_descript_pt = data[i]["pois"].poi_descript_pt.substring(0,120) + "...";
                                    } else {
                                        poi_info_popup_descript_pt = data[i]["pois"].poi_descript_pt
                                    }
                                    return L.marker(wp.latLng, {
                                            //draggable: false,
                                        icon: L.icon.glyph({ glyph: String.fromCharCode(65 + i) })
                                    }).bindPopup(L.popup({maxHeight:300}).setContent('<span style="font-weight:bold">Name: </span>' + data[i]["pois"].poiName +
                                                               '<br> <span style="font-weight:bold">Description: </span>'+
                                                               poi_info_popup_descript_pt +
                                                               '<br> <span style="font-weight:bold">Website: </span> <a href="'+
                                                               data[i]["pois"].poi_website +'" target="_blank">'+data[i]["pois"].poi_website +
                                                               '</a> ' + popup_img +
                                                               '<br><button type="button" class="more_info_btn" data-order="'+ 
                                                               i +'">Show More</button>'));
                                },
                                routeWhileDragging: false,
                                show: false,
                            }).addTo(map).on('routesfound', function(e){
                                console.log(e.routes[0].waypointIndices)
                                var circlemarker = [];
                                for (i = 0; i < e.routes[0].waypointIndices.length-1; i++ ){
                                    if (data[i]["pois"].sequence_review == 1){
                                        var start = e.routes[0].waypointIndices[i]
                                        var end = e.routes[0].waypointIndices[i+1]
                                        var middle = (start + end) / 2
                                        var middleround = Math.round(middle)
                                        var circlemarkerinst = L.circleMarker([e.routes[0].coordinates[middleround].lat, e.routes[0].coordinates[middleround].lng]).bindPopup(L.popup({maxHeight:300}).setContent('<span style="font-weight:bold">Rout description: </span>'+
                                                                   data[i]["pois"].route_descript_pt))
                                        circlemarker.push(circlemarkerinst)
                                    }
                                }
                                cmarkerlayer = L.featureGroup(circlemarker).addTo(map)
                            });                  // Adding  data to map define in the previous
                         }else{                                   // mode driving
                            routingcontrol = L.Routing.control({
                                waypoints: coord_poi,
                                router: driving_service ,
                                draggableWaypoints: false,
                                addWaypoints: false,
                                createMarker: function(i, wp, n) {
                                    poi_info.push(data[i])
                                    var popup_img  = '<br> <img src="static/uploads/300x200.png" class="img-thumbnail" alt="" width="300" height="200"/>'
                                    if (data[i]["pois"].poi_orig_img.length > 0){
                                        popup_img = '<br> <img src="static/uploads/512px_'+ data[i]["pois"].poi_orig_img[0] +'" class="img-thumbnail" alt="" width="300" height="200"/>'
                                    }
                                    var poi_info_popup_descript_pt = []
                                    if(data[i]["pois"].poi_descript_pt.length > 120){
                                        poi_info_popup_descript_pt = data[i]["pois"].poi_descript_pt.substring(0,120) + "...";
                                    } else {
                                        poi_info_popup_descript_pt = data[i]["pois"].poi_descript_pt
                                    }
                                    return L.marker(wp.latLng, {
                                        icon: L.icon.glyph({ glyph: String.fromCharCode(65 + i) })
                                    }).bindPopup(L.popup({maxHeight:300}).setContent('<span style="font-weight:bold">Name: </span>' + data[i]["pois"].poiName+
                                                               '<br> <span style="font-weight:bold">Description: </span>'+
                                                               poi_info_popup_descript_pt +
                                                               '<br> <span style="font-weight:bold">Website: </span> <a href="'+
                                                               data[i]["pois"].poi_website +'" target="_blank">'+data[i]["pois"].poi_website +
                                                               '</a> ' + popup_img +
                                                               '<br><button type="button" class="more_info_btn" data-order="'+ 
                                                               i +'">Show More</button>'));
                                    //}
                                },
                                addWaypoints: false,
                                routeWhileDragging: false,
                                show: false,
                                lineOptions: {
                                    styles: [{color: 'black', opacity: 0.15, weight: 9}, {color: 'white', opacity: 0.8, weight: 6}, {color: 'red', opacity: 1, weight: 2}]
                                },
                                
                            }).addTo(map).on('routesfound', function(e){
                                console.log(e.routes[0].waypointIndices)
                                var circlemarker = [];
                                for (i = 0; i < e.routes[0].waypointIndices.length-1; i++ ){
                                    if (data[i]["pois"].sequence_review == 1){
                                        var start = e.routes[0].waypointIndices[i]
                                        var end = e.routes[0].waypointIndices[i+1]
                                        var middle = (start + end) / 2
                                        var middleround = Math.round(middle)
                                        var circlemarkerinst = L.circleMarker([e.routes[0].coordinates[middleround].lat, e.routes[0].coordinates[middleround].lng]).bindPopup(L.popup({maxHeight:300}).setContent('<span style="font-weight:bold">Rout description: </span>'+
                                                                   data[i]["pois"].route_descript_pt))
                                        circlemarker.push(circlemarkerinst)
                                    }
                                }
                                cmarkerlayer = L.featureGroup(circlemarker).addTo(map)
                                
                                //code to initialize and open "PoI more info" popup
                                var popup = $(".leaflet-popup-pane")

                                $('#my_popup').popup({
                                    transition: 'all 0.3s'
                                });

                                $(popup).on("click", ".more_info_btn", function (){
                                    var i = $(this).data('order')
                                    var popup_img2 = '<img src="static/uploads/300x200.png" class="img-thumbnail" alt="" width="300" height="200" style="float: left;"/>'
                                    if (poi_info[i].pois.poi_orig_img.length > 0){
                                        popup_img2 = '<img src="static/uploads/512px_'+ poi_info[i].pois.poi_orig_img[0] +'" class="img-thumbnail" style="float: left;" alt="" width="300" height="200"/>'
                                }
                                    $("#my_popup").html('<a href="#" class="my_popup_close" style="float:right;margin-top: -0.4em; padding:0 0.2em;">×</a>' + 
                                                                                                                popup_img2 +
                                                        '<span style="font-weight:bold">Name: </span>' +
                                                        poi_info[i].pois.poiName +
                                                        '<br> <span style="font-weight:bold">Description: </span>'+
                                                        poi_info[i].pois.poi_descript_pt +
                                                        '<br> <span style="font-weight:bold">ID: </span>'+
                                                        poi_info[i].pois.poiID +
                                                        '<br> <span style="font-weight:bold">Address: </span>'+ 
                                                        poi_info[i].pois.address +
                                                        '<br> <span style="font-weight:bold">Opening: </span>'+
                                                        poi_info[i].pois.poi_open_h +
                                                        '<br> <span style="font-weight:bold">Closing: </span>'+
                                                        poi_info[i].pois.poi_close_h +
                                                        '<br> <span style="font-weight:bold">Visit duration: </span>'+
                                                        poi_info[i].pois.poi_dura +
                                                        '<br> <span style="font-weight:bold">Phone n.º: </span>'+
                                                        poi_info[i].pois.poi_phone +
                                                        '<br> <span style="font-weight:bold">E-mail: </span>'+
                                                        poi_info[i].pois.poi_email +
                                                        '<br> <span style="font-weight:bold">Website: </span> <a href="'+
                                                        poi_info[i].pois.poi_website[0] +'" target="_blank">'+ poi_info[i].pois.poi_website[0] + '</a> ' 
                                                       )
                                    $('#my_popup').popup('show');
                                })
                                $(popup).on("click", ".more_route_info_btn", function (){
                                    var popup_img2 = '<img src="static/uploads/300x200.png" class="img-thumbnail" alt="" width="300" height="200" style="float: left;"/>'
                                    if (poi_info[0].pois.poi_orig_img.length > 0){
                                        popup_img2 = '<img src="static/uploads/512px_'+ poi_info[0].pois.poi_orig_img[0] +'" class="img-thumbnail" style="float: left;" alt="" width="300" height="200"/>'
                                }
                                    
                                    $("#my_popup").html('<a href="#" class="my_popup_close" style="float:right;margin-top: -0.4em; padding:0 0.2em;">×</a>' + 
                                                        '<div style="min-height:200px">'+ popup_img2 +
                                                        '<span style="font-weight:bold">Name: </span>' +
                                                        poi_info[0].pois.poiName +
                                                        '<br> <span style="font-weight:bold">Description: </span>'+
                                                        poi_info[0].pois.poi_descript_pt +
                                                        '<br> <span style="font-weight:bold">ID: </span>'+
                                                        poi_info[0].pois.poiID +
                                                        '<br> <span style="font-weight:bold">Address: </span>'+ 
                                                        poi_info[0].pois.address +
                                                        '<br> <span style="font-weight:bold">Opening: </span>'+
                                                        poi_info[0].pois.poi_open_h +
                                                        '<br> <span style="font-weight:bold">Closing: </span>'+
                                                        poi_info[0].pois.poi_close_h +
                                                        '<br> <span style="font-weight:bold">Visit duration: </span>'+
                                                        poi_info[0].pois.poi_dura +
                                                        '<br> <span style="font-weight:bold">Phone n.º: </span>'+
                                                        poi_info[0].pois.poi_phone +
                                                        '<br> <span style="font-weight:bold">E-mail: </span>'+
                                                        poi_info[0].pois.poi_email +
                                                        '<br> <span style="font-weight:bold">Website: </span> <a href="'+
                                                        poi_info[0].pois.poi_website[0] +'" target="_blank">'+ poi_info[0].pois.poi_website[0] + '</a> <br> </div> <hr>' 
                                                       )
                                    for (var j = 0; j < poi_info.length-1; j++){
                                        if (poi_info[j].pois.sequence_review == 1){
                                            var popup_img2 = '<img src="static/uploads/300x200.png" class="img-thumbnail" alt="" width="300" height="200" style="float: left;"/>'
                                            if (poi_info[j].pois.sequence_image.length > 0){
                                                popup_img2 = '<img src="static/uploads/512px_'+ poi_info[j].pois.sequence_image[0] +'" class="img-thumbnail" style="float: left;" alt="" width="300" height="200"/>'
                                            }
                                            $("#my_popup").append('<div style="min-height:200px">'+ popup_img2 +
                                                                  '<span style="font-weight:bold">From </span>' +
                                                                  poi_info[j].pois.poiName +
                                                                  '<br> <span style="font-weight:bold">To: </span>'+
                                                                  poi_info[j+1].pois.poiName +
                                                                  '<br> <span style="font-weight:bold">Rout description: </span>'+
                                                                  poi_info[j].pois.route_descript_pt +
                                                                  '<br> </div> <hr>'
                                                                 )
                                        }
                                        var popup_img2 = '<img src="static/uploads/300x200.png" class="img-thumbnail" alt="" width="300" height="200" style="float: left;"/>'
                                        if (poi_info[j+1].pois.poi_orig_img.length > 0){
                                            popup_img2 = '<img src="static/uploads/512px_'+ poi_info[j+1].pois.poi_orig_img[0] +'" class="img-thumbnail" style="float: left;" alt="" width="300" height="200"/>'
                                }
                                    
                                        $("#my_popup").append('<div style="min-height:200px">'+ popup_img2 +
                                                        '<span style="font-weight:bold">Name: </span>' +
                                                        poi_info[j+1].pois.poiName +
                                                        '<br> <span style="font-weight:bold">Description: </span>'+
                                                        poi_info[j+1].pois.poi_descript_pt +
                                                        '<br> <span style="font-weight:bold">ID: </span>'+
                                                        poi_info[j+1].pois.poiID +
                                                        '<br> <span style="font-weight:bold">Address: </span>'+ 
                                                        poi_info[j+1].pois.address +
                                                        '<br> <span style="font-weight:bold">Opening: </span>'+
                                                        poi_info[j+1].pois.poi_open_h +
                                                        '<br> <span style="font-weight:bold">Closing: </span>'+
                                                        poi_info[j+1].pois.poi_close_h +
                                                        '<br> <span style="font-weight:bold">Visit duration: </span>'+
                                                        poi_info[j+1].pois.poi_dura +
                                                        '<br> <span style="font-weight:bold">Phone n.º: </span>'+
                                                        poi_info[j+1].pois.poi_phone +
                                                        '<br> <span style="font-weight:bold">E-mail: </span>'+
                                                        poi_info[j+1].pois.poi_email +
                                                        '<br> <span style="font-weight:bold">Website: </span> <a href="'+
                                                        poi_info[j+1].pois.poi_website[0] +'" target="_blank">'+ poi_info[j+1].pois.poi_website[0] + '</a> <br> </div> <hr>') 
                                    }
                                    $('#my_popup').popup('show');
                                })
                            })

                        }
                        firstcheck = 1
                    })
            })
            marker_array.push(marker)
            
        }
    }
markers.addLayers(marker_array);

map.addLayer(markers);

new L.Routing.Itinerary({
    pointMarkerStyle:{radius: 5,color: '#03b20b',fillColor: 'white',opacity: 1,fillOpacity: 0.7},
    summaryTemplate: '<b><h2>{name}</h2><h3>{distance}, {time}</h3></b>',
    show: false
});

map.on("layeradd", function (e) {
    cmarkerlayer.bringToFront()
})

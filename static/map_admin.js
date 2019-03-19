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
        zoom: 10, //9,
        //preferCanvas: true,
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

var markers = L.markerClusterGroup({/*disableClusteringAtZoom: 14*/
                                      maxClusterRadius: function (zoom) {
                                          return (zoom < 14) ? 7 : 1; // radius in pixels (40 : 1)
                                      }
                                  });
var marker_array = [];

    if (poi_info != null){
        for (var i = 0; i < poi_info.length; i++){
            var popup_img  = '<br> <img src="/static/uploads/300x200.png" class="img-thumbnail" alt="" width="300" height="200"/>'
            if (poi_info[i].poi_orig_img.length > 0){
                popup_img = '<br> <img src="/static/uploads/512px_'+ poi_info[i].poi_orig_img[0] +'" class="img-thumbnail" alt="" width="300" height="200"/>'
            }
            //shortens string to 120 characters to show in the marker pop-up
            var poi_info_popup_descript_pt = []
			if (poi_info[i].poi_descript_pt == null){
				poi_info_popup_descript_pt = "...";
			} else {	
				if(poi_info[i].poi_descript_pt.length > 120){
					poi_info_popup_descript_pt = poi_info[i].poi_descript_pt.substring(0,120) + "...";
				} else {
					poi_info_popup_descript_pt = poi_info[i].poi_descript_pt
				} 
			}
			
			if (poi_info[i].poi_review == 1) {
				var new_icon = new LIcon({className: 'cat'+ poi_info[i].category_id + " " + poi_info[i].poi_id + " conc" + poi_info[i].concelho_id+" ", iconUrl: '/static/icons/icon_green.png'})
			} else {
				var new_icon = new LIcon({className: 'cat'+ poi_info[i].category_id + " " + poi_info[i].poi_id + " conc" + poi_info[i].concelho_id+" ", iconUrl: '/static/icons/icon_red.png'})
			}
			marker = new L.marker([poi_info[i].poi_lat, poi_info[i].poi_lon], {icon: new_icon})
                .bindPopup(L.popup({maxHeight:300}).setContent('<span style="font-weight:bold">Nome: </span>' +
                                                               poi_info[i].poi_name +
                                                               '<br> <span style="font-weight:bold">Descrição: </span>'+
                                                               poi_info_popup_descript_pt +
                                                               '<br> <span style="font-weight:bold">Website: </span> <a href="'+
                                                               poi_info[i].poi_website +'" target="_blank">'+ poi_info[i].poi_website +
                                                               '</a> ' + popup_img +
                                                               '<br><button type="button" class="more_info_btn" data-order="'+ 
                                                               i +'">Mostrar Mais Informação</button>&nbsp'+
															   '<a href="/admin/pois/edit-pois/'+poi_info[i].poi_id+'" target="_blank"><button type="button" class="edit_poi">Edit</button></a>'));
            marker_array.push(marker)
            autocomplete_data.push({label: poi_info[i].poi_name, value: poi_info[i].poi_id, lat: poi_info[i].poi_lat, lon: poi_info[i].poi_lon})
        }
    }
markers.addLayers(marker_array);

map.addLayer(markers);

var radcatlist = $(".cat_list")
var radconclist = $(".conc_list")

var category_rating = [];  //this list keeps track of the status of each category, defaults to 1 (valid)
var concelho_rating = [];  //this list keeps track of the status of each concelho, defaults to 1 (valid)
for (var i = 0; i < $(radcatlist).find("input").length; i++){
    category_rating.push(1)
}
for (var i = 0; i < $(radconclist).find("input").length; i++){
    concelho_rating.push(1)
}

$(".main_checkbox").click(function(){
    if ($(this).children("input").is(":checked")){
        $(radcatlist).find("input[value^='1']").prop("checked",true)
        for (var i=0; i < category_rating.length; i++){
            category_rating[i] = 1
        }
        for (i = 0; i < marker_array.length; i++ ){
            for (var j=0; j < concelho_rating.length; j++){
                if (concelho_rating[j] == 1){
                    g=j+1
                    if (marker_array[i].options.icon.options.className.includes("conc"+g+" ")){
                        markers.addLayer(marker_array[i])
                    }
                }
            }
        }
    }else{
        $(radcatlist).find("input[value^='1']").prop("checked",false)
        markers.clearLayers()
        for (var i=0; i < category_rating.length; i++){
            category_rating[i] = 0
        }
    }
});
$(".cat_list input[type='checkbox']").click(function(){
    var cat = this.name
    var cat_num = this.name.replace("cat","")
    $("input[name='typeRoute_radio']").prop("checked",false);
    if ($(this).is(":checked")){
        category_rating[cat_num-1] = 1
        for (i = 0; i < marker_array.length; i++ ){
            if (marker_array[i].options.icon.options.className.includes(cat+" ")){
                for (var j=0; j < concelho_rating.length; j++){
                    if (concelho_rating[j] == 1){
                        g=j+1
                        if (marker_array[i].options.icon.options.className.includes("conc"+g+" ")){
                            markers.addLayer(marker_array[i])
                        }
                    }
                }
            }
        }
    }else{
        category_rating[cat_num-1] = 0
        for (i = 0; i < marker_array.length; i++ ){
            if (marker_array[i].options.icon.options.className.includes(cat+" ")){
                markers.removeLayer(marker_array[i])
            }
        }
    }
    if ($(radcatlist).find("input:checked").length == $(radcatlist).find("input").length){
        $("input[name='typeRoute_radio']").prop("checked",true);
    }
});

$(".main_concbox").click(function(){
    if ($(this).children("input").is(":checked")){
        $(radconclist).find("input[value^='1']").prop("checked",true)
        for (var i=0; i < concelho_rating.length; i++){
            concelho_rating[i] = 1
        }
        for (i = 0; i < marker_array.length; i++ ){
            for (var j=0; j < category_rating.length; j++){
                if (category_rating[j] == 1){
                    g=j+1
                    if (marker_array[i].options.icon.options.className.includes("cat"+g+" ")){
                        markers.addLayer(marker_array[i])
                    }
                }
            }
        }
    }else{
        $(radconclist).find("input[value^='1']").prop("checked",false)
        markers.clearLayers()
        for (var i=0; i < concelho_rating.length; i++){
            concelho_rating[i] = 0
        }
    }
});

$(".conc_list input[type='checkbox']").click(function(){
    var conc = this.name
    var conc_num = this.name.replace("conc","")
    $("input[name='typeRoute_radio2']").prop("checked",false);
    if ($(this).is(":checked")){
        concelho_rating[conc_num-1] = 1
        for (i = 0; i < marker_array.length; i++ ){
            if (marker_array[i].options.icon.options.className.includes(conc+" ")){
                for (var j=0; j < category_rating.length; j++){
                    if (category_rating[j] == 1){
                        g=j+1
                        if (marker_array[i].options.icon.options.className.includes("cat"+g+" ")){
                            markers.addLayer(marker_array[i])
                        }
                    }
                }
            }
        }
    }else{
        concelho_rating[conc_num-1] = 0
        for (i = 0; i < marker_array.length; i++ ){
            if (marker_array[i].options.icon.options.className.includes(conc+" ")){
                markers.removeLayer(marker_array[i])
            }
        }
    }
    if ($(radconclist).find("input:checked").length == $(radconclist).find("input").length){
        $("input[name='typeRoute_radio2']").prop("checked",true);
    }
});

//code to initialize and open "PoI more info" popup
var popup = $(".leaflet-popup-pane")

$('#my_popup').popup({
    transition: 'all 0.3s'
});

$(popup).on("click", ".more_info_btn", function (){
    var i = $(this).data('order')
    var popup_img2 = '<img src="/static/uploads/300x200.png" class="img-thumbnail" alt="" width="300" height="200" style="float: left;"/>'
    if (poi_info[i].poi_orig_img.length > 0){
        //popup_img2 = '<img src="static/uploads/512px_'+ poi_info[i].poi_orig_img[0] +'" class="img-thumbnail" style="float: left;" alt="" width="300" height="200"/>'
        popup_img2 = '<div style="float:left; padding-right:5px;">' +
            '<div id="carousel-example-generic" class="carousel slide" style="float:left; width:300px; height:200px;" data-ride="carousel">' +
                '<!-- Indicators ------------------------------------------------------------------------>' +
                '<ol class="carousel-indicators">' +
                '</ol>' +

                '<!-- Wrapper for slides ---------------------------------------------------------------->' +
                '<div class="carousel-inner">' +
                    '<!-- Slides  here -->' +
                '</div>' +

                '<!-- Controls -------------------------------------------------------------------------->' +
                '<a class="left carousel-control" href="#carousel-example-generic" data-slide="prev">' +
                    '<span class="icon-prev"></span>' +
                '</a>' +
                '<a class="right carousel-control" href="#carousel-example-generic" data-slide="next">' +
                    '<span class="icon-next"></span>' +
                '</a>' +
            '</div>' +
            '</div>'
    }
    $("#my_popup").html('<a href="#" class="my_popup_close" style="float:right;margin-top: -0.4em; padding:0 0.2em;">×</a>' +
        popup_img2 +
        '<span style="font-weight:bold">Nome: </span>' +
        poi_info[i].poi_name +
        '<br> <span style="font-weight:bold">Descrição: </span>'+
        poi_info[i].poi_descript_pt +
        '<br> <span style="font-weight:bold">ID: </span>'+
        poi_info[i].poi_id +
        '<br> <span style="font-weight:bold">Morada: </span>'+ 
        poi_info[i].address +
        '<br> <span style="font-weight:bold">Abertura: </span>'+
        poi_info[i].poi_open_h +
        '<br> <span style="font-weight:bold">Encerramento: </span>'+
        poi_info[i].poi_close_h +
        '<br> <span style="font-weight:bold">Duração da visita: </span>'+
        poi_info[i].poi_dura +
        '<br> <span style="font-weight:bold">Nº de Telefone: </span>'+
        poi_info[i].poi_phone +
        '<br> <span style="font-weight:bold">Endereço E-mail: </span>'+
        poi_info[i].poi_email +
        '<br> <span style="font-weight:bold">Website: </span> <a href="'+
        poi_info[i].poi_website +'" target="_blank">'+ poi_info[i].poi_website + '</a> ' 
        )
    if (poi_info[i].poi_orig_img.length > 0){

        $(document).ready(function(){
            for (j = 0; j < poi_info[i].poi_orig_img.length; j++ )
            {
                $('<div class="item"><img class="img-responsive center-block" src="/static/uploads/512px_'+ poi_info[i].poi_orig_img[j] +'" class="img-thumbnail" alt="" style="width:300px; height:200px;"><div class="carousel-caption"></div></div>').appendTo('.carousel-inner');
                if (j < 5)
                {
                    $('<li data-target="#carousel-example-generic" data-slide-to="'+j+'"></li>').appendTo('.carousel-indicators')
                }

            }
            $('.item').first().addClass('active');
            $('.carousel-indicators > li').first().addClass('active');
            $('#carousel-example-generic').carousel({
                interval: 5000 //changes the speed
            });

        });
    }
    $('#my_popup').popup('show');
})

//auto-complete code
var marker_array_length = marker_array.length
$("input[name^='start_pois_label']").keypress(function () {
   curr_mar_len=markers.getLayers()
   if (curr_mar_len.length!=marker_array_length){
       console.log("Check!")
       markers.clearLayers()
       for (i = 0; i < marker_array.length; i++ ){
           for (var j=0; j < category_rating.length; j++){
               if (category_rating[j] == 1){
                   g=j+1
                   if (marker_array[i].options.icon.options.className.includes("cat"+g+" ")){
                       for (var jj=0; jj < concelho_rating.length; jj++){
                           if (concelho_rating[jj] == 1){
                               gg=jj+1
                               if (marker_array[i].options.icon.options.className.includes("conc"+gg+" ")){
                                   markers.addLayer(marker_array[i])
                               }
                           }
                       }
                   }
               }
           }
       }
       marker_array_length=curr_mar_len.length
   }

    $("input[name^='start_pois_label']").autocomplete({
            source: autocomplete_data,
            minLength: 5,
            delay: 0,

            focus: function (event, ui) {
                event.preventDefault(); // prevent autocomplete from updating the textbox
                $(this).val(ui.item.label);
            },

            select: function (event, ui) {
                event.preventDefault(); // prevent autocomplete from updating the textbox
                $(this).val(ui.item.label);

                markers.clearLayers()
                for (i = 0; i < marker_array.length; i++ ){
                    if(marker_array[i].options.icon.options.className.includes(" " + ui.item.value + " ")){
                        markers.addLayer(marker_array[i])
                    }
                }
                map.panTo(new L.LatLng(ui.item.lat, ui.item.lon));
            }
        });
    });

$("#search_button").click(function () {
    var val = $("input[name^='start_pois_label']").val();
    markers.clearLayers()
    for (i = 0; i < marker_array.length; i++ ){
        if ($.trim(marker_array[i]._popup._content.split("<br>")[0].toLowerCase()).includes($.trim(val.toLowerCase()))){
            markers.addLayer(marker_array[i])
        }
    }
})


$(".caixa_poi").addClass("well2")

$(".caixa_mapa").addClass("well2")
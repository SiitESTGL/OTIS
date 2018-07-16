/**
 * Created by Jesus on 05-04-2017.
 */
var map;
map = L.map('mymap',
        {
        center: [lan, lon],
        zoom: 10
        });
        L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png',{
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        // add my marker
        L.marker([lan, lon]).addTo(map)
    .bindPopup(poiName)
    .openPopup();


// Check radio button, display blind (english or Portuguis)
$("input[name='descript']").click(function () {
    if ($(this).val() === '1') {
        $('#read_description_pt').css('display', 'block');
        $('#read_description_en').css('display', 'none');
    }
    else {
        $('#read_description_pt').css('display', 'none');
        $('#read_description_en').css('display', 'block');
    }
});
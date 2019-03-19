/**
 * Created by Jesus on 30-11-2016.
 */


// Script creates dynamic fields for POIs open and close hours

var max_fields = 15; // maximum input fields allowed
var wrapper = $(".time_create_field"); // fields wrapper
var add_button = $(".addNewField_btn"); // reference button ID
var count_field = 1; // initial text box count

// Function add New poi open, duration and close fields
$(add_button).click(function (e)
{
    e.preventDefault();

    if (count_field < max_fields) {
        count_field++; // text box increment
        $(wrapper).append('<div class="form-group">' +
            '<label for="name" class="col-md-2 control-label"></label>'+
            '<div class="col-md-2">' +
            '<input type="text" class="form-control open_time_poi_add" id="time_poi_open" name="poi_open[]" placeholder="open Hour">' +
            '</div><div class="col-md-2">' +
            '<input type="text" class="form-control close_time_poi" id="time_poi_close" name="poi_close[]"  placeholder="close Hour">' +
            '</div><a href="#" id="time_poi_remove" <button type="button"  class="remove_field btn-primary">Remove</button></a>' +
            '</div>');
    }


    // --------------------------------------------------------------------------------------------------------------------
    //Compute Duration of open time poi and close time poi
    // --------------------------------------------------------------------------------------------------------------------
    //  // customize timepicker poi open
    $('.open_time_poi').timepicker({
        'timeFormat': 'H:i',
        'step': 30
    });
	
	$('.open_time_poi_add').timepicker({
        'timeFormat': 'H:i',
		'maxTime': '23:59',
		'minTime': $('#poi_close').val(),
        'step': 30
    });

    // temporarily disable the close time of poi
    $('.close_time_poi').prop('disabled', true);

    // when a open time is chosen
    $('.open_time_poi_add').on('changeTime', function () {
        // enable the end time input
        $('.close_time_poi').prop('disabled', false);

        // enable the input as a timepicker
        $('.close_time_poi').timepicker({
            timeFormat: 'H:i',
			maxTime: '23:59',
            minTime: $(this).val(),
            showDuration: true,
            step: 30
        });
    });

});

// Remove  poi (open, duration and close) fields, when click on delete remove button
$(wrapper).on("click", ".remove_field", function (e) { // user click on remove text
    e.preventDefault();
    $(this).parent('div').remove();
    count_field--;
})

//Enable or disables de open/close inputs
$('#poistate_radio_fut_1').click(function()
{
  $('#poi_open').removeAttr("disabled");
  $('#poi_close').removeAttr("disabled");
  $('#button_addnew').removeAttr("disabled");
  $('#time_poi_open').removeAttr("disabled");
  $('#time_poi_close').removeAttr("disabled");
  document.getElementById("time_poi_remove").disabled = false;
  
  $('#poi_open').on('changeTime', function () {
    // enable the end time input
    $('#poi_close').prop('disabled', false);

    // enable the input as a timepicker
    $('#poi_close').timepicker({
        timeFormat: 'H:i',
		maxTime: '23:59',
        minTime: $(this).val(),
        showDuration: true,
        step: 30
    });
});
  
});

$('#poistate_radio_fut_0').click(function()
{
  $('#poi_open').attr("disabled","disabled");
  $('#poi_close').attr("disabled","disabled");
  $('#button_addnew').attr("disabled","disabled");
  $('#time_poi_open').attr("disabled","disabled");
  $('#time_poi_close').attr("disabled","disabled");
  document.getElementById("time_poi_remove").disabled = true;
});

// Script creates dynamic images fields
var max_image_field = 15;
var wrapper_image = $(".new_img_field");
var add_img_field_btn = $(".addNewimgField_btn");
var count_img_field = 1;

// Function add New Image fields
$(add_img_field_btn).click(function (e)
{
    e.preventDefault();

    if (count_img_field < max_image_field) {
        count_img_field++; // text box increment
        $(wrapper_image).append('<div class="form-group">'+
                        '<label for="name" class="col-md-2 control-label"></label>'+
                        '<div class="col-md-4">'+
                            '<input type="file" class="file-upload"  name="imagefile[]">'+
                        '</div>'+
                        '<a href="#<button type="button" class="removebtn_img_field btn-primary">Remove</button></a>'+
                    '</div>');
    }
});

// Remove  dynamic fields, when click on delete remove button
$(wrapper_image).on("click", ".removebtn_img_field", function (e) { // user click on remove text
    e.preventDefault();
    $(this).parent('div').remove();
    count_img_field--;
})


// ---------------------------------------------------------------------------------------------------------------------
//Default fields,  Compute Duration of open time poi and close time poi
// ---------------------------------------------------------------------------------------------------------------------

// for open time of  POI
$('#poi_open').timepicker({
    'timeFormat': 'H:i',
    'step': 30
});

// temporarily disable the close time of poi
$("#poi_close").prop('disabled', true);

// when a open time is chosen
$('#poi_open').on('changeTime', function () {
    // enable the end time input
    $('#poi_close').prop('disabled', false);

    // enable the input as a timepicker
    $('#poi_close').timepicker({
        timeFormat: 'H:i',
		maxTime: '23:59',
        minTime: $(this).val(),
        showDuration: true,
        step: 30
    });
});

//-----------------------------------------------------------------------------------------------------------------+
var responDista;
$.validator.addMethod
(
    "checkPoiByDistances",
    function (value, element)
    {
        $.ajax({
            url: $("#addPOI").attr("action"),
            data: "poi_long="+ value,
            type: "POST",
            dataType: "html",
            success: function (data){
                poi_distance = this.data;
            }
        });
        return responDista;
    },
    "Poi Already  existed"
);


// validate phone number
$.validator.addMethod('customphone', function (value, element) {
    return this.optional(element) || /^(\+351-|\+351|0)?\d{9}$/.test(value);
}, "Please enter a valid phone number");


// Validate Image Size
$.validator.addMethod // AddMethod(Function_name, function, message)
(
    "minImageSize",
    function( value, element, minSize){
        var result = $(element).data('imageSize')
        return ((result[0] || 0 ) > minSize[0] && (result[1] || 0 ) > minSize[1]);
    },
    function(minSize, element){
        var imagesize = $(element).data('imageSize');
        return (imagesize)
            ? ("Image Size must be greater than " + imagesize[0] + "x" +  imagesize[1] +  " pixels")
            : "Selected file is not  an image.";
    }
);


// Validate POI Time
$.validator.addMethod(
    "poitime",
    function (value, element) {
         return this.optional(element) || /^(([0-1]?[0-9])|([2][0-3])):([0-5]?[0-9])(:([0-5]?[0-9]))?$/i.test(value);
    },
    "Please enter a valid time!");


// ----------------------------------------------------------------------------------------------------------------+
$("#addPOI").validate(
{
    debug:true,
    onkeyup: false, //turn off auto validate whilst typing
    errorClass: "my-error-class",
    validClass: "my-valid-class",
    rules:
    {
        poi_name:
        {
            required: true,
            minlength: 5,
            "remote":
            {
                url: '/admin/pois/check-poiname',
                type: "POST",
                data:
                {
                    poi_name: function ()
                    {
                        return $('#poi_name').val();
                    }
                }
            }

        },
        poi_address:
        {
            required: true
        },
        poi_phone:
        {
            customphone:true
        },
        poi_email:
        {
          email:true
        },
        poi_website:
        {
          url:true
        },
		lat_decimal:
        {
            required:true,
            number: true,
            range: [40, 42] // Degree > 40 and < 42

        },
		long_decimal:
        {
            required:true,
            number: true,
            range: [-9,-6] // Degree > -9 and < -6
        },
		
        poi_descri_pt_short:
        {
            required: true,
            minlength: 10
        },
        
        poi_descri_pt_long:
        {
            required: true,
            minlength: 10
        },

        poi_descri_en_short:
        {
            required: true,
            minlength: 10
        },

        poi_descri_en_long:
        {
            required: true,
            minlength: 10
        },

        select_categ:
        {
            required: true
        },
        select_conc:
        {
            required: true
        },
        select_score:
        {
            required: true
        },
        'poi_open[]':
        {
            required: true,
            poitime:true
        },
        'poi_close[]':
        {
            required: true,
            poitime: true
        },
        visitduration:
        {
            required: true,
            poitime:true
        }
    },

    messages:
    {
        poi_name:
        {
            required: "*",
            minlength: "Poi name must consist of at 5 characters",
            remote: $.validator.format("{0} is already existed.")
        },
        poi_address:
        {
          required: "*"
        },
        poi_phone:
        {
            required:"*"

        },
        poi_email:
        {
          email: "Please enter a valid email address"
        },
        poi_website:
        {
          url:"Please enter a valid url (http://www.test.com)"
        },

        lat_decimal:{
            required:"*",
            number: "please, enter the coordinates with six decimal places",
            range: "please, the value must between 40 and  42"

        },

        long_decimal:{
            required:"*",
            number: "please, enter the coordinates with six decimal places",
            range: "please, the value must between -9 and -6"

        },

        poi_descri_pt_short:{
            required: "*",
            minlength: "POI description must consist of at 10 characters"
        },
        
        poi_descri_pt_long:{
            required: "*",
            minlength: "POI description must consist of at 10 characters"
        },

        poi_descri_en_short:{
            required: "*",
            minlength: "POI description must consist of at 10 characters"
        },
        
        poi_descri_en_long:{
            required: "*",
            minlength: "POI description must consist of at 10 characters"
        },

        select_categ:{
            required: "*"
        },
        'poi_open[]':
        {
            required: "*"
        },

        'poi_close[]':{
            required: "*"
        },
         visitduration:
        {
            required: "*"
        }

    },

    submitHandler: function (form)
    {
        form.submit();
        form.reset()
    }
});



    var $submitBtn = $("#addPOI").find('button:submit');
    var $imageFile = $('#imgfile');
    var $imgContainer = $('#imageContainer');


    var validator_image = $("#addPOI").validate(
            {
                rules:
                {
                    'img_file[]':
                    {
                        required: true,
                        minImageSize: [842, 402]
                    }
                },
                messages:
                {
                     'img_file[]':
                    {
                        required: "tengke upload imagem ida!"
                    }
                }
            });

        // function get Image Size
        $($imageFile).change(function()
        {
              $imageFile.removeData('imageSize');
              $imgContainer.hide().empty();

              var file = this.files[0];

              if (file.type.match(/image\/.*/))
              {
                $submitBtn.attr('disabled', true);

                var reader = new FileReader();

                reader.onload = function()
                {
                  var $img = $('<img />').attr({ src: reader.result });

                  $img.on('load', function()
                  {
                    $imgContainer.append($img).show();
                    var imageWidth = $img.width();
                    var imageHeight = $img.height();
                    var imageSize = [imageWidth, imageHeight];
                    $imageFile.data('imageSize', imageSize);
                    if ((imageSize[0] <= 842) || (imageSize[1] <= 402) )
                        {
                          $imgContainer.hide();
                        }
                    else
                        {
                          $img.css({ width: '80px', height: '40px' });
                        }
                    $submitBtn.attr('disabled', false);

                    validator_image.element($imageFile);
                  });
                };
                reader.readAsDataURL(file);
              }
              else
              {
                validator_image.element($imageFile);
              }
        });

// End Form validation---------------------------------------------------------------------------------------------+
/**
 * Created by Jesus on 07-03-2017.
 */


var max_fields = 20; // maximum input fields allowed
var add_button = $(".addNewField_btn"); // reference button ID
var wrapper = $(".route_edit_wrap"); // fields wrapper
var find_field = $(wrapper).find("input[name^='start_pois_label']:last").data('field'); // initial text box count
var count_field = parseInt(find_field) || 1;


// ===================================================================================================================
// When click on this button, it will add a new fields
// -------------------------------------------------------------------------------------------------------------------

$(add_button).click(function (e) {
    e.preventDefault();

    if (count_field < max_fields) {
        count_field++; // text box increment
        $(wrapper).append('<div>' +
            '</br><input type="text" class="form-control"  name="start_pois_label" placeholder="value be equal to the previus field " data-field="'+ count_field + '"/>' +
            '<input type="hidden" class="form-control"  name="start_pois_value[]" data-field="'+ count_field + '"/>' +
            '<label class="my-error-class" name="start_pois_label-error2" data-field="'+ count_field +'" style="display: none;">please, enter start poi name</label>' +
            '<textarea class="form-control" placeholder="Description between these points(Language1)" rows="4" id="input_routeDescript" name="input_descriptwopois_pt[]" datatype="text"></textarea>'+
            '<textarea class="form-control" placeholder="Description between these points(Language2)" rows="4" id="input_routeDescript" name="input_descriptwopois_en[]" datatype="text"></textarea>'+
            '<input type="text" class="form-control"  name="end_pois_label" placeholder="End Poi" data-field="'+ count_field + '"/></br>' +
            '<input type="hidden" class="form-control"  name="end_pois_value[]" data-field="'+ count_field + '"/>' +
            '<label class="my-error-class" name="end_pois_label-error2" data-field="'+ count_field +'" style="display: none;">please, enter start poi name</label>' +
            '<label for="name" class="control-label">Is Sequence Valid?:</label>'+
                '<input id="radio" type="radio"  name="sequence_review_radio'+ count_field +'" value="1" checked="true">Yes' +
                '<input id="radio" type="radio"  name="sequence_review_radio'+ count_field +'" value="0">No' +
                '<br>' +
            '<a href="#" <button type="button" class="remove_field btn-primary" data-field="'+ count_field + '">Remove</button></a></div>');
        

        // ==============================================================================
        // Autocomplete for new start pois fields
        // ------------------------------------------------------------------------------
        $(wrapper).find("input[name^='start_pois_label']").keyup(function () {
            var val = $(this).val();
            var field = $(this).data('field');
            $(wrapper).find("input[name^='start_pois_value'][data-field=" + field +"]").val("");
            $.ajax({
                method: "POST",
                url: '/admin/route/autocomplete',
                cache: false,
                data: {key: val}
            }).done(function (data) {
                //console.log(data)
               for (i = 0; i < data.length; i++ ){
                   if ($.trim(data[i].label.toLowerCase()) == $.trim(val.toLowerCase())){
                       $(wrapper).find("input[name^='start_pois_value'][data-field=" + field +"]").val(data[i].value);
                       $(wrapper).find("label[name^='start_pois_label-error2'][data-field=" + field +"]").text("POI Confirmed")
                       $(wrapper).find("label[name^='start_pois_label-error2'][data-field=" + field +"]").attr("style", "display: inline-block;")
                       $(wrapper).find("label[name^='start_pois_label-error2'][data-field=" + field +"]").attr("class", "my-valid-class")
                        }
                   else{
                       $(wrapper).find("label[name^='start_pois_label-error2'][data-field=" + field +"]").text("POI Not found or does not exist, submitting will create blank POI with this name")
                       $(wrapper).find("label[name^='start_pois_label-error2'][data-field=" + field +"]").attr("style", "display: inline-block;")
                       $(wrapper).find("label[name^='start_pois_label-error2'][data-field=" + field +"]").attr("class", "my-error-class")
                       }
                   }
                $(wrapper).find("input[name^='start_pois_label']").autocomplete({
                    source: data,
                    minLength: 2,

                    focus: function (event, ui) {
                        event.preventDefault(); // prevent autocomplete from updating the textbox
                        $(this).val(ui.item.label);
                    },

                    select: function (event, ui) {
                        event.preventDefault(); // prevent autocomplete from updating the textbox
                        $(this).val(ui.item.label);
                        $(wrapper).find("input[name^='start_pois_value'][data-field=" + field +"]").val(ui.item.value);
                        $(wrapper).find("label[name^='start_pois_label-error2'][data-field=" + field +"]").text("POI Confirmed")
                        $(wrapper).find("label[name^='start_pois_label-error2'][data-field=" + field +"]").attr("style", "display: inline-block;")
                        $(wrapper).find("label[name^='start_pois_label-error2'][data-field=" + field +"]").attr("class", "my-valid-class")
                    }
                });
            });
        });

        // ===================================================================================
        // Autocomplete for a new end pois fields
        // -----------------------------------------------------------------------------------
        $(wrapper).find("input[name^='end_pois_label']").keyup(function () {
            var val = $(this).val();
            var field = $(this).data('field');
            $(wrapper).find("input[name^='end_pois_value'][data-field=" + field +"]").val("");
            $.ajax({
                method: "POST",
                url: '/admin/route/autocomplete',
                cache: false,
                data: {key: val}
            }).done(function (data) {
                for (i = 0; i < data.length; i++ ){
                   if ($.trim(data[i].label.toLowerCase()) == $.trim(val.toLowerCase())){
                       $(wrapper).find("input[name^='end_pois_value'][data-field=" + field +"]").val(data[i].value);
                       $(wrapper).find("label[name^='end_pois_label-error2'][data-field=" + field +"]").text("POI Confirmed")
                       $(wrapper).find("label[name^='end_pois_label-error2'][data-field=" + field +"]").attr("style", "display: inline-block;")
                       $(wrapper).find("label[name^='end_pois_label-error2'][data-field=" + field +"]").attr("class", "my-valid-class")
                        }
                   else{
                       $(wrapper).find("label[name^='end_pois_label-error2'][data-field=" + field +"]").text("POI Not found or does not exist, submitting will create blank POI with this name")
                       $(wrapper).find("label[name^='end_pois_label-error2'][data-field=" + field +"]").attr("style", "display: inline-block;")
                       $(wrapper).find("label[name^='end_pois_label-error2'][data-field=" + field +"]").attr("class", "my-error-class")
                       }
                   }
                $(wrapper).find("input[name^='end_pois_label']").autocomplete({
                    source: data,
                    minLength: 2,

                    focus: function (event, ui) {
                        event.preventDefault(); // prevent autocomplete from updating the textbox
                        $(this).val(ui.item.label);
                    },

                    select: function (event, ui) {
                        event.preventDefault(); // prevent autocomplete from updating the textbox
                        $(this).val(ui.item.label);
                        $(wrapper).find("input[name^='end_pois_value'][data-field=" + field +"]").val(ui.item.value);
                        $(wrapper).find("input[name^='end_pois_value'][data-field=" + field +"]").val(ui.item.value);
                        $(wrapper).find("label[name^='end_pois_label-error2'][data-field=" + field +"]").text("POI Confirmed")
                        $(wrapper).find("label[name^='end_pois_label-error2'][data-field=" + field +"]").attr("style", "display: inline-block;")
                        $(wrapper).find("label[name^='end_pois_label-error2'][data-field=" + field +"]").attr("class", "my-valid-class")
                    }
                });
            });
        });

    }
});

// ===============================================================================
// Remove  fields, when clicked on remove button
// -------------------------------------------------------------------------------

$(wrapper).on("click", ".remove_field", function (e) { // user click on remove text
    e.preventDefault();
    
    //timer to prevent rapid removal of fields that can send the system out of sync
    var btn = $(".remove_field");
    btn.prop('disabled',true);
    window.setTimeout(function(){ 
        btn.prop('disabled',false);
    },1000);
    
    
    var counter = $(this).data('field');
    for (i = counter; i <= count_field; i++) {
        $(wrapper).find("input[name^='sequence_review_radio"+i+"']").each(function() {
            j = i-1
            $(this).attr("name", "sequence_review_radio"+String(j))
        });
    }
    $(wrapper).find("input[name^='start_pois_label']").each(function() {
        var value = $(this).data('field');
        if (value > counter){
            $(wrapper).find("[data-field=" + value +"]").attr("data-field", value-1)
        }
    });
    
    $(this).parent('div').remove();
    count_field--;
});

// Show hide fields, if route is a circle

$("input[name='typeRoute_radio']").click(function(){
    if (route_circle == true){
        $(wrapper.find('div.route_field:last')).css('display',($(this).val() === '0') ? 'none':'block');
    }
    else{
         $("#hide-me").css('display', ($(this).val() === '1') ? 'block':'none');
    }


});

$("input[name='typeRoute_radio2']").click(function(){
    if (route_circle == false){
        $(wrapper.find('div.route_field:last')).css('display',($(this).val() === '1') ? 'block':'none');
    }
    else{
         $("#hide-me2").css('display', ($(this).val() === '0') ? 'none':'block');
    }


});


// =================================================================================
// Autocomplete default fields of Start POI
// ---------------------------------------------------------------------------------
$("input[name^='start_pois_label']").keyup(function () {
    var val = $(this).val();
    var field = $(this).data('field');
    $("input[name^='start_pois_value[]'][data-field=" + field +"]").val("");
    $.ajax({
        method: "POST",
        url: '/admin/route/autocomplete',
        cache: false,
        data: {key: val}
    }).done(function (data) {
        for (i = 0; i < data.length; i++ ){
            if ($.trim(data[i].label.toLowerCase()) == $.trim(val.toLowerCase())){
                $("input[name^='start_pois_value'][data-field=" + field +"]").val(data[i].value);
                $("label[name^='start_pois_label-error2'][data-field=" + field +"]").text("POI Confirmed")
                $("label[name^='start_pois_label-error2'][data-field=" + field +"]").attr("style", "display: inline-block;")
                $("label[name^='start_pois_label-error2'][data-field=" + field +"]").attr("class", "my-valid-class")
                        }
            else{
                $("label[name^='start_pois_label-error2'][data-field=" + field +"]").text("POI Not found or does not exist, submitting will create blank POI with this name")
                $("label[name^='start_pois_label-error2'][data-field=" + field +"]").attr("style", "display: inline-block;")
                $("label[name^='start_pois_label-error2'][data-field=" + field +"]").attr("class", "my-error-class")
                       }
                   }
        $("input[name^='start_pois_label']").autocomplete({
            source: data,
            minLength: 2,

            focus: function (event, ui) {
                event.preventDefault(); // prevent autocomplete from updating the textbox
                $(this).val(ui.item.label);
            },

            select: function (event, ui) {
                event.preventDefault(); // prevent autocomplete from updating the textbox
                $(this).val(ui.item.label);
                $("input[name^='start_pois_value[]'][data-field=" + field +"]").val(ui.item.value);
                $("label[name^='start_pois_label-error2'][data-field=" + field +"]").text("POI Confirmed")
                $("label[name^='start_pois_label-error2'][data-field=" + field +"]").attr("style", "display: inline-block;")
                $("label[name^='start_pois_label-error2'][data-field=" + field +"]").attr("class", "my-valid-class")
            }
        });
    });
});

// =======================================================================================
// Autocomplete for default field of end poi
// --------------------------------------------------------------------------------------
$("input[name^='end_pois_label']").keyup(function () {
    var val = $(this).val();
    var field = $(this).data('field');
    $("input[name^='end_pois_value[]'][data-field=" + field +"]").val("");
    $.ajax({
        method: "POST",
        url: '/admin/route/autocomplete',
        cache: false,
        data: {key: val}
    }).done(function (data) {
        for (i = 0; i < data.length; i++ ){
            if ($.trim(data[i].label.toLowerCase()) == $.trim(val.toLowerCase())){
                $("input[name^='end_pois_value'][data-field=" + field +"]").val(data[i].value);
                $("label[name^='end_pois_label-error2'][data-field=" + field +"]").text("POI Confirmed")
                $("label[name^='end_pois_label-error2'][data-field=" + field +"]").attr("style", "display: inline-block;")
                $("label[name^='end_pois_label-error2'][data-field=" + field +"]").attr("class", "my-valid-class")
                        }
            else{
                $("label[name^='end_pois_label-error2'][data-field=" + field +"]").text("POI Not found or does not exist, submitting will create blank POI with this name")
                $("label[name^='end_pois_label-error2'][data-field=" + field +"]").attr("style", "display: inline-block;")
                $("label[name^='end_pois_label-error2'][data-field=" + field +"]").attr("class", "my-error-class")
                       }
                   }
        $("input[name^='end_pois_label']").autocomplete({
            source: data,
            minLength: 2,

            focus: function (event, ui) {
                event.preventDefault(); // prevent autocomplete from updating the textbox
                $(this).val(ui.item.label);
            },

            select: function (event, ui) {
                event.preventDefault(); // prevent autocomplete from updating the textbox
                $(this).val(ui.item.label);
                $("input[name^='end_pois_value[]'][data-field=" + field +"]").val(ui.item.value);
                $("label[name^='end_pois_label-error2'][data-field=" + field +"]").text("POI Confirmed")
                $("label[name^='end_pois_label-error2'][data-field=" + field +"]").attr("style", "display: inline-block;")
                $("label[name^='end_pois_label-error2'][data-field=" + field +"]").attr("class", "my-valid-class")
            }
        });
    });
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
                            '<input type="file" class="file-upload"  name="route_image[]">'+
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

// ========================================================================================
// Form Route Validation
// ---------------------------------------------------------------------------------------
$("#addRoute").validate(
    {
        onkeyup: false, //turn off auto validate whilst typing
        rules: {
            
                input_routename:
                {
                    required: true,
                    "remote": {
                        url: '/admin/route/check-routename-edit',
                        type: 'POST',
                        data: {
                            input_routename: function () {
                                return $("#input_routename").val();
                            },
                            route_id: function () {
                                return $("#route_id").val();
                            }
                        }  
                    }
                
            },
            mode_travel: {
                required: true
            },
            input_routes_label: {
                required: true
            },
            input_routes_label2: {
                required: true
            },
            input_routeDescript: {
                required: true
            }
        },

        messages: {
            input_routename:
            {
                required: "This field required.",
                remote: "Route name already exists."
            },
            mode_travel: {
                required: "Please, select an option."
            },
            input_routes_label: {
                required: "This field required."
            },
            input_routes_label2: {
                required: "This field required."
            },
            input_routeDescript: {
                required: "Please, add desciption."
            }
        },

        submitHandler: function (form) {
            form.submit();
        }
    });

    
    var $submitBtn = $("#addRoute").find('button:submit');
    var $imageFile = $('#route_image');
    var $imgContainer = $('#imageContainer');


    var validator_image = $("#addRoute").validate(
            {
                rules:
                {
                    'route_image[]':
                    {
                        required: true,
                        minImageSize: [842, 402]
                    }
                },
                messages:
                {
                     'route_image[]':
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

(function ($) {
    'use strict';
    /*==================================================================
        [ Daterangepicker ]*/
    try {
        $('.js-datepicker').daterangepicker({
            "singleDatePicker": true,
            "showDropdowns": true,
            "autoUpdateInput": false,
            locale: {
                format: 'MM/DD/YYYY'
            },
        });
    
        var myCalendar = $('.js-datepicker');
        var isClick = 0;
    
        $(window).on('click',function(){
            isClick = 0;
        });
    
        $(myCalendar).on('apply.daterangepicker',function(ev, picker){
            isClick = 0;
            $(this).val(picker.startDate.format('MM/DD/YYYY'));
    
        });
    
        $('.js-btn-calendar').on('click',function(e){
            e.stopPropagation();
    
            if(isClick === 1) isClick = 0;
            else if(isClick === 0) isClick = 1;
    
            if (isClick === 1) {
                myCalendar.focus();
            }
        });
    
        $(myCalendar).on('click',function(e){
            e.stopPropagation();
            isClick = 1;
        });
    
        $('.daterangepicker').on('click',function(e){
            e.stopPropagation();
        });
    
    
    } catch(er) {console.log(er);}
    /*[ Select 2 Config ]
        ===========================================================*/
    
    try {
        var selectSimple = $('.js-select-simple');
    
        selectSimple.each(function () {
            var that = $(this);
            var selectBox = that.find('select');
            var selectDropdown = that.find('.select-dropdown');
            selectBox.select2({
                dropdownParent: selectDropdown
            });
        });
    
    } catch (err) {
        console.log(err);
    }

    /*
        Conditional formatting
    */
    $("#output-file").change(function() {
        var val = $(this).val();
        if (val === "Excel (recommended)") {
            $("#checkbox").prop( "checked", true );
            $("#recommended").show();
            $("#book-name").show();
        }
        else if (val === "CSV") {
            $("#checkbox").prop( "checked", false );
            $("#recommended").hide();
            $("#book-name").hide();
        }
    });

    /*
        Validation (used https://www.sitepoint.com/basic-jquery-form-validation-tutorial/ as reference)
    */
   
    // Extra event triggers for validation
    $('select[name="frequency"]').change(function() {
        $('select[name="frequency"]').valid();
    });

    $('#output-file').change(function() {
        $('#output-file').valid();
    });

    $(document.body).click( function() {
        if ($('input[name ="end_date"]')[0].value) {
            $('input[name ="end_date"]').valid();
        }
    });

    // Custom validators
    $.validator.addMethod("dateFormat", 
    function(value, element) {
        return value.match(/^\d{2}\/\d{2}\/\d{4}$/);
    },
    "Please enter a date in the format MM/DD/YYYY.");

    $.validator.addMethod("withinDateLimit",
    function(value, element) {
        try {
            if (!$('input[name ="start_date"]')[0].value) {
                return true;
            }
            var MONTH = 0;
            var DAY = 1;
            var YEAR = 2;
            var start_date_parts = $('input[name ="start_date"]')[0].value.split('/');
            var end_date_parts = value.split('/');
            var start_date = new Date(start_date_parts[YEAR], start_date_parts[MONTH]-1, start_date_parts[DAY]);
            var end_date = new Date(end_date_parts[YEAR], end_date_parts[MONTH]-1, end_date_parts[DAY]);
            return (new Date(end_date-start_date).getUTCFullYear() - 1970) < 3;
        } catch (err) {
            return true;
        }
    },
    "Please enter an end date that is within 3 years of the start date.");

    // Validation rules
    $("form[name='plan_form']").validate({
        rules: {
            start_date: {
                required: true,
                dateFormat: true
            },
            end_date: {
                required: true,
                dateFormat: true,
                withinDateLimit: true
            },
            start_page: {
                required: true,
                digits: true
            },
            end_page: {
                required: true,
                digits: true
            },
            frequency: {
                required: true
            },
            output_file_type: {
                required: true
            }
        },
        errorPlacement: function(error, element) { // Referenced https://stackoverflow.com/a/26500000
            var special_placement = $(element).data('error');
            if (special_placement) {
                $(special_placement).append(error)
            } else {
                error.insertAfter(element);
            }
        },
        submitHandler: function(form) {
            form.submit();
        }
    });
})(jQuery);
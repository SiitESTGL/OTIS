/**
 * Created by Jesus on 02-02-2017.
 */

$("#userForm").validate(
    {
        onkeyup: false, //turn off auto validate whilst typing
        errorClass: "my-error-class",
        validClass: "my-valid-class",
        rules:
        {
            user_name:
            {
                required: true,
                minlength: 4,
                "remote":
                {
                    url:'/admin/user/check-unique-user',
                    type: "POST",
                    data:
                    {
                        user_name: function () {
                            return $("#user_name").val();
                        }
                    }

                }
            },
            user_password:
            {
                required: true,
                minlength: 5
            },
            user_email:
            {
                required:true,
                email: true,
                "remote":
                {
                    url: '/admin/user/unique-email',
                    type: "POST",
                    data:
                    {
                        user_email: function () {
                            return $("#user_email").val();
                        }
                    }
                }
            }
        },

        messages:
        {
            user_name:
            {
                required: "this field required.",
                minlength: " user name must consist of at 4 characters",
                remote: $.validator.format("{0} is already taken.")
            },
            user_password:
            {
                required: "this field required.",
                minlength: " password must consist of at 5 characters",
            },
            user_email:
            {
                required: "provides your email, please!.",
                email: "your email is not correct.",
                remote: $.validator.format("{0} is already taken.")
            }
        },
        submitHandler: function () {
        form.submit();
    }

    });
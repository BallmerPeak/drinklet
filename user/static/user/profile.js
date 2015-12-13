/**
 * Created by Bradley on 11/21/2015.
 */

// Wait until the DOM is ready
$(document).ready(function() {
    var pwd1, pwd2, pwd3, passwordModalContent, replaceHtml;

    function getParameterByName(name) {
        name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
        var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
            results = regex.exec(location.search);
        return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
    }

    if (getParameterByName("password_change")) {
        $('#chgPwSuccess').show().find('li').append(" Password Successfully Changed.");
    }

    /**
     * @class UserProfile
     * Namespace for the functions that handle user profile
     */
    (function UserProfile() {
        var noClear = true,
            clearButton = null;
        /**
         * @method init
         * First things that happen when DOM is loaded
         */
        function init() {
            // Initialize the Chosen.io Selectors
            var config = {
                '.chosen-select'           : {},
                '.chosen-select-deselect'  : {allow_single_deselect:true},
                '.chosen-select-no-single' : {disable_search_threshold:10},
                '.chosen-select-no-results': {no_results_text:'Oops, nothing found!'},
                '.chosen-select-width'     : {width:"95%"}
            };
            for (var selector in config) {
                if(config.hasOwnProperty(selector)) {
                    $(selector).chosen(config[selector]);
                }
            }

            // Add clear button if it isn't already there
            $("#ingredientList").chosen().change(function() {
                if($("#ingredientList").val().length) {
                    if(noClear) {
                        noClear = false;
                        // Create button for clearing ingredients list
                        clearButton = $("<div />",{'class': 'col s1'})
                            .append("<br>")
                            .append($('<a />',{'id': 'clearIngredients', 'class': 'btn-floating btn-small blue'})
                                .append($('<i />',{'class': 'large material-icons'})
                                    .append('delete')
                            )
                        );
                        /**
                         * @event clearButton.click
                         * Clear the list of ingredients and remove self
                         */
                        clearButton.click(clearIngredients);
                        $("#ingredientListContainer").toggleClass("s12 s10");
                        $("#ingredientListContainer").toggleClass("m4 m3");
                        $("#ingredientListContainer").after(clearButton);
                    }
                }

            });
        }


        /**
         * @method getSelectedIngredients
         * Handle setting the value of a hidden field to list of ingredient ids
         */
        function getSelectedIngredients() {
            $("#add_ingredients").val($("#ingredientList").val());
        }

        /**
         * @method clearIngredients
         * Handle setting the value of the ingredients field to empty array
         */
        function clearIngredients() {
            // Clear the ingredients list
            $("#ingredientList").val([]);
            $("#ingredientList").trigger("chosen:updated");

            // Remove the clear button
            this.remove();
            $("#ingredientListContainer").toggleClass("s10 s12");
            $("#ingredientListContainer").toggleClass("m3 m4");
            noClear = true;
        }

        $('#pantry_form').submit(function() {
            var ingredients = [];
            var deleted = [];

            $('.ingredient-input:not(.deleted)').each(function() {
                var self = $(this);
                var ingredient_id = self.data("id"),
                    ingredient_name = self.data("name"),
                    ingredient_quantity = self.find("#" + ingredient_id + "_quantity").val();
                ingredients.push({ "id": ingredient_id, "name": ingredient_name, "quantity": ingredient_quantity});
            });

            $('.deleted').each(function() {
                var self = $(this);
                var ingredient_id = self.data("id");
                deleted.push({ "id": ingredient_id});
            });

            $('#deleted_ingredients').val(JSON.stringify(deleted));
            $('#ingredient_objects').val(JSON.stringify(ingredients));
            return true;
        });

        $('#pantry-wrapper').on('click', '.delete-button', function(){
            var row = $(this).parents('.ingredient-input');
            row.addClass('deleted');
            row.hide();
        });

        /**
         * @event #addIngredientsButton.click
         * Grab the list of ingredients from ingredientList
         */
        $("#addIngredientsButton").click(getSelectedIngredients);

        $('#changePw').leanModal({
            ready: function() {
                $('#chg_pw_errors').hide();
                $('#oldPassword').val("").focus();
                $('#newPassword').val("");
                $('#confirmNewPassword').val("");
            },
            // Modal complete event handler
            complete: function() {
                // Remove all overlays
            }
        });

        $('#passwordModal').keypress(function (evt) {
        if(evt.which == 13) {
            $('button#confirm_button').click();
        }
    });

        $('#confirm_button').click(function() {
            pwd1 = $('#oldPassword').val();
            pwd2 = $('#newPassword').val();
            pwd3 = $('#confirmNewPassword').val();
            var jqxhr;
            jqxhr = $.post('change_password',
                {
                    'oldpwd': pwd1,
                    'newpwd': pwd2,
                    'confirmpwd': pwd3
                });

            jqxhr.done(
                function(data) {
                    var jsonData = JSON.parse(data);
                    if(jsonData.redirect)
                        window.location.href = jsonData.redirect + "?password_change=true";
                }
            ).fail(
                function(data) {
                    var errorIcon = '<i class="material-icons valign left">error_outline</i>';
                    $('#chg_pw_errors').show().find('li').html(errorIcon + data.responseText);
                    $('#oldPassword').focus().select();
                }
            );
        });

        init();
    })();


});

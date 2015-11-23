/**
 * Created by Bradley on 11/21/2015.
 */
// Wait until the DOM is ready
$(document).ready(function() {
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
                        // $("#ingredientListContainer").after("<div id='clearIngredientsContainer' class='col s1'><br><a id='clearIngredients' class='btn-floating btn-small blue'><i class='large material-icons'>delete</i></a></div>");
                    } 
                }

            });
        }

        /**
         * @method getSelectedIngredients
         * Handle setting the value of a hidden field to list of ingredient ids
         */
        function getSelectedIngredients() {
            $("#ingredients").val($("#ingredientList").val());
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

        $('.delete-button').click(function(){
            var row = $(this).parents('.ingredient-input');
            row.addClass('deleted');
            row.hide();
        });

        /**
         * @event #addIngredientsButton.click
         * Grab the list of ingredients from ingredientList
         */
        $("#addIngredientsButton").click(getSelectedIngredients);

        init();
    })();
});

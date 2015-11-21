/**
 * Created by Bradley on 11/21/2015.
 */
// Wait until the DOM is ready
$(document).ready(function() {
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
});

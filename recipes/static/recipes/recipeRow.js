/**
 * Created by Bradley on 11/22/2015.
 */
// Wait until the DOM is ready
$(document).ready(function() {
	/**
	 * @class RecipeList
	 * Namespace for the functions that handle listing recipes
	 */
	(function MakeDrink() {
        /**
         * @method toggleOrder
         * Handle toggling the order and rerunning the search
         */
        function submitRecipe(recipeid) {
            $.ajax({
                type: "POST",
                url: "makedrink",
                data: {
                    'recipe': recipeid
                }
            }).success(function(data){
                //window.alert(data);
            }).fail(function(jqXHR, textStatus){
                //window.alert(textStatus);
            });
        }

        /**
         * @event #orderNameButton.click
         * Toggle the order and rerun the search
         */
        $("a[name='make_drink_button']").click(function() {
            submitRecipe($(this).data("id"));
        });
    })();
});
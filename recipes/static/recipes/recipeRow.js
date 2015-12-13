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
        function submitRecipe(recipeid, element) {
            var jqxhr = $.ajax({
                type: "POST",
                url: "/makedrink",
                data: {
                    'recipe': recipeid
                }
            });

            jqxhr.that = element;

            return jqxhr;
        }

        /**
         * @event #orderNameButton.click
         * Toggle the order and rerun the search
         */
        $('#list-wrapper').on('click', '.recipe-card-make-drink', function() {
            var that = this;
            submitRecipe($(that).data("id"), that)
                .done(function (data, status, jqxhr) {
                    var $makeDrinkButton = $(jqxhr.that),
                        $replacementHtml = $(data),
                        numLeft, ingredients,
                        $pantry;

                    numLeft = $replacementHtml.find('#make-drink-num').html();
                    ingredients = $replacementHtml.find('#pantry-wrapper').html();
                    if (numLeft > 0) {
                        $makeDrinkButton.closest('.row').find('.num-left').html('Drinks left = ' + numLeft);
                    } else {
                        $makeDrinkButton.closest('.row').remove();
                    }
                    $pantry = $('#pantry-wrapper');

                    if($pantry.length) {
                        $pantry.html(ingredients);
                        $pantry.find('label').addClass('active');
                    }
                })
        });
    })();
});

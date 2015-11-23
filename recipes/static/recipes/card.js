// wait until DOM is ready
$(document).ready(function() {

	/**
	* @class RecipeCard
	* Namespace for the functions that handle Recipe Card behavior
	*/
	(function RecipeCard() {

		// html for filled in star
		var html_rating_star = '<i class="material-icons orange-text">star</i>';
		// html for empty star
		var html_rating_star_border = '<i class="material-icons orange-text">star_border</i>';
		// maximum amount of stars
		var maxStars = 5;

		/**
		 * @method toggleFavoriteIcon
		 * Toggles between filled in heart and empty heart on hover
		 */
		function toggleFavoriteIcon() {
			if($(this).html().trim() == 'favorite'){
				$(this).html('favorite_border');
			} else {
				$(this).html('favorite');
			}
		}

		/**
		 * @method toggleFavorite
		 * Sends POST to server to favorite/unfavorite the recipe
		 */
		function toggleFavorite() {
			// if it's currently unfavorited and becoming favorited
			if($(this).html().trim() == 'favorite'){
				$(this).html('favorite_border');							
				$.post('/favorite/', {
					recipe_id: $(this).data('recipeid'),
					is_favorite: false
				});

			// if it's currently favorited and becoming unfavorited
			} else {
				$(this).html('favorite');
				$.post('/favorite/', {
					recipe_id: $(this).data('recipeid'),
					is_favorite: true
				});
			}
		}

		/**
		 * @method displayRatings
		 * Displays amount of empty stars/filled in stars based on
		 *  sum of ratings and number of ratings
		 */
		function displayRatings() {
			$('.recipe-card-rating').each( function(index, element) {
				var ratingSum = parseInt($(element).data('rating-sum'));
				var numRatings = parseInt($(element).data('num-ratings'));

				var rating = 0;
				if(numRatings > 0 && ratingSum > 0)
					rating = Math.round(ratingSum/numRatings);

				if (rating < 0)
					rating = 0;

				if (rating > maxStars)
					rating = maxStars;

				for(var i = 0; i < maxStars; i++) {
					if(i < rating) {
						$(element).append(html_rating_star);
					}
					else {
						$(element).append(html_rating_star_border);
					}
				}	
			});
		}

		/**
		 * @method setRatings
		 * Sets the onclick listeners for all stars to POST to server
		 *  if the user rates the drink
		 */
		function setRatings() {
			$('.recipe-card-rating').each(function(index, element) {
				var recipeId = parseInt($(element).data('recipeid'));

				$(element).children().each(function(index, celement) {
					$(celement).click(function() {

						$.post('/rate/', {
							recipe_id: recipeId,
							rating: (index+1)
						});

					});
				});

			});
		}

		//sets the hover event when favorite heart is hovered
		$('.recipe-card-favorite>i').hover(toggleFavoriteIcon, toggleFavoriteIcon);
		//sets the onclick event to POST to server when a user favorites/unfavorites
		$('.recipe-card-favorite>i').click(toggleFavorite);
		// display the appropriate amount and type of stars for rating
		displayRatings();
		//set the onclick events to POST to server when a user rates
		setRatings();
	})();

});
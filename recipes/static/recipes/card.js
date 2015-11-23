$(document).ready(function() {

	(function RecipeCard() {

		function toggleFavoriteIcon() {
			if($(this).html() == 'favorite'){
				$(this).html('favorite_border');
			} else {
				$(this).html('favorite');
			}
		}

		// this is backwards because hover flips them
		function toggleFavorite() {
			// if it's currently unfavorited and becoming favorited
			if($(this).html() == 'favorite'){
				$(this).html('favorite_border');				
				console.log('Favorited! ' + $(this).data('recipeid'));				
				$.post('/recipes/favorite/', {
					recipe_id: $(this).data('recipeid'),
					is_favorite: true
				}, function(json_response) {
					console.log(json_response);
				})

			// if it's currently favorited and becoming unfavorited
			} else {
				$(this).html('favorite');
				console.log('Unfavorited! ' + $(this).data('recipeid'));
				$.post('/recipes/favorite/', {
					recipe_id: $(this).data('recipeid'),
					is_favorite: false
				}, function(json_response) {
					console.log(json_response);
				})
			}
		}

		$('.recipe-card-favorite>i').hover(toggleFavoriteIcon, toggleFavoriteIcon);
		$('.recipe-card-favorite>i').click(toggleFavorite);


	})();

});
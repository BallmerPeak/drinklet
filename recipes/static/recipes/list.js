// Wait until the DOM is ready
$(document).ready(function() {
	/**
	 * @class RecipeList
	 * Namespace for the functions that handle listing recipes
	 */
	(function RecipeList() {
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
			// Update the ingredients list to contain the last searched values
			$("#ingredientList").val(JSON.parse($("#search_ingredients").val()));
			$("#ingredientList").trigger("chosen:updated");
		}

		/**
		 * @method getSelectedIngredients
		 * Handle setting the value of a hidden field to list of ingredient ids
		 */
		function getSelectedIngredients() {
			$("#search_ingredients").val($("#ingredientList").val());
		}

		/**
		 * @method toggleOrder
		 * Handle toggling the order and rerunning the search
		 */
		function toggleOrder() {
			// Toggle the value in the "order" hidden field
			$("#order").val(($("#order").val() === "asc")? "desc" : "asc");

			// Rerun the search
			$("#searchButton").click();
		}

		/**
		 * @method clearName
		 * Handle setting the value of the name field empty
		 */
		function clearName() {
			// Clear the name field
			$("#query").val("");

			// Rerun the search
			$("#searchButton").click();
		}

		/**
		 * @method clearIngredients
		 * Handle setting the value of the ingredients field to empty array
		 */
		function clearIngredients() {
			// Clear the ingredients list
			$("#ingredientList").val([]);
			$("#ingredientList").trigger("chosen:updated");

			// Rerun the search
			$("#searchButton").click();
		}

		/**
		 * @method handleNavigation
		 * Handle navigating to a new page
		 */
		function handleNavigation(_page) {
			// Make sure passed in page is a number
			if(isNaN(_page)) _page = 1;

			// Set the page value to the new page number
			$("#page").val(_page);

			// Rerun the search
			$("#searchButton").click();
		}

		/**
		 * @event #searchButton.click
		 * Grab the list of ingredients from ingredientList
		 */
		$("#searchButton").click(getSelectedIngredients);

		/**
		 * @event #orderNameButton.click
		 * Set order_by to "name", toggle the order, and rerun the search
		 */
		$("#orderNameButton").click(function() {
			$("#order_by").val("name");
			toggleOrder();
		});

		/**
		 * @event #orderRatingButton.click
		 * Set order_by to "ratings", toggle the order, and rerun the search
		 */
		$("#orderRatingButton").click(function() {
			$("#order_by").val("ratings");
			toggleOrder();
		});

		/**
		 * @event #clearName.click
		 * Clear the name query and rerun the search
		 */
		$("#clearName").click(clearName);

		/**
		 * @event #clearIngredients.click
		 * Clear the list of ingredients and rerun the search
		 */
		$("#clearIngredients").click(clearIngredients);

		/**
		 * @event #firstNumber.click
		 * Navigate to the first page.
		 */
		$(".firstNumber").click(function() {
			handleNavigation(1);
		});

		/**
		 * @event #lastNumber.click
		 * Navigate to the last page.
		 */
		$(".lastNumber").click(function() {
			handleNavigation($("#numPages").val());
		});

		/**
		 * @event #previousArrow.click
		 * Navigate to the previous page.
		 */
		$(".previousArrow").click(function() {
			handleNavigation(parseInt($("#thisPage").val())-1);
		});

		/**
		 * @event #previousNumber.click
		 * Navigate to the previous page.
		 */
		$(".previousNumber").click(function() {
			handleNavigation(parseInt($("#thisPage").val())-1);
		});

		/**
		 * @event #nextArrow.click
		 * Navigate to the next page.
		 */
		$(".nextArrow").click(function() {
			handleNavigation(parseInt($("#thisPage").val())+1);
		});

		/**
		 * @event #nextNumber.click
		 * Navigate to the next page.
		 */
		$(".nextNumber").click(function() {
			handleNavigation(parseInt($("#thisPage").val())+1);
		});

		init();
	})();
});
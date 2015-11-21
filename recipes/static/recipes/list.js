// Wait until the DOM is ready
$(document).ready(function() {
	/**
	 * @class RecipeList
	 * Namespace for the functions that handle listing recipes
	 */
	(function RecipeList() {
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
		 * @event #orderNameButton.click
		 * Toggle the order and rerun the search
		 */
		$("#orderNameButton").click(toggleOrder);
	})();
});
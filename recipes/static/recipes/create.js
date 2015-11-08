// Wait until the DOM is ready
$(document).ready(function() {

	/**
	* @class RecipeCreating
	* Namespace for the functions that handle creating recipes
	*/
	(function RecipeCreating() {

		// empty html input stubs that get appended
		var ingredientInputStub = null;
		var instructionInputStub = null;

		/**
		 * @method init
		 * Initial initialization
		 */
		function init() {
			// get the empty html stub for ingredients
			ingredientInputStub = captureInputHTML('#ingredient-input-wrapper');
			// get the empty html stub for instructions
			instructionInputStub = captureInputHTML('#instruction-input-wrapper');
			// set the initial onChange event for the ingredient select
			$('.ingredient-input').first().find('select').first().change(ingredientChange);
			// set the initial onChange event for the 
			$('.instruction-input').first().find('input').first().on('input', instructionChange);
			// set the onSubmit event for the form
			$('#create-recipe-form').submit(formSubmit);
		}

		/**
		 * @method captureInputHTML
		 * Returns the inner html for the given wrapper id
		 */
		function captureInputHTML(wrapper) {
			return $(wrapper).html();
		}

		/**
		 * @method appendInput
		 * Appends child to parent
		 */
		function appendInput(parent, child) {
			$(parent).append(child);
		}

		/**
		 * @method swapIngredientOnChange
		 * Removes the onChange event from the previous select
		 * Adds the onChange event to the current select
		 * Adds a 'required' property to the last quantity field
		 */
		function swapIngredientOnChange() {
			var last = $('.ingredient-input').last();
			last.prev().find('input').first().prop('required', true);
			last.prev().find('select').first().unbind('change');
			last.find('select').first().change(ingredientChange);
		}

		/**
		 * @method ingredientChange 
		 * Appends a new ingredient input row to the end
		 * Swaps the onChange events
		 */
		function ingredientChange() {
			appendInput('#ingredient-input-wrapper', ingredientInputStub);
			swapIngredientOnChange();
		}

		/**
		 * @method swapInstructionOnChange
		 * Removes the onChange event from the previous input box
		 * Adds the onChange event to the current input box
		 */
		function swapInstructionOnChange() {
			var last = $('.instruction-input').last();
			last.prev().find('input').first().unbind('input');
			last.find('input').first().on('input', instructionChange);
		}

		/**
		 * @method instructionChange
		 * Appends a new instruction input row to the end
		 * Swaps the onChange events
		 */
		function instructionChange() {
			appendInput('#instruction-input-wrapper', instructionInputStub);
			swapInstructionOnChange();
		}

		/**
		 * @method formSubmit
		 * Puts a map of ingredient_id:quantity into the hidden POST field
		 * Puts an array of string instructions into the hidden POST field
		 */
		function formSubmit() {
			$('#post_ingredients_id_quantity').val(getAllIngredientJSONMap());
			$('#post_instructions').val(getAllInstructionJSONArray());
			
			// little validation for now
			return true;
		}

		/**
		 * @method getAllIngredientJSONMap
		 * Agregates all input ingredients into a 'id':'quantity' map
		 */
		function getAllIngredientJSONMap() {
			// TODO
			// need to add additional validation and behavior for
			//	possible negative quantities

			var ingredientMap = {};
			$('.ingredient-input').each(function(index, element) {
				var id = parseInt($(element).find('select').first().val());
				var quantity = Math.abs(parseFloat($(element).find('input').first().val()));
				if(id && quantity)
					ingredientMap[id] = "" + quantity;
			});
			return JSON.stringify(ingredientMap);
		}

		/**
		 * @method getAllInstructionJSONArray
		 * Agregates all input instructions into an array
		 */
		function getAllInstructionJSONArray() {
			var instructionArray = [];
			$('.instruction-input').each(function(index, element) {
				var instruction = $(element).find('input').first().val();
				if(instruction)
					instructionArray.push(instruction);
			});
			return JSON.stringify(instructionArray);
		}

		init();
	})();
});
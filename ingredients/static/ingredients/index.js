// Wait until the DOM has loaded before loading the JavaScript functions
document.addEventListener('DOMContentLoaded', function() {

	/**
	 * @class IngredientSearching
	 * Namespace for the functions that handle searching by ingredients
	 */
	(function IngredientSearching() {
		// Global list of ingredient objects
		var ingredientList = [];
		var ingredients = {};

		/**
		 * @method init
		 * First things that happen when DOM is loaded
		 */
		function init() {
			// Grab the clear button
			var ingredientClear = document.getElementById('ingredientClear');

			// Add respective event handlers for clear button
			if(ingredientClear) ingredientClear.addEventListener('click', clearIngredients);

			// Grab the ingredientsJSON with ingredient objects
			getIngredientObjects();

			// Grab the ingredients list from local storage
			getLocalIngredients();
		}

		/**
		 * @method getIngredientObjects
		 * Grab the JSON string of the list of Ingredient objects
		 */
		function getIngredientObjects() {
			// Grab the ingredientsJSON hidden input's value
			ingredients = document.getElementById('ingredientsJSON');

			// Make sure ingredientsJSON exists
			if(ingredients) {
				// Grab the value of the ingredientsJSON input
				ingredients = ingredients.value;

				// Parse the ingredientsJSON into an Object if it is a String
				if(toString.call(ingredients) === '[object String]') {
					try {
						ingredients = JSON.parse(ingredients);
					} catch(_error) {
						console.error('Invalid list of ingredients.');
					}
				}

				// Iterate over the ingredientsJSON object to initialize check boxes
				if(toString.call(ingredients) === '[object Object]') {
					for(var i in ingredients) {
						if(ingredients.hasOwnProperty(i)) {
							// Grab the corresponding check box for the current ingredient
							var checkBox = document.getElementById(i+'_ingredient');

							// If the check box exists, make it call updateIngredient on click
							if(checkBox) checkBox.addEventListener('click', function(_e) {
								// Grab the 'data-id' value of the check box and call updateIngredient
								updateIngredient(_e.srcElement.dataset.id);
							});
						}
					}
				}
			}
		}

		/**
		 * @method getLocalIngredients
		 * Query the local storage for the list of ingredients
		 */
		function getLocalIngredients() {
			// Grab the ingredients list from local storage
			var localIngredients = localStorage.ingredientList;

			// Check if there was an existing list of ingredients in local storage
			if(localIngredients) {
				// Parse the local ingredients into an Array if it is a String
				if(toString.call(localIngredients) === '[object String]') {
					try {
						localIngredients = JSON.parse(localIngredients);
					} catch(_error) {
						console.error('Invalid local storage list of ingredients.');
					}
				}
				// Grab the contents of the local ingredients and update inventory
				if(toString.call(localIngredients) === '[object Array]') {
					ingredientList = localIngredients;

					// Update the DOM with the list of ingredients
					updateInventory();
				}
			}
		}

		/**
		 * @method addIngredient
		 * Add an ingredient from the ingredient list
		 * @param {Object} _data The ingredient to add
		 */
		function addIngredient(_data) {
			// Add ingredient to ingredient list
			ingredientList.push(_data);

			// Add the selected ingredients to local storage
			localStorage.setItem('ingredientList', JSON.stringify(ingredientList));
		}

		/**
		 * @method removeIngredient
		 * Remove an ingredient from the ingredient list
		 * @param {Number} _id The id of the ingredient to remove
		 */
		function removeIngredient(_id) {
			// Add ingredient to ingredient list
			ingredientList.splice(_id,1);

			// Add the selected ingredients to local storage
			localStorage.setItem('ingredientList', JSON.stringify(ingredientList));
		}

		/**
		 * @method updateIngredient
		 * Either adds or removes an ingredient from the selected ingredient list.
		 * @param {Object} _id The ingredient to update
		 */
		function updateIngredient(_id) {
			// Make sure the data passed in is a non null object
			if(_id !== undefined
			&& !isNaN(_id)) {
				// Find the index of the ingredient in the ingredient list
				var ingredientIndex = getIngredientIndex(_id);

				// If the ingredient was in the list, remove it
				if(ingredientIndex >= 0) removeIngredient(ingredientIndex);

				// Otherwise add it to the list
				else addIngredient(ingredients[_id]);

				// Update the DOM with the list of ingredients
				updateInventory();
			}
		}

		/**
		 * @method clearIngredients
		 * Unchecks all selected ingredients and clears ingredient list.
		 */
		function clearIngredients() {
			// Uncheck each currently selected ingredient's checkbox
			for(var i=0; i<ingredientList.length; i++) {
				// Grab the ingredient's checkbox
				var checkBox = document.getElementById(ingredientList[i].id+'_ingredient');
				// Uncheck the checkbox
				if(checkBox) checkBox.checked = false;
			}
			// Clear the ingredient list
			ingredientList = [];

			// Add the selected ingredients to local storage
			localStorage.setItem('ingredientList', JSON.stringify(ingredientList));

			// Update the DOM with the list of ingredients
			updateInventory();
		}

		/**
		 * @method getIngredientIDList
		 * Retrieve an array of just ingredient ids.
		 * @returns {Array} Array of ingredient ids.
		 */
		function getIngredientIDList() {
			var idList = [];
			// Build the id list according to ingredient list
			for(var i=0; i<ingredientList.length; i++) {
				// Grab the ingredient id and push into the id list
				idList.push(ingredientList[i].id);
			}
			// Return the list of ingredient ids
			return idList;
		}

		/**
		 * @method getIngredientIndex
		 * Get the index of an ingredient in the ingredient list.
		 * @param  {Number} _id The id of the ingredient to find
		 * @returns {Number} The index of the ingredient or -1 if not found.
		 */
		function getIngredientIndex(_id) {
			// Check if the id exists and is a number
			if(_id !== undefined
			&& !isNaN(_id)) {
				// Find the index of the ingredient in the ingredient list
				for(var i=0; i<ingredientList.length; i++) {
					// Return index of the first occurrence of the ingredient
					if(parseInt(ingredientList[i].id) === parseInt(_id)) return i;
				}
			}
			// Assume ingredient not found or invalid id passed in
			return -1;
		}

		/**
		 * @makeChip
		 * Create a deletable chip corresponding to an ingredient.
		 * @param   {Object}   _data     The ingredient object to make a chip of
		 * @param   {Function} _callback The click handler for when the X is clicked
		 * @returns {Element}  The chip DOM element or null if ingredient not found.
		 */
		function makeChip(_data,_callback) {
			// Check if the data exists and is an object
			if(_data !== undefined
			&& toString.call(_data) === '[object Object]') {
				// Create the DOM elements for a materialize chip
				var chip = document.createElement('div'),
					text = document.createTextNode(_data.name),
					icon = document.createElement('i'),
					type = document.createTextNode('close');
				
				// Add the classes to the DOM elements
				chip.className = 'chip';
				icon.className = 'material-icons';

				// Set up the structure of the chip
				icon.appendChild(type);
				chip.appendChild(text);
				chip.appendChild(icon);

				// Add a custom property for tracking which ingredient
				icon._id = _data.id;

				// Add the click handler for the chip
				icon.addEventListener('click', function(_e) {
					// Check if the callback exists and is a function
					if(_callback !== undefined
					&& toString.call(_callback) === '[object Function]') {
						// Call the callback, passing it the custom id property
						_callback(_e.srcElement._id);
					}
				});

				// Return the newly created chip element
				return chip;
			}
			// Assume invalid ingredient passed in
			return null;
		}

		/**
		 * @method removeChip
		 * Removes a chip and its corresponding ingredient
		 * @param {Number} _id The ingredient id
		 */
		function removeChip(_id) {
			var checkBox,
				ingredientIndex;
			if(_id !== undefined) {
				// If the ingredient id was passed in, grab its checkbox
				checkBox = document.getElementById(_id+'_ingredient');

				// Find the index of the ingredient in the ingredient list
				ingredientIndex = getIngredientIndex(_id);

				// Check if the ingredient was found and has a checkbox
				if(ingredientIndex !== undefined 
				&& checkBox) {
					// Uncheck the ingredient's checkbox
					checkBox.checked = false;

					// Remove the ingredient from the ingredient list
					removeIngredient(ingredientIndex);
				}
			}

			// Update the DOM with the list of ingredients
			updateInventory();
		}

		/**
		 * @method updateInventory
		 * Given what is in the list of ingredients, update the DOM element
		 * "inventory" with deletable chips.
		 */
		function updateInventory() {
			// Grab the inventory DOM element
			var inventory = document.getElementById('inventory'),
				buttons = document.getElementById('inventoryButtons'),
				emptyMessage = document.getElementById('inventoryEmpty'),
				idListField = document.getElementById('ingredient_ids');

			// Check if the inventory DOM element exists
			if(inventory) {
				// Clear the inventory DOM element
				inventory.innerHTML = '';

				// Create a chip for each ingredient in the ingredient list
				for(var i=0; i<ingredientList.length; i++) {
					// Call the makeChip function with the ingredient and click handler
					var chip = makeChip(ingredientList[i], removeChip);

					// Grab the checkbox for the current ingredient
					var checkBox = document.getElementById(ingredientList[i].id+'_ingredient');

					// Add the chip to the inventory DOM element
					if(chip) inventory.appendChild(chip);

					// Make sure the checkbox for the current ingredient is checked
					if(checkBox) checkBox.checked = true;
				}
				// Check if the inventoryButtons and inventoryEmpty DOM elements exist
				if(buttons
				&& emptyMessage) {
					// If there are ingredients, show the buttons and hide the empty message
					if(ingredientList.length > 0) {
						buttons.style.display = 'inline';
						emptyMessage.style.display = 'none';

					// Otherwise hide the buttons and show the empty message
					} else {
						buttons.style.display = 'none';
						emptyMessage.style.display = 'inline';
					}	
				}
			}
			// Set the list of id DOM element's value to be the list of ingredient ids
			if(idListField) idListField.value = JSON.stringify(getIngredientIDList());
		}

		// Initialize the application once all JS file is serialized
		init();
	})();
});
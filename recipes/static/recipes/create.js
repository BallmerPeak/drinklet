    // Wait until the DOM is ready
$(document).ready(function() {

    $('select').material_select();

    /**
     * @class RecipeCreating
     * Namespace for the functions that handle creating recipes
     */
    (function RecipeCreating() {

        // empty html input stubs that get appended
        var ingredientInputStub, instructionInputStub, ingrIndex,
            instIndex, ingredientName, categoryName, instructionName,
            qtyName, uomName, numIngredientInputs, numInstructionInputs,
            $ingredientInput, $instructionInput, maxIngredients, maxInstructions,
            $instructionAdd, $ingredientAdd, uomLookup;

        function ingredientRemove() {
            numIngredientInputs--;
            $(this).closest('.ingredient-input').remove();

            if ( numIngredientInputs < 2){
                $("#ingredient-input-wrapper").off();
                $('.ingredient-remove').addClass('disabled');
            }

            if ( numIngredientInputs < maxIngredients) {
                $ingredientAdd.removeClass('disabled');
                $ingredientAdd.off().click(ingredientAdd);
            }
        }

        function instructionRemove() {

            numInstructionInputs--;

            $(this).closest('.instruction-input').remove();

            if ($('.instruction-input').length < 2){
                $('.instruction-remove').addClass('disabled');
                $('#instruction-input-wrapper').off();
            }

            if (numInstructionInputs < maxInstructions) {
                $instructionAdd.removeClass('disabled');
                $instructionAdd.off().click(instructionAdd);
            }
        }

        function setUOM() {
            var $ingredient = $(this),
                ingredientName = $ingredient.val().toLowerCase(),
                uom = uomLookup[ingredientName],
                $uomInput = $ingredient.closest('.row').find('.units');

            if (uom) {
                $uomInput.val(uom)
                    .prop('disabled', false)
                    .prop('readonly', true)
                    .siblings('label')
                    .addClass('active');
            } else if(ingredientName.trim()) {
                $uomInput.prop('disabled', false)
                    .prop('readonly', false)
                    .siblings('label')
                    .addClass('active');
            } else {
                $uomInput.prop('readonly', false)
                    .prop('disabled', true)
                    .siblings('label')
                    .removeClass('active');
            }
        }

        function initializeUOM() {
            $('.units').each(function () {
                var $uom = $(this),
                    unit = $uom.val(),
                    ingredient = $uom.closest('.row').find('.ingredients').val().toLowerCase();
                if (unit && uomLookup[ingredient]){
                    $uom.prop('disabled', false)
                        .prop('readonly', true);
                }
            })
        }

        /**
         * @method init
         * Initial initialization
         */
        function init() {
            var $ingredientWrapper = $('#ingredient-input-wrapper');
            ingrIndex = $('#ingr-index').val();
            instIndex = $('#inst-index').val();
            ingredientName = $('#ingredient-name').val();
            categoryName = $('#category-name').val();
            instructionName = $('#instruction-name').val();
            qtyName = $('#qty-name').val();
            uomName = $('#uom-name').val();
            uomLookup = JSON.parse($('#uom-lookup').val());
            $ingredientInput = $('.ingredient-input');
            $instructionInput = $('.instruction-input');
            $ingredientAdd = $('#ingredient-add');
            $instructionAdd = $('#instruction-add');
            numIngredientInputs = $ingredientInput.length;
            numInstructionInputs = $instructionInput.length;
            maxIngredients = 10;
            maxInstructions = 15;

            $('#categories').change(function () {
                $('#ingredient').attr('list', $(this).val()).prop('disabled', false);
            });

            $('body').on('blur', '.ingredients', setUOM);
            initializeUOM();

            // get the empty html stub for ingredients
            ingredientInputStub = captureInputHTML('#ingredient-input-wrapper');

            ingredientInputStub = updateStub(ingredientInputStub, 'ingredient', ingredientName + ingrIndex);
            ingredientInputStub = updateStub(ingredientInputStub, 'categories', categoryName + ingrIndex);
            ingredientInputStub = updateStub(ingredientInputStub, 'ingredient_qty', qtyName + ingrIndex);
            ingredientInputStub = updateStub(ingredientInputStub, 'uom', uomName + ingrIndex);

            // get the empty html stub for instructions
            instructionInputStub = captureInputHTML('#instruction-input-wrapper');

            instructionInputStub = updateStub(instructionInputStub, 'instruction', instructionName + instIndex);
            // set the initial onChange event for the ingredient select
            if (numIngredientInputs < maxIngredients) $ingredientAdd.click(ingredientAdd);
            if (numIngredientInputs > 1)
                $ingredientWrapper.on('click', '.ingredient-remove', ingredientRemove);

            // set the initial onChange event for the
            if (numInstructionInputs < maxInstructions) $instructionAdd.click(instructionAdd);
            if (numInstructionInputs > 1)
                $('#instruction-input-wrapper').on('click', '.instruction-remove', instructionRemove);
            // set the onSubmit event for the form
            //$('#create-recipe-form').submit(formSubmit);
        }

        function updateStub(stub, id, name){
            var jStub = $(stub);
            jStub.find('#' + id)
                .attr('id', name)
                .removeAttr('name');
            jStub.find('label[for="' + id + '"]')
                .attr('for', name);

            return jStub.prop("outerHTML");
        }

        function clearInputs(wrapper) {
            var $inputWrapper = $('#recipe-form').clone().find(wrapper),
                $input = $inputWrapper.children().first();

            $input.find('input:text').attr('list', '').removeAttr('value').end()
                .find('select').children().slice(1).removeAttr('selected').end()
                .find('label').removeAttr('class');

            $input.find('input[type="number"]').removeAttr('value');

            return $input;
        }

        /**
         * @method captureInputHTML
         * Returns the inner html for the given wrapper id
         */
        function captureInputHTML(wrapper) {
            return clearInputs(wrapper).prop('outerHTML');
        }

        /**
         * @method appendInput
         * Appends child to parent
         */
        function appendInput(parent, child) {
            $(parent).append(child);
        }

        /**
         * @method ingredientAdd
         * Appends a new ingredient input row to the end
         * Swaps the onChange events
         */
        function ingredientAdd() {
            var currentIndex, futureIndex;
            appendInput('#ingredient-input-wrapper', ingredientInputStub);
            numIngredientInputs++;

            if (numIngredientInputs > 1) {
                $('#ingredient-input-wrapper').off().on('click', '.ingredient-remove', ingredientRemove);
                $('.ingredient-remove').removeClass('disabled');
            }

            if (numIngredientInputs >= maxIngredients) {
                $ingredientAdd.off().addClass('disabled');
            }

            currentIndex = ingrIndex;

            $('#' + categoryName + currentIndex).change(function () {
                $('#' + ingredientName + currentIndex).attr('list', $(this).val()).prop('disabled', false);
            });

            ingrIndex++;
            futureIndex = ingrIndex;
            initializeNames([ingredientName + currentIndex,
                categoryName + currentIndex,
                qtyName + currentIndex,
                uomName + currentIndex]);
            ingredientInputStub = updateStub(ingredientInputStub, ingredientName + currentIndex, ingredientName + futureIndex);
            ingredientInputStub = updateStub(ingredientInputStub, categoryName + currentIndex, categoryName + futureIndex);
            ingredientInputStub = updateStub(ingredientInputStub, qtyName + currentIndex, qtyName + futureIndex);
            ingredientInputStub = updateStub(ingredientInputStub, uomName + currentIndex, uomName + futureIndex);
        }

        /**
         * @method instructionAdd
         * Appends a new instruction input row to the end
         * Swaps the onChange events
         */
        function instructionAdd() {
            var currentIndex, futureIndex;
            appendInput('#instruction-input-wrapper', instructionInputStub);
            numInstructionInputs++;

            if (numInstructionInputs > 1) {
                $('#instruction-input-wrapper').off().on('click', '.instruction-remove', instructionRemove);
                $('.instruction-remove').removeClass('disabled');
            }

            if (numInstructionInputs >= maxInstructions) {
                $instructionAdd.off().addClass('disabled');
            }

            currentIndex = instIndex;
            instIndex++;
            futureIndex = instIndex;
            initializeNames([instructionName + currentIndex]);
            instructionInputStub = updateStub(instructionInputStub, instructionName + currentIndex, instructionName + futureIndex);
        }

        function initializeNames(names){
            $.each(names, function (_, name) {
                $('#' + name).attr('name', name);
            })
        }

        init();
    })();
});
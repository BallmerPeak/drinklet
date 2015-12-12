// wait until DOM is ready
$(document).ready(function() {
        function displayComments(data){
            recipename = $(this).data('recipename');


            /*Find elements */

            card = $(this).closest('.card');
            recipeelement= $(this).closest('.card').find('.card-recipe');



            /*Find comments element*/
            comment_card = card.find('.recipe-card-comment');
            /*Reveal the comments card and hide the recipe card*/


            comment_card.addClass('card-reveal');

            $.ajax({
                type: "GET",
                url: "/comment/",
                data: {
                    'recipe_name': recipename
                }
            }).success(function(data,textStatus,xhr){
                comment_card.html(data);
                //console.log();

                comment_card = card.find('.recipe-card-comment');
                comment_card.show();
                console.log(data);

            }).fail(function(jqXHR, textStatus){
                console.log(textStatus);
            });




        }


        function displayRecipe(){
            card = $(this).closest('.card').find('.card-recipe') ;

            $(this).closest('.card').find('.recipe-card-comment').removeClass('card-reveal');

        }

        function postComment(){

            card = $(this).closest('.card');
            comment_card = $(this).closest('.recipe-card-comment');
            recipename = comment_card.data('recipename');
            recipe_card= $(this).closest('.card').find('.card-recipe');

            comment_text = comment_card.find('.write-comment').val()

            comment_card.addClass('card-reveal');
            username = $(this).data('username');
            $.ajax({
                type: "POST",
                url: "/comment/",
                data: {
                    'recipe_name': recipename,
                    'comment_text':comment_text
                }
            }).success(function(data,status,xhr){
                comment_card.html(data);
                comment_card = card.find('.recipe-card-comment');
                comment_card.show();
                console.log(status);

                if (xhr.status == 207){
                    document.getElementById(username).scrollIntoView();
                }
                fademessages();
                //console.log(data);
            }).fail(function(jqXHR, textStatus){
                console.log(textStatus);
            });

        }
        function editComment(){

            card = $(this).closest('.card');
            comment_card = $(this).closest('.recipe-card-comment');
            recipename = comment_card.data('recipename');

            comment_text = comment_card.find('.write-comment').val()

            comment_card.addClass('card-reveal');


            $.ajax({
                type: "POST",
                url: "/editcomment/",
                data: {
                    'recipe_name': recipename,
                    'comment_text':comment_text
                }
            }).success(function(data){
                comment_card.html(data);
                comment_card = card.find('.recipe-card-comment');
                comment_card.show();

                fademessages();
                //console.log(data);
            }).fail(function(jqXHR, textStatus){
                console.log(textStatus);
            });

        }

        function deleteComment(){
            console.log('IN');
            card = $(this).closest('.card');
            comment_card = $(this).closest('.recipe-card-comment');
            recipename = comment_card.data('recipename');

            comment_card.addClass('card-reveal');

            $.ajax({
                type: "POST",
                url: "/deletecomment/",
                data: {
                    'recipe_name': recipename,
                }
            }).success(function(data){
                comment_card.html(data);
                comment_card = card.find('.recipe-card-comment');
                comment_card.show();
                fademessages();
                console.log(data);
            }).fail(function(jqXHR, textStatus){
                console.log(textStatus);
            });

        }


        function fademessages(){
            $('.success-message').delay(6000).fadeOut();

            $('.error-message').delay(6000).fadeOut();
        }

        /*    Events for text area           */
        $(document).on('focus','.recipe-card-comment #comment',function(){

            cardTitle = $(this).closest('.recipe-card-comment').find('span:first') ;

            cardTitle.hide();
            $('.message').hide().html('{{success-message}}');

            cardTitle.closest('.recipe-card-comment').find('.post-comment').show();

        });
        $(document).on('blur','.recipe-card-comment #comment',function(){
            cardTitle = $(this).closest('.recipe-card-comment').find('span:first') ;
            cardTitle.show();

            cardTitle.closest('.recipe-card-comment').find('.post-comment').hide();
        });
        /*   Events for post data*/
        $(document).on('click','.post-edit-comment',editComment);
        $(document).on('click','.post-comment',postComment);

        /* Events for single comment element  */
        $(document).on('click','.edit-comment', function(){

            comment_text = $(this).closest('.collection-item').find('p').html();

            comment_text_area = $(this).closest('.recipe-card-comment').find('.write-comment');
            comment_text_area.val(comment_text);
            comment_text_area.next().html("Edit...");

            comment_text_area.next().next().html("SAVE");
            comment_text_area.next().next().show();
            comment_text_area.next().next().addClass("post-edit-comment");
            comment_text_area.next().next().removeClass("post-comment");
            $('.recipe-card-comment').scrollTop(0);

        });
        $(document).on('click','.delete-comment',deleteComment);

        $('.recipe-card-comments>i').click(displayComments);
        $('.card-content').click(displayRecipe);


});
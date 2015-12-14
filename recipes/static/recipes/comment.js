var comments_init = function () {
    var postComment, editComment, deleteComment;

    function displayComments(data){
        var recipename = $(this).data('recipename'),
            card, recipeelement, comment_card;


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
            card.find('textarea.write-comment').characterCounter();

        }).fail(function(jqXHR, textStatus){
            console.log(textStatus);
        });




    }


    function displayRecipe(){
        var card = $(this).closest('.card').find('.card-recipe') ;

        $(this).closest('.card').find('.recipe-card-comment').removeClass('card-reveal');

    }

    postComment = function () {

        var card = $(this).closest('.card'),
            comment_card = $(this).closest('.recipe-card-comment'),
            recipename = comment_card.data('recipename'),
            recipe_card= $(this).closest('.card').find('.card-recipe'),
            comment_text = comment_card.find('.write-comment').val(),
            username;

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
                //document.getElementById(username).scrollIntoView();
                $(comment_card).animate({
                        scrollTop: $("#"+username).offset().top},
                    'slow');
            }
            fademessages();
            //console.log(data);
            card.find('textarea.write-comment').characterCounter();
        }).fail(function(jqXHR, textStatus){
            console.log(textStatus);
        });

    };

    editComment = function () {

        var card = $(this).closest('.card'),
            comment_card = $(this).closest('.recipe-card-comment'),
            recipename = comment_card.data('recipename'),
            comment_text = comment_card.find('.write-comment').val();

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
            card.find('textarea.write-comment').characterCounter();
        }).fail(function(jqXHR, textStatus){
            console.log(textStatus);
        });

    };

    deleteComment = function () {

        var card = $(this).closest('.card'),
            comment_card = $(this).closest('.recipe-card-comment'),
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
            card.find('textarea.write-comment').characterCounter();
        }).fail(function(jqXHR, textStatus){
            console.log(textStatus);
        });

    };


    function fademessages(){
        $('.success-message').delay(6000).fadeOut();

        $('.error-message').delay(6000).fadeOut();
    }


    $('.recipe-card-comments>i').click(displayComments);
    $('.card-content').click(displayRecipe);

    return {
        'editComment': editComment,
        'postComment': postComment,
        'deleteComment': deleteComment
    };
};


// wait until DOM is ready
$(document).ready(function() {
    var comments = comments_init(),
        $listWrapper = $('div#list-wrapper');

    /*    Events for text area           */
    $listWrapper.on('focus','.recipe-card-comment #comment',function(){

        var cardTitle = $(this).closest('.recipe-card-comment').find('span:first') ;

        cardTitle.hide();
        $('.message').hide().html('{{success-message}}');

        cardTitle.closest('.recipe-card-comment').find('.post-comment').show();

    });
    $listWrapper.on('blur','.recipe-card-comment form',function(){
        $(this).delay(400).queue(function(){
            var cardTitle = $(this).closest('.recipe-card-comment').find('span:first') ;
            cardTitle.show();

            cardTitle.closest('.recipe-card-comment').find('.post-comment').hide();
            $(this).clearQueue();
        });

    });

    /*   Events for post data*/
    $listWrapper.on('click','.post-edit-comment',comments.editComment);
    $listWrapper.on('click','.post-comment',comments.postComment);

    /* Events for single comment element  */
    $listWrapper.on('click','.edit-comment', function(){

        var comment_text = $(this).closest('.collection-item').find('p').html();

        var comment_text_area = $(this).closest('.recipe-card-comment').find('.write-comment');
        comment_text_area.val(comment_text);
        comment_text_area.next().html("Edit...");

        comment_text_area.next().next().html("SAVE");
        comment_text_area.next().next().show();
        comment_text_area.next().next().addClass("post-edit-comment");
        comment_text_area.next().next().removeClass("post-comment");
        $('.recipe-card-comment').scrollTop(0);

    });

    $listWrapper.on('click','.delete-comment',comments.deleteComment);
});
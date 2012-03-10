$(function($) {
    $(".has_info").click(function() {
        $(".hidden_info", $(this)).toggle();
    });
    
    $(".has_info").click(function() {
        return false;
    });
})
// static/js/dashboard.js
$(document).ready(function() {
    loadSection('/dashboard/employee-summary', '#employee-summary');
});

function loadSection(url, container) {
    $.get(url, function(data) {
        $(container).html(data);
    });
}
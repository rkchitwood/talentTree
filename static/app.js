async function getResults(input){
    const response = await $.ajax({
        url: '/api/companies/search',
        method: 'GET',
        data: {q : input}
    });
    return response;
}

function getHTML(results){
    if(results.length > 0){
        console.log(results)
        const html = results.map(result => {
            return `<div class="list-group-item list-group-item-info">${result}</div>`;
        });
        return html;

    }else{
        console.log('else', results)
        const html = '<div class="list-group-item list-group-item-primary">No companies found <a href="/companies/new"><button class="btn btn-primary btn-sm" id="open-company-form">Create Company</button></div>';
        $(document).on('click', '#open-company-form', function(evt){
            evt.preventDefault();
            window.open('/companies/new', '_blank');
        });
        return [html]
    }
}

function appendResults(results){
    console.log('inappend');
    var dropdown = $('<div class="list-group" id="result-container"></div>');
    for(var result of results){
        dropdown.append(result);
    }
    dropdown.css({
        position: 'absolute',
        width: $('#profile-form').outerWidth()
    });
    $('#company').after(dropdown);        
}

$(document).ready(function(){
    $('#company').on('input', async function(){
        $('#result-container').empty()
        const input = $(this).val();
        const results = await getResults(input);
        const html = getHTML(results);
        appendResults(html);
        $('#profile-button').prop('disabled', true).hide();
    })
}
)

$(document).ready(function() {
    $(document).on('mouseenter', '.list-group-item', function(){
        $(this).removeClass('list-group-item-info').addClass('list-group-item-primary');
    });
    $(document).on('mouseleave', '.list-group-item', function(){
        $(this).removeClass('list-group-item-primary').addClass('list-group-item-info');
    });
    $(document).on('click', '.list-group-item', function(){
        if(!$(this).text().includes("No companies found")){
            $('#company').val($(this).text());
            $('#profile-button').prop('disabled', false).show();
        }        
        $('#result-container').empty();        
    });
});
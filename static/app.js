async function getResults(input){
    //queries api to fetch result company domains
    const response = await $.ajax({
        url: '/api/companies/search',
        method: 'GET',
        data: {q : input}
    });
    return response;
}

function getHTML(results){
    //returns html for results or button to add a company
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
    //appends html for results to DOM
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
    //attaches event listener to profile form company field
    $('#profile-form #company').on('input', async function(){
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
    //attaches event listeners to profile form result options
    $('#profile-form').on('mouseenter', '.list-group-item', function(){
        $(this).removeClass('list-group-item-info').addClass('list-group-item-primary');
    });
    $('#profile-form').on('mouseleave', '.list-group-item', function(){
        $(this).removeClass('list-group-item-primary').addClass('list-group-item-info');
    });
    $('#profile-form').on('click', '.list-group-item', function(){
        if(!$(this).text().includes("No companies found")){
            $('#company').val($(this).text());
            $('#profile-button').prop('disabled', false).show();
        }        
        $('#result-container').empty();        
    });
});

$(document).ready(function() {
    //initiates select2 on map form companies
    $('#companiesSelect').select2();
});
